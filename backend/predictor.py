import requests
import pandas as pd
import joblib
import json
from pathlib import Path

BASE = Path(__file__).parent
MODEL = joblib.load(BASE / "../models/production_model.pkl")
HISTORY_PATH = BASE / "../data/processed/production_features.csv"
MINES_PATH = BASE / "mines.json"

FEATURE_ORDER = [
    'rainfall_mm', 'temp_max_c', 'soil_moisture_pct',
    'downtime_hrs', 'blasting_delay_hrs',
    'rainfall_lag1', 'downtime_lag1', 'soil_moisture_lag1',
    'production_lag1', 'production_lag7', 'rolling_avg_7'
]

def get_mine_coords(mine_id: str):
    mines = json.loads(MINES_PATH.read_text())
    for m in mines:
        if m["id"] == mine_id:
            return m["lat"], m["lon"]
    raise ValueError(f"Unknown mine_id: {mine_id}")

def fetch_today_weather(lat: float, lon: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=precipitation_sum,temperature_2m_max&timezone=auto&forecast_days=1"
    )
    data = requests.get(url, timeout=10).json()["daily"]
    return float(data["precipitation_sum"][0]), float(data["temperature_2m_max"][0])

def build_feature_vector(rainfall_mm, temp_max_c, soil_moisture_pct, downtime_hrs, blasting_delay_hrs):
    hist = pd.read_csv(HISTORY_PATH)
    last = hist.iloc[-1]
    last7 = hist["actual_production_t"].tail(7)

    row = {
        'rainfall_mm': rainfall_mm,
        'temp_max_c': temp_max_c,
        'soil_moisture_pct': soil_moisture_pct,
        'downtime_hrs': downtime_hrs,
        'blasting_delay_hrs': blasting_delay_hrs,
        'rainfall_lag1': last['rainfall_mm'],
        'downtime_lag1': last['downtime_hrs'],
        'soil_moisture_lag1': last['soil_moisture_pct'],
        'production_lag1': last['actual_production_t'],
        'production_lag7': hist['actual_production_t'].iloc[-7] if len(hist) >= 7 else last['actual_production_t'],
        'rolling_avg_7': last7.mean()
    }
    return pd.DataFrame([row])[FEATURE_ORDER], hist

def grouped_contributors():
    """Group model feature importances into the PS's 3 named shortfall causes."""
    importances = dict(zip(FEATURE_ORDER, MODEL.feature_importances_))
    groups = {
        "Equipment Downtime": importances['downtime_hrs'] + importances['downtime_lag1'],
        "Weather Conditions": (
            importances['rainfall_mm'] + importances['temp_max_c'] +
            importances['soil_moisture_pct'] + importances['rainfall_lag1'] +
            importances['soil_moisture_lag1']
        ),
        "Blasting Delays": importances['blasting_delay_hrs'],
    }
    total = sum(groups.values())
    return [{"cause": k, "contribution_pct": round(v / total * 100, 1)} for k, v in groups.items()]

def generate_recommendations(downtime_hrs, blasting_delay_hrs, rainfall_mm, soil_moisture_pct, risk_level):
    recs = []
    if downtime_hrs > 4:
        recs.append({
            "action": "Redeploy available equipment to reduce downtime",
            "reason": f"Equipment downtime reported at {downtime_hrs:.0f} hrs, above normal range",
            "category": "Equipment Redeployment", "priority": "HIGH"
        })
    if rainfall_mm > 50 or soil_moisture_pct > 70:
        recs.append({
            "action": "Adjust mining schedule around current wet conditions",
            "reason": f"Rainfall {rainfall_mm:.0f}mm / soil moisture {soil_moisture_pct:.0f}% impacting operations",
            "category": "Schedule Adjustment", "priority": "MEDIUM"
        })
    if blasting_delay_hrs > 2:
        recs.append({
            "action": "Reschedule blasting operations to next viable window",
            "reason": f"Blasting delay of {blasting_delay_hrs:.0f} hrs reported",
            "category": "Blasting Optimization", "priority": "MEDIUM"
        })
    if risk_level == "HIGH":
        recs.append({
            "action": "Increase equipment allocation for this period",
            "reason": "Predicted shortfall risk is HIGH based on current inputs",
            "category": "Equipment Redeployment", "priority": "HIGH"
        })
    if not recs:
        recs.append({
            "action": "Maintain current operations — no significant risk factors reported",
            "reason": "All manager-reported indicators within normal range",
            "category": "Schedule Adjustment", "priority": "LOW"
        })
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(recs, key=lambda r: priority_order[r["priority"]])

def predict(mine_id, downtime_hrs, blasting_delay_hrs, soil_moisture_pct, target_production_t):
    lat, lon = get_mine_coords(mine_id)
    rainfall_mm, temp_max_c = fetch_today_weather(lat, lon)

    X, hist = build_feature_vector(rainfall_mm, temp_max_c, soil_moisture_pct, downtime_hrs, blasting_delay_hrs)
    predicted = float(MODEL.predict(X)[0])
    shortfall = max(0, target_production_t - predicted)

    hist_shortfalls = hist['target_production_t'] - hist['actual_production_t']
    shortfall_probability = float((hist_shortfalls >= shortfall).mean() * 100)
    shortfall_probability = max(5, min(95, shortfall_probability))

    if shortfall_probability >= 65 or shortfall > 0.15 * target_production_t:
        risk = "HIGH"
    elif shortfall_probability >= 35 or shortfall > 0.05 * target_production_t:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "rainfall_mm": rainfall_mm,
        "temp_max_c": temp_max_c,
        "predicted_production_t": round(predicted, 0),
        "target_production_t": target_production_t,
        "shortfall_t": round(shortfall, 0),
        "shortfall_probability_pct": round(shortfall_probability, 0),
        "risk_level": risk,
        "contributors": grouped_contributors(),
        "recommendations": generate_recommendations(downtime_hrs, blasting_delay_hrs, rainfall_mm, soil_moisture_pct, risk)
    }