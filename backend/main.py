from fastapi import FastAPI, HTTPException
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

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
MINES_FILE = Path(__file__).resolve().parent / "mines.json"


def get_mine(mine_id: str):
    mines = json.loads(MINES_FILE.read_text(encoding="utf-8"))
    mine = next((mine for mine in mines if mine["id"] == mine_id), None)
    if mine is None:
        raise HTTPException(status_code=404, detail=f"Unknown mine_id: {mine_id}")
    return mine


def mine_data_dir(mine_id: str):
    mine = get_mine(mine_id)
    if mine["status"] != "active":
        raise HTTPException(
            status_code=409,
            detail={"message": "This mine has not been processed yet.", "mine": mine},
        )
    # Backwards-compatible while the committed Dongri files are migrated by
    # the first mine-aware pipeline run.
    scoped = DATA / mine_id
    return scoped if scoped.exists() else DATA


def read_csv(mine_id: str, filename: str):
    path = mine_data_dir(mine_id) / filename
    if not path.exists():
        raise HTTPException(status_code=409, detail="Processed outputs are incomplete for this mine.")
    return pd.read_csv(path)

@app.get("/api/reserve")
def get_reserve(mine_id: str = "dongri_buzurg"):
    return read_csv(mine_id, "reserve_summary.csv").iloc[0].to_dict()

@app.get("/api/reserve-map")
def get_reserve_map(mine_id: str = "dongri_buzurg"):
    df = read_csv(mine_id, "reserve_probability_map.csv")
    # downsample for a snappy demo (map doesn't need every pixel)
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)
    return df.to_dict(orient="records")

@app.get("/api/production")
def get_production(mine_id: str = "dongri_buzurg"):
    forecast = read_csv(mine_id, "production_forecast.csv").iloc[0].to_dict()
    history = read_csv(mine_id, "production_features.csv")[
        ["date", "actual_production_t", "target_production_t"]
    ].tail(60)
    return {"forecast": forecast, "history": history.to_dict(orient="records")}

@app.get("/api/risk")
def get_risk(mine_id: str = "dongri_buzurg"):
    risk = read_csv(mine_id, "shortfall_risk.csv").iloc[0].to_dict()
    contributors = read_csv(mine_id, "risk_contributors.csv").to_dict(orient="records")
    return {"summary": risk, "contributors": contributors}

@app.get("/api/recommendations")
def get_recommendations(mine_id: str = "dongri_buzurg"):
    return read_csv(mine_id, "recommendations.csv").to_dict(orient="records")

@app.get("/api/mines")
def get_mines():
    return json.loads(MINES_FILE.read_text(encoding="utf-8"))
