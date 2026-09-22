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
