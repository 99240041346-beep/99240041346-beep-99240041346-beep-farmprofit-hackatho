import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "farmprofit-dev-secret-change-me")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

raw_db_url = os.environ.get("DATABASE_URL", "").strip()
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url or (
    "sqlite:///" + os.path.join(INSTANCE_DIR, "farmprofit.db")
)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "error"


# Global AgriWise language support
SITE_LANGUAGES = ["English", "తెలుగు", "தமிழ்", "हिन्दी", "ಕನ್ನಡ", "മലയാളം"]
SITE_TEXT = {
    "English": {"dashboard":"Dashboard","weather":"Weather & Alerts","soil":"Soil & Irrigation","equipment":"Equipment Rental","rentals":"My Rentals","assistant":"Agri AI Chatbot","profit":"Profit Predictor","whatif":"What-if Simulator","compare":"Compare Crops","history":"History","reports":"Reports","logout":"Logout","language":"Language"},
    "తెలుగు": {"dashboard":"డాష్‌బోర్డ్","weather":"వాతావరణం & హెచ్చరికలు","soil":"నేల & నీటిపారుదల","equipment":"పరికరాల అద్దె","rentals":"నా అద్దెలు","assistant":"అగ్రి AI చాట్‌బాట్","profit":"లాభ అంచనా","whatif":"ఏమైతే సిమ్యులేటర్","compare":"పంటల పోలిక","history":"చరిత్ర","reports":"రిపోర్టులు","logout":"లాగ్ అవుట్","language":"భాష"},
    "தமிழ்": {"dashboard":"டாஷ்போர்டு","weather":"வானிலை & எச்சரிக்கைகள்","soil":"மண் & பாசனம்","equipment":"விவசாய கருவி வாடகை","rentals":"என் வாடகைகள்","assistant":"அக்ரி AI சாட்பாட்","profit":"லாப கணிப்பு","whatif":"என்ன ஆகும் சிமுலேட்டர்","compare":"பயிர் ஒப்பீடு","history":"வரலாறு","reports":"அறிக்கைகள்","logout":"வெளியேறு","language":"மொழி"},
    "हिन्दी": {"dashboard":"डैशबोर्ड","weather":"मौसम और अलर्ट","soil":"मिट्टी और सिंचाई","equipment":"कृषि उपकरण किराया","rentals":"मेरी बुकिंग","assistant":"एग्री AI चैटबॉट","profit":"लाभ अनुमान","whatif":"व्हाट-इफ सिम्युलेटर","compare":"फसल तुलना","history":"इतिहास","reports":"रिपोर्ट","logout":"लॉग आउट","language":"भाषा"},
    "ಕನ್ನಡ": {"dashboard":"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್","weather":"ಹವಾಮಾನ & ಎಚ್ಚರಿಕೆಗಳು","soil":"ಮಣ್ಣು & ನೀರಾವರಿ","equipment":"ಕೃಷಿ ಉಪಕರಣ ಬಾಡಿಗೆ","rentals":"ನನ್ನ ಬಾಡಿಗೆಗಳು","assistant":"ಅಗ್ರಿ AI ಚಾಟ್‌ಬಾಟ್","profit":"ಲಾಭ ಅಂದಾಜು","whatif":"ವಾಟ್-ಇಫ್ ಸಿಮ್ಯುಲೇಟರ್","compare":"ಬೆಳೆ ಹೋಲಿಕೆ","history":"ಇತಿಹಾಸ","reports":"ವರದಿಗಳು","logout":"ಲಾಗ್ ಔಟ್","language":"ಭಾಷೆ"},
    "മലയാളം": {"dashboard":"ഡാഷ്ബോർഡ്","weather":"കാലാവസ്ഥ & മുന്നറിയിപ്പുകൾ","soil":"മണ്ണ് & ജലസേചനം","equipment":"കാർഷിക ഉപകരണ വാടക","rentals":"എന്റെ വാടകകൾ","assistant":"അഗ്രി AI ചാറ്റ്ബോട്ട്","profit":"ലാഭ പ്രവചനം","whatif":"വാട്ട്-ഇഫ് സിമുലേറ്റർ","compare":"വിള താരതമ്യം","history":"ചരിത്രം","reports":"റിപ്പോർട്ടുകൾ","logout":"ലോഗ് ഔട്ട്","language":"ഭാഷ"}
}

