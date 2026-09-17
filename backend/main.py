from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import json


app = FastAPI(title="VantaWenge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for hackathon demo
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = Path(__file__).resolve().parent.parent / "data" / "processed"

@app.get("/api/reserve")
def get_reserve():
    return pd.read_csv(DATA / "reserve_summary.csv").iloc[0].to_dict()

@app.get("/api/reserve-map")
def get_reserve_map():
    df = pd.read_csv(DATA / "reserve_probability_map.csv")
    # downsample for a snappy demo (map doesn't need every pixel)
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)
    return df.to_dict(orient="records")

@app.get("/api/production")
def get_production():
    forecast = pd.read_csv(DATA / "production_forecast.csv").iloc[0].to_dict()
    history = pd.read_csv(DATA / "production_features.csv")[
        ["date", "actual_production_t", "target_production_t"]
    ].tail(60)
    return {"forecast": forecast, "history": history.to_dict(orient="records")}

@app.get("/api/risk")
def get_risk():
    risk = pd.read_csv(DATA / "shortfall_risk.csv").iloc[0].to_dict()
    contributors = pd.read_csv(DATA / "risk_contributors.csv").to_dict(orient="records")
    return {"summary": risk, "contributors": contributors}

@app.get("/api/recommendations")
def get_recommendations():
    return pd.read_csv(DATA / "recommendations.csv").to_dict(orient="records")

@app.get("/api/mines")
def get_mines():
    with open("mines.json") as f:
        return json.load(f)