import json
import urllib.parse
import urllib.request
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

SOIL_PROFILES = {
    "Sandy": {"holding":"Low","factor":1.18,"interval":"1–2 days","method":"Drip or light, frequent irrigation","note":"Drains quickly, so smaller and more frequent irrigation is usually appropriate."},
    "Sandy Loam": {"holding":"Low–Medium","factor":1.08,"interval":"2–3 days","method":"Drip or sprinkler","note":"Good drainage with moderate storage; avoid long dry gaps."},
    "Loamy": {"holding":"Medium–High","factor":1.00,"interval":"3–4 days","method":"Drip, sprinkler or furrow","note":"Balanced drainage and storage; rainfall can extend the interval."},
    "Silty": {"holding":"High","factor":0.94,"interval":"4–5 days","method":"Drip or controlled furrow","note":"Retains water well; avoid over-irrigation and waterlogging."},
    "Clay": {"holding":"Very High","factor":0.88,"interval":"5–7 days","method":"Drip or slow furrow","note":"High water holding; irrigate slowly and allow drainage."},
}
CROP_WATER_MM = {"Rice":6.0,"Wheat":4.0,"Maize":5.0,"Cotton":5.0,"Sugarcane":7.0,"Tomato":4.0,"Potato":3.5,"Groundnut":4.5}
CROP_STAGES = {"Establishment":0.78,"Vegetative":1.00,"Flowering / Fruiting":1.16,"Grain / Bulking":1.20,"Maturity":0.76}


def fetch_weather(place):
    lat=float(place["latitude"]); lon=float(place["longitude"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid weather coordinates")
    q=urllib.parse.urlencode({
        "latitude":lat,"longitude":lon,
        "current":"temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
        "daily":"temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
        "forecast_days":7,"timezone":"auto"
    })
    url="https://api.open-meteo.com/v1/forecast?"+q
    last_error=None
    for _ in range(2):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"AgriWise/1.0"})
            with urllib.request.urlopen(req,timeout=12) as response:
                data=json.load(response)
            if data.get("error"):
                raise ValueError(data.get("reason","Weather API error"))
            return {"place":place,"current":data.get("current",{}),"daily":data.get("daily",{}),"hourly":data.get("hourly",{}),"timezone":data.get("timezone","auto")}
        except Exception as exc:
            last_error=exc
    raise RuntimeError("Weather service unavailable") from last_error


def find_locations(query):
    query=(query or "").strip()
    if len(query)<2:
        return []
    q=urllib.parse.urlencode({"name":query,"count":8,"language":"en","format":"json"})
    with urllib.request.urlopen("https://geocoding-api.open-meteo.com/v1/search?"+q,timeout=8) as response:
        geo=json.load(response)
    return [
        {"id":f"{p.get('latitude')}:{p.get('longitude')}","name":p.get("name",""),"admin1":p.get("admin1",""),
         "admin2":p.get("admin2",""),"country":p.get("country",""),"latitude":p.get("latitude"),"longitude":p.get("longitude")}
        for p in geo.get("results",[])
    ]


def day_summary(weather):
    cur=weather.get("current",{}); daily=weather.get("daily",{})
    temp=float(cur.get("temperature_2m") or 0); wind=float(cur.get("wind_speed_10m") or 0)
    rain=float((daily.get("precipitation_sum") or [0])[0] or 0)
    prob=float((daily.get("precipitation_probability_max") or [0])[0] or 0)
    if rain>=10 or prob>=70:
        return {"label":"Rainy / wet day","message":"Rain is likely today. Check drainage and avoid unnecessary irrigation.","action":"Reduce or skip irrigation"}
    if wind>=30:
        return {"label":"Windy day","message":"Strong winds are possible. Plan spraying and exposed field work carefully.","action":"Avoid unnecessary spraying"}
    if temp>=36:
        return {"label":"Hot day","message":"High heat can increase crop water demand. Check soil moisture before irrigation.","action":"Monitor soil moisture"}
    if temp<=18:
        return {"label":"Cool day","message":"Cooler conditions generally reduce crop water demand compared with hotter days.","action":"Irrigation may be less frequent"}
    return {"label":"Generally workable day","message":"Conditions are relatively moderate. Use crop stage and soil moisture for field decisions.","action":"Continue normal field checks"}