@app.context_processor
def inject_site_language():
    language = session.get("site_language", "English")
    if language not in SITE_LANGUAGES:
        language = "English"
    return {"site_language": language, "site_languages": SITE_LANGUAGES, "site_text": SITE_TEXT[language]}

@app.post("/set-language")
@login_required
def set_language():
    language = request.form.get("language", "English")
    if language in SITE_LANGUAGES:
        session["site_language"] = language
        session["agri_language"] = language
    response = make_response(redirect(request.form.get("next") or url_for("dashboard")))
    google_codes = {"English":"en","తెలుగు":"te","தமிழ்":"ta","हिन्दी":"hi","ಕನ್ನಡ":"kn","മലയാളം":"ml"}
    code = google_codes.get(language, "en")
    response.set_cookie("googtrans", f"/en/{code}", max_age=31536000, samesite="Lax")
    return response


# Planning profiles use common Indian farm units: yield is quintals/acre and
# market price is INR/quintal. Farmers can replace these starting estimates.
CROPS = {
    "Rice": {"yield": 22, "price": 2400},
    "Wheat": {"yield": 20, "price": 2300},
    "Maize": {"yield": 25, "price": 2100},
    "Cotton": {"yield": 8, "price": 6500},
    "Sugarcane": {"yield": 350, "price": 360},
    "Tomato": {"yield": 180, "price": 3200},
    "Potato": {"yield": 240, "price": 1800},
    "Groundnut": {"yield": 10, "price": 6200},
}

# Production costs are per acre so the model scales correctly with farm size.
COST_FIELDS = [
    ("seed", "Seed", 3000),
    ("fertilizer", "Fertilizer", 5000),
    ("pesticide", "Pesticide", 2500),
    ("labor", "Labour", 6000),
    ("machinery", "Machinery", 3000),
    ("irrigation", "Irrigation", 2000),
    ("transport", "Transport", 1800),
    ("other", "Other", 1000),
]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    plans = db.relationship("FarmPlan", backref="owner", lazy=True, cascade="all, delete-orphan")


class FarmPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    crop = db.Column(db.String(80), nullable=False)
    area = db.Column(db.Float, nullable=False)
    yield_per_acre = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seed = db.Column(db.Float, default=0, nullable=False)
    fertilizer = db.Column(db.Float, default=0, nullable=False)
    pesticide = db.Column(db.Float, default=0, nullable=False)
    labor = db.Column(db.Float, default=0, nullable=False)
    machinery = db.Column(db.Float, default=0, nullable=False)
    irrigation = db.Column(db.Float, default=0, nullable=False)
    transport = db.Column(db.Float, default=0, nullable=False)
    other = db.Column(db.Float, default=0, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    roi = db.Column(db.Float, nullable=False)
    risk = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def nfloat(value, default=0.0):
    try:
        number = float(value)
        return max(number, 0.0)
    except (TypeError, ValueError):
        return default


def calculate(data):
    area = nfloat(data.get("area"), 5.0)
    yield_per_acre = nfloat(data.get("yield_per_acre"), 22.0)
    price = nfloat(data.get("price"), 2400.0)

    # Costs are entered per acre; production and revenue scale with land area.
    costs_per_acre = {key: nfloat(data.get(key), default) for key, _, default in COST_FIELDS}
    production = area * yield_per_acre
    revenue = production * price
    total_cost = sum(costs_per_acre.values()) * area
    profit = revenue - total_cost
    roi = (profit / total_cost * 100) if total_cost else 0.0
    margin = (profit / revenue * 100) if revenue else 0.0

    if profit < 0 or margin < 10:
        risk = "High"
    elif margin < 25:
        risk = "Medium"
    else:
        risk = "Low"

    break_even_price = total_cost / production if production else 0.0
    break_even_yield = total_cost / price / area if price and area else 0.0
    cost_per_acre = total_cost / area if area else 0.0

    return {
        "area": area,
        "yield_per_acre": yield_per_acre,
        "price": price,
        "production": production,
        "revenue": revenue,
        "total_cost": total_cost,
        "profit": profit,
        "roi": roi,
        "margin": margin,
        "risk": risk,
        "break_even_price": break_even_price,
        "break_even_yield": break_even_yield,
        "cost_per_acre": cost_per_acre,
        "revenue_per_acre": revenue / area if area else 0.0,
        **costs_per_acre,
    }


def ai_predict(data):
    """Explainable farm intelligence layer combining crop, soil, stage and weather signals."""
    crop = data.get("crop", "Rice")
    if crop not in CROPS:
        crop = "Rice"
    soil_profiles = {
        "Black Soil": {"factor": 1.02, "water": "High", "interval": "4–6 days"},
        "Sandy": {"factor": 0.94, "water": "Low", "interval": "1–2 days"},
        "Sandy Loam": {"factor": 0.98, "water": "Low–Medium", "interval": "2–3 days"},
        "Loamy": {"factor": 1.05, "water": "Medium–High", "interval": "3–4 days"},
        "Silty": {"factor": 1.01, "water": "High", "interval": "4–5 days"},
        "Clay": {"factor": 0.97, "water": "Very High", "interval": "5–7 days"},
    }
    stages = {"Establishment": 0.92, "Vegetative": 1.00, "Flowering / Fruiting": 1.08, "Grain / Bulking": 1.05, "Maturity": 0.90}
    soil = data.get("soil", "Loamy")
    if soil not in soil_profiles:
        soil = "Loamy"
    stage = data.get("stage", "Vegetative")
    if stage not in stages:
        stage = "Vegetative"

    base_yield = float(CROPS[crop]["yield"])
    base_price = float(CROPS[crop]["price"])
    area = nfloat(data.get("area"), 5.0)
    price = nfloat(data.get("price"), base_price) or base_price

    temp = nfloat(data.get("temperature"), 0.0)
    humidity = nfloat(data.get("humidity"), 0.0)
    rain = nfloat(data.get("rain"), 0.0)
    rain_probability = nfloat(data.get("rain_probability"), 0.0)

    # Start from crop/soil/stage suitability, then apply live-weather stress signals.
    factor = soil_profiles[soil]["factor"] * stages[stage]
    reasons = []
    if temp:
        if temp >= 38:
            factor *= 0.86; reasons.append("High heat can reduce crop performance.")
        elif temp >= 35:
            factor *= 0.94; reasons.append("Warm conditions may increase crop stress.")
        elif temp < 18:
            factor *= 0.93; reasons.append("Cool conditions may slow crop growth.")
        else:
            reasons.append("Temperature is within a broadly workable range.")
    if humidity >= 90 and rain > 10:
        factor *= 0.95; reasons.append("Very humid and wet conditions increase disease pressure.")
    if rain >= 50:
        factor *= 0.96; reasons.append("Heavy rainfall can increase waterlogging and field-loss risk.")
    if rain_probability >= 80:
        reasons.append("High rain probability means irrigation should be planned cautiously.")

    factor = max(0.65, min(factor, 1.12))
    predicted_yield = base_yield * factor

    calc = dict(data)
    calc["yield_per_acre"] = predicted_yield
    calc["price"] = price
    baseline = calculate(calc)

    # Water need is deliberately shown as a planning estimate, not a sensor measurement.
    water_factor = {"Black Soil":0.92,"Sandy":1.18,"Sandy Loam":1.08,"Loamy":1.00,"Silty":0.94,"Clay":0.88}[soil]
    crop_water = {"Rice":6.0,"Wheat":4.0,"Maize":5.0,"Cotton":5.0,"Sugarcane":7.0,"Tomato":4.0,"Potato":3.5,"Groundnut":4.5}[crop]
    stage_factor = {"Establishment":0.78,"Vegetative":1.00,"Flowering / Fruiting":1.16,"Grain / Bulking":1.20,"Maturity":0.76}[stage]
    mm = crop_water * water_factor * stage_factor
    if temp >= 35: mm *= 1.10
    if humidity >= 80: mm *= 0.90
    if rain >= mm * 0.8 or rain_probability >= 70:
        irrigation_action = "Delay irrigation and recheck soil moisture after the rain."
    elif rain >= mm * 0.35 or rain_probability >= 45:
        irrigation_action = "Plan irrigation after the next forecast update and inspect soil moisture."
    else:
        irrigation_action = "Irrigation may be needed; use soil moisture and field condition before watering."

    confidence = 58
    confidence += 12 if temp else 0
    confidence += 10 if humidity else 0
    confidence += 10 if rain or rain_probability else 0
    confidence += 5 if soil in soil_profiles else 0
    confidence = min(confidence, 90)

    return {
        **baseline,
        "crop": crop,
        "soil": soil,
        "stage": stage,
        "predicted_yield_per_acre": round(predicted_yield, 2),
        "yield_factor": round(factor, 3),
        "confidence": confidence,
        "water_need_mm": round(mm, 2),
        "water_need_litres_per_acre": round(mm * 4046.856),
        "water_holding": soil_profiles[soil]["water"],
        "irrigation_interval": soil_profiles[soil]["interval"],
        "irrigation_action": irrigation_action,
        "insights": reasons or ["Prediction is based on crop, soil and management assumptions."],
        "engine": "Explainable multi-factor farm prediction using crop baseline data, soil suitability, growth stage and available weather signals."
    }


def save_plan_from_result(form, result):
    crop = form.get("crop", "Rice")
    if crop not in CROPS:
        crop = "Rice"
    plan = FarmPlan(
        user_id=current_user.id,
        crop=crop,
        area=result["area"],
        yield_per_acre=result["yield_per_acre"],
        price=result["price"],
        seed=result["seed"],
        fertilizer=result["fertilizer"],
        pesticide=result["pesticide"],
        labor=result["labor"],
        machinery=result["machinery"],
        irrigation=result["irrigation"],
        transport=result["transport"],
        other=result["other"],
        revenue=result["revenue"],
        total_cost=result["total_cost"],
        profit=result["profit"],
        roi=result["roi"],
        risk=result["risk"],
    )
    db.session.add(plan)
    db.session.commit()
    return plan


@app.context_processor
def inject_globals():
    return {"crops": CROPS, "cost_fields": COST_FIELDS, "now": datetime.utcnow()}


@app.route("/")
def index():
    return redirect(url_for("dashboard")) if current_user.is_authenticated else render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(name) < 2:
            flash("Enter a valid name.", "error")
        elif "@" not in email or len(email) < 5:
            flash("Enter a valid email address.", "error")
        elif len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter(func.lower(User.email) == email).first():
            flash("That email is already registered. Please log in.", "error")
        else:
            user = User(name=name, email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash("Account created successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(func.lower(User.email) == email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            flash("Welcome back!", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    plans = FarmPlan.query.filter_by(user_id=current_user.id).order_by(FarmPlan.created_at.desc()).all()
    total_revenue = sum(p.revenue for p in plans)
    total_cost = sum(p.total_cost for p in plans)
    total_profit = sum(p.profit for p in plans)
    avg_roi = sum(p.roi for p in plans) / len(plans) if plans else 0
    return render_template(
        "dashboard.html",
        plans=plans[:5],
        total_revenue=total_revenue,
        total_cost=total_cost,
        total_profit=total_profit,
        avg_roi=avg_roi,
    )


@app.route("/simulator", methods=["GET", "POST"])
@login_required
def simulator():
    result = None
    form = {
        "crop": "Rice",
        "area": "5",
        "yield_per_acre": "22",
        "price": "2400",
        **{key: str(default) for key, _, default in COST_FIELDS},
    }

    if request.method == "POST":
        form.update(request.form.to_dict())
        crop = form.get("crop", "Rice")
        if crop in CROPS and not request.form.get("yield_per_acre"):
            form["yield_per_acre"] = str(CROPS[crop]["yield"])
        if crop in CROPS and not request.form.get("price"):
            form["price"] = str(CROPS[crop]["price"])

        result = calculate(form)

        if request.form.get("save_plan") == "1":
            save_plan_from_result(form, result)
            flash("Farm analysis saved successfully.", "success")

    return render_template("simulator.html", result=result, form=form)


@app.route("/what-if", methods=["GET", "POST"])
@login_required
def what_if():
    form = {
        "crop": "Rice",
        "area": "5",
        "yield_per_acre": str(CROPS["Rice"]["yield"]),
        "price": str(CROPS["Rice"]["price"]),
        **{key: str(default) for key, _, default in COST_FIELDS},
        "yield_change": "0",
        "price_change": "0",
        "cost_change": "0",
    }
    result = None
    baseline = None
    if request.method == "POST":
        form.update(request.form.to_dict())
        baseline = calculate(form)
        yield_change = nfloat(form.get("yield_change"), 0)
        price_change = nfloat(form.get("price_change"), 0)
        cost_change = nfloat(form.get("cost_change"), 0)
        scenario = dict(form)
        scenario["yield_per_acre"] = baseline["yield_per_acre"] * (1 + yield_change / 100)
        scenario["price"] = baseline["price"] * (1 + price_change / 100)
        for key, _, _ in COST_FIELDS:
            scenario[key] = baseline[key] * (1 + cost_change / 100)
        result = calculate(scenario)
        result["baseline_profit"] = baseline["profit"]
        result["profit_change"] = result["profit"] - baseline["profit"]
        result["profit_change_pct"] = (result["profit_change"] / baseline["profit"] * 100) if baseline["profit"] else 0
    return render_template("simulator.html", result=result, baseline=baseline, form=form, what_if_only=True)

@app.route("/compare")
@login_required
def compare():
    results = []
    for crop_name, crop in CROPS.items():
        demo = {
            "crop": crop_name,
            "area": 5,
            "yield_per_acre": crop["yield"],
            "price": crop["price"],
            "seed": 3000,
            "fertilizer": 5000,
            "pesticide": 2500,
            "labor": 6000,
            "machinery": 3000,
            "irrigation": 2000,
            "transport": 1800,
            "other": 1000,
        }
        result = calculate(demo)
        result["crop"] = crop_name
        results.append(result)
    results.sort(key=lambda item: item["profit"], reverse=True)
    return render_template("compare.html", results=results)


@app.route("/history")
@login_required
def history():
    plans = FarmPlan.query.filter_by(user_id=current_user.id).order_by(FarmPlan.created_at.desc()).all()
    return render_template("history.html", plans=plans)


@app.post("/history/<int:plan_id>/delete")
@login_required
def delete_plan(plan_id):
    plan = FarmPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    flash("Saved analysis deleted.", "success")
    return redirect(url_for("history"))


@app.route("/report")
@login_required
def report():
    plans = FarmPlan.query.filter_by(user_id=current_user.id).order_by(FarmPlan.created_at.desc()).all()
    return render_template("report.html", plans=plans)


@app.post("/api/calculate")
@login_required
def api_calculate():
    data = request.get_json(silent=True) or request.form
    return jsonify(calculate(data))


@app.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "error"
    return jsonify({"status": "ok", "application": "FarmProfit", "database": database})


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(_error):
    db.session.rollback()
    return render_template("500.html"), 500


def initialize_database():
    with app.app_context():
        db.create_all()
        if os.environ.get("ENABLE_DEMO", "1") == "1":
            demo_email = os.environ.get("DEMO_EMAIL", "demo@farmprofit.app").lower()
            demo_password = os.environ.get("DEMO_PASSWORD", "Demo@12345")
            if not User.query.filter_by(email=demo_email).first():
                demo = User(
                    name="Demo Farmer",
                    email=demo_email,
                    password_hash=generate_password_hash(demo_password),
                )
                db.session.add(demo)
                db.session.commit()


initialize_database()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
