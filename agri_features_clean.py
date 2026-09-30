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
CROP_WATER_MM={"Rice":6.0,"Wheat":4.0,"Maize":5.0,"Cotton":5.0,"Sugarcane":7.0,"Tomato":4.0,"Potato":3.5,"Groundnut":4.5}\nCROP_STAGES={"Establishment":0.78,"Vegetative":1.00,"Flowering / Fruiting":1.16,"Grain / Bulking":1.20,"Maturity":0.76}

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
            req=urllib.request.Request(url,headers={"User-Agent":"FarmProfit/1.0"})
            with urllib.request.urlopen(req,timeout=12) as response:
                data=json.load(response)
            if data.get("error"): raise ValueError(data.get("reason","Weather API error"))
            return {"place":place,"current":data.get("current",{}),"daily":data.get("daily",{}),"hourly":data.get("hourly",{}),"timezone":data.get("timezone","auto")}
        except Exception as exc:
            last_error=exc
    raise RuntimeError("Weather service unavailable") from last_error

def find_locations(query):
    if len((query or "").strip())<2:return []
    q=urllib.parse.urlencode({"name":query.strip(),"count":8,"language":"en","format":"json"})
    with urllib.request.urlopen("https://geocoding-api.open-meteo.com/v1/search?"+q,timeout=8) as response:
        geo=json.load(response)
    return [{"id":f"{p.get('latitude')}:{p.get('longitude')}","name":p.get("name",""),"admin1":p.get("admin1",""),"admin2":p.get("admin2",""),"country":p.get("country",""),"latitude":p.get("latitude"),"longitude":p.get("longitude")} for p in geo.get("results",[])]

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
        "crop":crop,"soil":soil,"stage":stage,
        "soil_water_holding":profile["holding"],
        "irrigation_method":profile["method"],
        "soil_note":profile["note"],
        "typical_interval":profile["interval"],
        "action":action,"timing":timing,
        "estimated_need_mm":round(net,2),
        "estimated_litres_per_acre":round(per),
        "estimated_total_litres":round(per*area),
        "rain_24h_mm":round(rain,2),
        "rain_probability_percent":round(prob),
        "temperature_c":round(temp,1),
        "humidity_percent":round(humidity),
        "stage_factor":CROP_STAGES[stage],
        "method":"Rule-based estimate using crop demand, growth stage, selected soil, current weather and forecast rain. Confirm with field soil moisture, irrigation-system efficiency and local agronomist guidance."
    }