def irrigation(crop,soil,area,stage,weather):
    crop=crop if crop in CROP_WATER_MM else "Rice"
    soil=soil if soil in SOIL_PROFILES else "Loamy"
    stage=stage if stage in CROP_STAGES else "Vegetative"
    profile=SOIL_PROFILES[soil]
    area=max(float(area or 1),0.1)
    cur=weather.get("current",{}); daily=weather.get("daily",{})
    temp=float(cur.get("temperature_2m") or 0)
    humidity=float(cur.get("relative_humidity_2m") or 0)
    rain=float((daily.get("precipitation_sum") or [0])[0] or 0)
    probs=daily.get("precipitation_probability_max") or [0]
    prob=max(probs[:2] or [0])
    base=CROP_WATER_MM[crop]*profile["factor"]*CROP_STAGES[stage]
    if temp>=35: base*=1.10
    elif temp<=20: base*=0.90
    if humidity>=80: base*=0.90
    elif humidity<=45: base*=1.08
    net=max(base-min(rain,base),0)
    if rain>=base*.80 or prob>=70:
        action="Skip irrigation — rain expected"
        timing="Recheck soil moisture after the rain event"
    elif rain>=base*.35 or prob>=45:
        action="Irrigate tomorrow"
        timing="Wait for the next forecast update and inspect the field"
    elif net<=0.05:
        action="No irrigation needed"
        timing="Recheck soil moisture before the next irrigation cycle"
    else:
        action="Irrigate now"
        timing=f"Typical interval for {soil.lower()} soil: {profile['interval']}"
    per=net*4046.856
    return {
        "crop":crop,"soil":soil,"stage":stage,"soil_water_holding":profile["holding"],
        "irrigation_method":profile["method"],"soil_note":profile["note"],"typical_interval":profile["interval"],
        "action":action,"timing":timing,"estimated_need_mm":round(net,2),
        "estimated_litres_per_acre":round(per),"estimated_total_litres":round(per*area),
        "rain_24h_mm":round(rain,2),"rain_probability_percent":round(prob),
        "temperature_c":round(temp,1),"humidity_percent":round(humidity),"stage_factor":CROP_STAGES[stage],
        "method":"Rule-based estimate using crop demand, growth stage, selected soil, current weather and forecast rain. Confirm with field soil moisture, irrigation-system efficiency and local agronomist guidance."
    }


