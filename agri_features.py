import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
import urllib.parse
import urllib.request


def register_agri_features(app, db):
    class Equipment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        category = db.Column(db.String(80), nullable=False)
        owner_name = db.Column(db.String(120), nullable=False)
        location = db.Column(db.String(160), nullable=False)
        price_per_day = db.Column(db.Float, nullable=False)
        available = db.Column(db.Boolean, default=True, nullable=False)
        rating = db.Column(db.Float, default=4.5, nullable=False)
        phone = db.Column(db.String(40), default="", nullable=False)
        image = db.Column(db.String(500), default="", nullable=False)

    class RentalRequest(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
        equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
        start_date = db.Column(db.String(20), nullable=False)
        end_date = db.Column(db.String(20), nullable=False)
        status = db.Column(db.String(30), default="Pending", nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        equipment = db.relationship("Equipment")

    app.config.setdefault("AGRI_EQUIPMENT", [
        ("Mahindra 575 DI Tractor", "Tractor", "Kumar Agro Services", "Pudukkottai", 1400, 1, 4.8),
        ("Sonalika Tiger Harvester", "Harvester", "Green Field Rentals", "Pudukkottai", 3200, 1, 4.7),
        ("Kirloskar 5HP Water Pump", "Irrigation", "Sri Farm Equipments", "Pudukkottai", 650, 1, 4.6),
        ("Rotavator 6ft", "Tillage", "Vetri Machinery", "Pudukkottai", 900, 1, 4.5),
        ("Battery Crop Sprayer", "Sprayer", "AgriTech Rentals", "Pudukkottai", 450, 1, 4.4),
        ("Power Tiller", "Tiller", "FarmEase", "Pudukkottai", 850, 1, 4.6),
    ])

    def seed_equipment():
        if Equipment.query.count() == 0:
            for row in app.config["AGRI_EQUIPMENT"]:
                db.session.add(Equipment(name=row[0], category=row[1], owner_name=row[2], location=row[3], price_per_day=row[4], available=bool(row[5]), rating=row[6]))
            db.session.commit()

    @app.route("/weather")
    @login_required
    def weather():
        location = request.args.get("location", "Pudukkottai").strip() or "Pudukkottai"
        weather_data = None
        error = None
        try:
            q = urllib.parse.urlencode({"name": location, "count": 1, "language": "en", "format": "json"})
            with urllib.request.urlopen("https://geocoding-api.open-meteo.com/v1/search?" + q, timeout=8) as response:
                geo = json.load(response)
            if not geo.get("results"):
                raise ValueError("Location not found")
            place = geo["results"][0]
            q = urllib.parse.urlencode({"latitude": place["latitude"], "longitude": place["longitude"], "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m", "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code", "forecast_days": 7, "timezone": "auto"})
            with urllib.request.urlopen("https://api.open-meteo.com/v1/forecast?" + q, timeout=8) as response:
                data = json.load(response)
            weather_data = {"place": place, "current": data.get("current", {}), "daily": data.get("daily", {})}
        except Exception as exc:
            error = "Weather service is temporarily unavailable. Try again in a moment."
        return render_template("weather.html", weather=weather_data, error=error, location=location)

    SOIL_PROFILES = {
        "Sandy": {
            "holding": "Low", "factor": 1.18, "interval": "1–2 days",
            "method": "Drip or light, frequent irrigation",
            "note": "Sandy soil drains quickly, so apply smaller amounts more often."
        },
        "Sandy Loam": {
            "holding": "Low–Medium", "factor": 1.08, "interval": "2–3 days",
            "method": "Drip or sprinkler",
            "note": "Good drainage with moderate water storage; avoid long dry gaps."
        },
        "Loamy": {
            "holding": "Medium–High", "factor": 1.00, "interval": "3–4 days",
            "method": "Drip, sprinkler or furrow",
            "note": "Balanced drainage and water holding; use rainfall to extend the interval."
        },
        "Silty": {
            "holding": "High", "factor": 0.94, "interval": "4–5 days",
            "method": "Drip or controlled furrow",
            "note": "Retains water well; avoid over-irrigation and waterlogging."
        },
        "Clay": {
            "holding": "Very High", "factor": 0.88, "interval": "5–7 days",
            "method": "Drip or slow furrow",
            "note": "High water holding; irrigate slowly and allow the soil to drain."
        },
    }

    CROP_WATER_MM = {
        "Rice": 6.0, "Wheat": 4.0, "Maize": 5.0, "Cotton": 5.0,
        "Sugarcane": 7.0, "Tomato": 4.0, "Potato": 3.5, "Groundnut": 4.5
    }

    def fetch_weather_for_place(place):
        q = urllib.parse.urlencode({
            "latitude": place["latitude"], "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
            "hourly": "precipitation_probability,precipitation,temperature_2m",
            "forecast_days": 7, "timezone": "auto"
        })
        with urllib.request.urlopen("https://api.open-meteo.com/v1/forecast?" + q, timeout=8) as response:
            data = json.load(response)
        return {
            "place": place,
            "current": data.get("current", {}),
            "daily": data.get("daily", {}),
            "hourly": data.get("hourly", {}),
            "timezone": data.get("timezone", "auto")
        }

    def find_locations(query):
        query = (query or "").strip()
        if len(query) < 2:
            return []
        q = urllib.parse.urlencode({
            "name": query, "count": 6, "language": "en", "format": "json"
        })
        with urllib.request.urlopen("https://geocoding-api.open-meteo.com/v1/search?" + q, timeout=8) as response:
            geo = json.load(response)
        return [{
            "id": f"{p.get('latitude')}:{p.get('longitude')}",
            "name": p.get("name", ""),
            "admin1": p.get("admin1", ""),
            "admin2": p.get("admin2", ""),
            "country": p.get("country", ""),
            "latitude": p.get("latitude"),
            "longitude": p.get("longitude")
        } for p in geo.get("results", [])]

    def irrigation_advice(crop, soil, area, weather):
        crop = crop if crop in CROP_WATER_MM else "Rice"
        soil = soil if soil in SOIL_PROFILES else "Loamy"
        profile = SOIL_PROFILES[soil]
        area = max(float(area or 1), 0.1)
        current = weather.get("current", {})
        daily = weather.get("daily", {})
        temp = float(current.get("temperature_2m") or 0)
        humidity = float(current.get("relative_humidity_2m") or 0)
        rain24 = float((daily.get("precipitation_sum") or [0])[0] or 0)
        rain48 = sum(float(x or 0) for x in (daily.get("precipitation_sum") or [])[:2])
        rain_prob = max((daily.get("precipitation_probability_max") or [0])[:2] or [0])
        base = CROP_WATER_MM[crop] * profile["factor"]

        if temp >= 35:
            base *= 1.10
        elif temp <= 20:
            base *= 0.90
        if humidity >= 80:
            base *= 0.90
        elif humidity <= 45:
            base *= 1.08

        expected_rain = min(rain24, base)
        net_mm = max(base - expected_rain, 0)
        if rain24 >= base * 0.80 or rain_prob >= 70:
            action = "Skip irrigation — rain expected"
            timing = "Recheck after the rain event"
        elif rain24 >= base * 0.35 or rain_prob >= 45:
            action = "Irrigate tomorrow"
            timing = "Wait and reassess after the next forecast update"
        else:
            action = "Irrigate now"
            timing = f"Typical interval for {soil.lower()} soil: {profile['interval']}"

        litres_per_acre = net_mm * 4046.856
        total_litres = litres_per_acre * area
        return {
            "crop": crop, "soil": soil, "soil_water_holding": profile["holding"],
            "soil_factor": profile["factor"], "irrigation_method": profile["method"],
            "soil_note": profile["note"], "typical_interval": profile["interval"],
            "action": action, "timing": timing,
            "estimated_need_mm": round(net_mm, 2),
            "estimated_litres_per_acre": round(litres_per_acre),
            "estimated_total_litres": round(total_litres),
            "rain_24h_mm": round(rain24, 2), "rain_48h_mm": round(rain48, 2),
            "rain_probability_percent": round(rain_prob),
            "temperature_c": round(temp, 1), "humidity_percent": round(humidity),
            "method": "Rule-based estimate using crop demand, selected soil, temperature, humidity and forecast rain.",
        }

    @app.get("/api/location-search")
    @login_required
    def location_search_api():
        query = request.args.get("q", "")
        try:
            return jsonify({"results": find_locations(query)})
        except Exception:
            return jsonify({"results": [], "error": "Location search is temporarily unavailable."}), 503

    @app.route("/weather")
    @login_required
    def weather():
        location = request.args.get("location", "Pudukkottai").strip() or "Pudukkottai"
        weather_data = None
        error = None
        try:
            places = find_locations(location)
            if not places:
                raise ValueError("Location not found")
            weather_data = fetch_weather_for_place(places[0])
        except Exception:
            error = "Could not load weather for that location. Search again and select a valid place."
        return render_template("weather.html", weather=weather_data, error=error, location=location)

    @app.get("/api/weather")
    @login_required
    def weather_api():
        try:
            lat = float(request.args["lat"])
            lon = float(request.args["lon"])
            name = request.args.get("name", "Selected farm")
            place = {"name": name, "latitude": lat, "longitude": lon}
            return jsonify(fetch_weather_for_place(place))
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Select a farm location first."}), 400
        except Exception:
            return jsonify({"error": "Weather service is temporarily unavailable."}), 503

    @app.get("/api/irrigation")
    @login_required
    def irrigation_api():
        try:
            lat = float(request.args["lat"])
            lon = float(request.args["lon"])
            crop = request.args.get("crop", "Rice")
            soil = request.args.get("soil", "Loamy")
            area = float(request.args.get("area", "1"))
            place = {"name": request.args.get("name", "Selected farm"), "latitude": lat, "longitude": lon}
            weather_data = fetch_weather_for_place(place)
            advice = irrigation_advice(crop, soil, area, weather_data)
            return jsonify({"location": place, "irrigation": advice})
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Select a location, crop, soil type and valid farm area."}), 400
        except Exception:
            return jsonify({"error": "Irrigation data is temporarily unavailable."}), 503

    @app.route("/equipment")
    @login_required
    def equipment():
        seed_equipment()
        category = request.args.get("category", "all")
        query = Equipment.query
        if category != "all":
            query = query.filter_by(category=category)
        items = query.order_by(Equipment.available.desc(), Equipment.price_per_day.asc()).all()
        categories = [x[0] for x in db.session.query(Equipment.category).distinct().all()]
        return render_template("equipment.html", equipment=items, categories=categories, selected=category)

    @app.post("/equipment/<int:equipment_id>/request")
    @login_required
    def request_equipment(equipment_id):
        seed_equipment()
        item = Equipment.query.get_or_404(equipment_id)
        start = request.form.get("start_date", "").strip()
        end = request.form.get("end_date", "").strip()
        if not start or not end:
            flash("Select rental dates.", "error")
        else:
            db.session.add(RentalRequest(user_id=current_user.id, equipment_id=item.id, start_date=start, end_date=end))
            db.session.commit()
            flash(f"Rental request sent for {item.name}.", "success")
        return redirect(url_for("equipment"))

    @app.route("/rentals")
    @login_required
    def rentals():
        requests = RentalRequest.query.filter_by(user_id=current_user.id).order_by(RentalRequest.created_at.desc()).all()
        return render_template("rentals.html", rentals=requests)

    @app.route("/assistant", methods=["GET", "POST"])
    @login_required
    def assistant():
        answer = None
        question = ""
        if request.method == "POST":
            question = request.form.get("question", "").strip()
            q = question.lower()
            if any(x in q for x in ["rain", "weather", "மழை"]):
                answer = "Check the Weather & Alerts page for the latest forecast. If heavy rain is expected, avoid unnecessary irrigation and plan field operations around the forecast."
            elif any(x in q for x in ["tractor", "harvester", "pump", "equipment", "machine"]):
                answer = "Open Equipment Rental to compare nearby tractors, harvesters, pumps and other machinery by category and daily rental price."
            elif any(x in q for x in ["irrigation", "water"]):
                answer = "Irrigation should be planned using crop stage, soil moisture and rainfall forecast. Avoid irrigation immediately before significant rainfall."
            elif any(x in q for x in ["crop", "paddy", "rice", "wheat", "maize"]):
                answer = "Select your crop in Profit Predictor and use the weather alerts plus farming calendar to plan operations."
            else:
                answer = "I can help with weather alerts, irrigation planning, crops, farming operations and agricultural equipment rentals. Try asking a specific question."
        return render_template("assistant.html", answer=answer, question=question)

    @app.get("/api/weather")
    @login_required
    def weather_api():
        return jsonify({"message": "Use /weather for the live dashboard."})

    @app.context_processor
    def agri_globals():
        return {"agri_nav": True}

    # Tables are created by the main application's existing initializer.
    app.extensions["agri_seed"] = seed_equipment
