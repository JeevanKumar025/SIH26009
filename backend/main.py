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
    # Regular lat/lon grid -> return as a compact raster grid instead of
    # per-point records, so the frontend can render continuous probability
    # zones (an image overlay) instead of individual dot markers.
    nx = df["longitude"].nunique()
    ny = df["latitude"].nunique()

    # Sort so the flattened array reads top-to-bottom (north -> south),
    # left-to-right (west -> east), matching standard image row order.
    grid = df.sort_values(["latitude", "longitude"], ascending=[False, True])

    return {
        "nx": int(nx),
        "ny": int(ny),
        "lon_min": float(df["longitude"].min()),
        "lon_max": float(df["longitude"].max()),
        "lat_min": float(df["latitude"].min()),
        "lat_max": float(df["latitude"].max()),
        "probability": grid["manganese_probability"].round(4).tolist(),
    }

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