def register_agri_features(app,db):
    class Equipment(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        name=db.Column(db.String(120),nullable=False)
        category=db.Column(db.String(80),nullable=False)
        owner_name=db.Column(db.String(120),nullable=False)
        location=db.Column(db.String(160),nullable=False)
        price_per_day=db.Column(db.Float,nullable=False)
        available=db.Column(db.Boolean,default=True,nullable=False)
        rating=db.Column(db.Float,default=4.5,nullable=False)

    class RentalRequest(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
        equipment_id=db.Column(db.Integer,db.ForeignKey("equipment.id"),nullable=False)
        start_date=db.Column(db.String(20),nullable=False)
        end_date=db.Column(db.String(20),nullable=False)
        status=db.Column(db.String(30),default="Pending",nullable=False)
        created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
        equipment=db.relationship("Equipment")

    seed=[
        ("Mahindra 575 DI Tractor","Tractor","Kumar Agro Services","Pudukkottai",1400,4.8),
        ("Sonalika Tiger Harvester","Harvester","Green Field Rentals","Pudukkottai",3200,4.7),
        ("Kirloskar 5HP Water Pump","Irrigation","Sri Farm Equipments","Pudukkottai",650,4.6),
        ("Rotavator 6ft","Tillage","Vetri Machinery","Pudukkottai",900,4.5),
        ("Battery Crop Sprayer","Sprayer","AgriTech Rentals","Pudukkottai",450,4.4),
        ("Power Tiller","Tiller","FarmEase","Pudukkottai",850,4.6)
    ]

    def seed_equipment():
        if Equipment.query.count()==0:
            for n,c,o,l,p,r in seed:
                db.session.add(Equipment(name=n,category=c,owner_name=o,location=l,price_per_day=p,rating=r))
            db.session.commit()

    @app.get("/api/location-search")
    @login_required
    def location_search_api():
        try:
            return jsonify({"results":find_locations(request.args.get("q",""))})
        except Exception:
            return jsonify({"results":[],"error":"Location search is temporarily unavailable."}),503

    @app.route("/weather")
    @login_required
    def weather():
        location=request.args.get("location","Pudukkottai").strip() or "Pudukkottai"
        try:
            if request.args.get("lat") and request.args.get("lon"):
                place={"name":location,"latitude":float(request.args["lat"]),"longitude":float(request.args["lon"]),"country":request.args.get("country","")}
            else:
                places=find_locations(location)
                if not places:
                    raise ValueError("No matching place")
                place=places[0]
                location=place["name"]
            data=fetch_weather(place)
            return render_template("weather.html",weather=data,error=None,location=location,day_summary=day_summary(data),selected_place=place)
        except ValueError:
            msg="That place was not found. Search for a village, town, district or city and select a result."
        except Exception:
            msg="Weather data is temporarily unavailable for that place. Please try again."
        return render_template("weather.html",weather=None,error=msg,location=location,day_summary=None,selected_place=None)

    @app.get("/api/weather")
    @login_required
    def weather_api():
        try:
            place={"name":request.args.get("name","Selected weather location"),"latitude":float(request.args["lat"]),"longitude":float(request.args["lon"])}
            return jsonify(fetch_weather(place))
        except (KeyError,TypeError,ValueError):
            return jsonify({"error":"Select a weather location first."}),400
        except Exception:
            return jsonify({"error":"Weather service is temporarily unavailable."}),503

    @app.get("/api/irrigation")
    @login_required
    def irrigation_api():
        try:
            place={"name":request.args.get("name","Selected weather location"),"latitude":float(request.args["lat"]),"longitude":float(request.args["lon"])}
            data=fetch_weather(place)
            result=irrigation(request.args.get("crop","Rice"),request.args.get("soil","Loamy"),float(request.args.get("area","1")),request.args.get("stage","Vegetative"),data)
            return jsonify({"location":place,"irrigation":result})
        except (KeyError,TypeError,ValueError):
            return jsonify({"error":"Select a weather location, crop, soil type, growth stage and a valid area."}),400
        except Exception:
            return jsonify({"error":"Irrigation data is temporarily unavailable."}),503

    @app.route("/equipment")
    @login_required
    def equipment():
        seed_equipment()
        category=request.args.get("category","all")
        q=Equipment.query
        if category!="all":
            q=q.filter_by(category=category)
        return render_template("equipment.html",equipment=q.order_by(Equipment.available.desc(),Equipment.price_per_day.asc()).all(),categories=[x[0] for x in db.session.query(Equipment.category).distinct().all()],selected=category)

    @app.post("/equipment/<int:equipment_id>/request")
    @login_required
    def request_equipment(equipment_id):
        seed_equipment()
        item=Equipment.query.get_or_404(equipment_id)
        start=request.form.get("start_date","").strip()
        end=request.form.get("end_date","").strip()
        try:
            start_dt=datetime.strptime(start,"%Y-%m-%d").date()
            end_dt=datetime.strptime(end,"%Y-%m-%d").date()
            today=datetime.utcnow().date()
            if start_dt < today: raise ValueError("past")
            if end_dt < start_dt: raise ValueError("order")
            days=(end_dt-start_dt).days+1
            if days > 60: raise ValueError("long")
        except ValueError as exc:
            msg={"past":"Rental start date cannot be in the past.","order":"End date must be on or after the start date.","long":"Rental requests are limited to 60 days."}.get(str(exc),"Enter valid rental dates.")
            flash(msg,"error")
            return redirect(url_for("equipment"))
        if not item.available:
            flash("This equipment is currently unavailable.","error")
            return redirect(url_for("equipment"))
        conflicts=RentalRequest.query.filter(
            RentalRequest.equipment_id==item.id,
            RentalRequest.status.in_(["Pending","Approved"]),
            RentalRequest.start_date <= end,
            RentalRequest.end_date >= start
        ).count()
        if conflicts:
            flash("Those dates overlap an existing request. Choose different dates.","error")
            return redirect(url_for("equipment"))
        db.session.add(RentalRequest(user_id=current_user.id,equipment_id=item.id,start_date=start,end_date=end))
        db.session.commit()
        flash(f"Rental request sent for {item.name} for {days} day(s). Estimated rental: ₹{days*item.price_per_day:,.0f}.","success")
        return redirect(url_for("rentals"))

    @app.route("/rentals")
    @login_required
    def rentals():
        return render_template("rentals.html",rentals=RentalRequest.query.filter_by(user_id=current_user.id).order_by(RentalRequest.created_at.desc()).all())

    @app.route("/assistant",methods=["GET","POST"])
    @login_required
    def assistant():
        question=""; answer=None
        if request.method=="POST":
            question=request.form.get("question","").strip()
            q=question.lower()
            if any(x in q for x in ["rain","weather"]):
                answer="Use Weather & Farming Day to check the selected weather location and today's conditions."
            elif any(x in q for x in ["irrigation","water"]):
                answer="Select a weather location, crop, soil type and growth stage. The planner combines forecast rain with soil water-holding characteristics and crop demand."
            elif any(x in q for x in ["tractor","harvester","pump","equipment"]):
                answer="Open Equipment Rental to compare machinery, choose dates and submit a rental request. The system checks overlapping requests."
            elif any(x in q for x in ["profit","cost","income","roi"]):
                answer="Use Profit Predictor to enter your farm area, expected yield, market price and production costs. Review revenue, profit, ROI and break-even values."
            elif any(x in q for x in ["what if","scenario","price change","yield change"]):
                answer="Use the What-if Simulator inside Profit Predictor to test price, yield and cost changes before committing to a farm plan."
            else:
                answer="I can help with weather, crop planning, irrigation, equipment rentals, farm costs, profit prediction and what-if scenarios."
        return render_template("assistant.html",answer=answer,question=question)

    @app.context_processor
    def agri_globals():
        return {"agri_nav":True,"soil_profiles":SOIL_PROFILES,"crop_stages":CROP_STAGES}

    app.extensions["agri_seed"]=seed_equipment
