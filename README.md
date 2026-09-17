# VantaWenge
### AI-Based Manganese Reserve Identification & Production Planning System
**Smart India Hackathon — Problem Statement SIH26009 (MOIL Limited)**

---

## 1. Problem Statement Summary:

MOIL Limited, India's largest manganese ore producer, currently relies on manual
surveys, drilling results, and production records for reserve estimation and
production planning — a slow process that often causes a mismatch between
expected and actual ore output.

**The ask:** an AI/ML solution that uses geological data, historical production,
equipment performance, and satellite/space technology inputs to:
1. Identify and map manganese reserves using surface and sub-surface indicators
2. Predict production shortfalls (equipment downtime, weather, blasting delays)
3. Suggest corrective actions (schedule adjustment, blasting optimization,
   equipment redeployment)
4. Present all of this in a user-friendly dashboard

---

## 2. Our Solution — VantaWenge

An end-to-end pipeline: **Satellite + Weather + Production data → AI models →
Explainable risk & recommendations → Interactive dashboard.**

Study area: **Dongri Buzurg manganese mine, Bhandara district, Maharashtra**
(real, verified MOIL-belt mine location — 21.55°N, 79.69°E), AOI ≈ 41 km².

```
Satellite (Sentinel-2) + Geological + Weather + Production + Equipment Data
                              ↓
                       DATA PROCESSING
                              ↓
             ┌────────────────┴────────────────┐
             ↓                                  ↓
     Manganese Reserve AI                Production Forecast AI
             ↓                                  ↓
      Reserve Probability                  Shortfall Risk
             ↓                                  ↓
             └────────────────┬────────────────┘
                              ↓
                   Recommendation Engine
                              ↓
                       WEB DASHBOARD
                              ↓
             Map + Reserves + Trends + Risk + Actions
```

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Satellite data | Google Earth Engine (Sentinel-2 SR, Copernicus) |
| Data processing | Python — pandas, numpy, rasterio, scipy |
| Reserve detection model | scikit-learn Random Forest Classifier |
| Production forecast model | scikit-learn Random Forest Regressor |
| Recommendation logic | Rule-based Python engine |
| Backend API | FastAPI (Python) |
| Frontend | React (Vite) |
| Mapping | Leaflet / react-leaflet + OpenStreetMap tiles |
| Charts | Recharts |
| Database (prototype) | Flat CSV files (SQLite/PostGIS-ready for production) |
| Weather data | Open-Meteo API |

---

## 4. Data Sources

| Data | Source | Type |
|---|---|---|
| Satellite bands (B2,B3,B4,B8,B11,B12) + NDVI + NDMI | Sentinel-2 via Google Earth Engine | **Real** |
| Geological favorability layer (sub-surface proxy) | Synthetic, anchored to verified real mine coordinates | Synthetic (clearly labeled) |
| Rainfall, land surface temperature (max/min) | Open-Meteo historical API — **fetched AND used directly as model features** | **Real** |
| Soil moisture | Synthetic AR(1) process driven by real rainfall (rises after rain, decays otherwise) — no free real-time source available for this exact point | Synthetic (clearly labeled, physically realistic) |
| Production / equipment downtime / blasting delay | Generated synthetic dataset, statistically correlated with real rainfall + temperature (weather → downtime → shortfall) | Synthetic (clearly labeled) |

We are transparent about this split — real MOIL operational data isn't
publicly available, so synthetic data was used for anything beyond satellite
and public weather sources, exactly as expected for a prototype-stage
hackathon submission. Note: rainfall and temperature are genuinely fetched
from Open-Meteo **and** flow into the production forecasting model as real
features — not just displayed separately.

---

## 5. Core Features / Modules

### A. Manganese Reserve Identification
- Sentinel-2 spectral bands + NDVI (vegetation index) + NDMI processed into a
  per-pixel feature table
- Random Forest classifier trained on spectral features to output a
  **manganese probability score** per 20m pixel
- Classified into LOW / MEDIUM / HIGH probability zones
- Converted into **area (km²) and preliminary tonnage estimate**, clearly
  labeled *"AI-based preliminary reserve estimate"* — not a certified
  geological reserve figure

### B. Production Shortfall Prediction
- Random Forest regressor trained on historical production + **real rainfall**
  + **real land surface temperature** + synthetic soil moisture + equipment
  downtime + blasting delay, using lag features and a time-based train/test
  split (not random split — avoids data leakage in time series)
- Outputs next-period production forecast vs target, and expected shortfall

### C. Explainable Risk Scoring
- Shortfall probability derived from historical shortfall distribution
- Risk level: LOW / MEDIUM / HIGH
- **Risk contributors are the model's actual feature importances** — not
  hardcoded numbers — so every percentage shown is traceable back to what the
  model learned, including rainfall, temperature, and soil moisture
  contributions specifically

### D. Recommendation Engine
- Rule-based (deterministic, demo-safe — no LLM variability)
- Triggers on real thresholds: equipment downtime, rainfall, blasting delay,
  risk level, high-probability zone size
- Outputs prioritized actions: redeploy equipment, adjust schedule,
  reschedule blasting, prioritize high-probability zones

### E. Interactive Dashboard
- Summary cards: Reserve area, Estimated tonnage, Avg NDVI (high zone),
  Shortfall, Risk level
- Interactive map (Leaflet) — pixel-level manganese probability, color-coded
- Production trend chart — actual vs target, last 60 days
- Risk panel — risk level + explainable contributor breakdown (now includes
  rainfall, temperature, and soil moisture as named contributors)
- Recommendations panel — prioritized corrective actions with reasons

---

## 6. What's Real vs What's Simulated (be upfront about this in the PPT)

| Component | Real | Simulated |
|---|---|---|
| Satellite imagery & indices (bands, NDVI, NDMI) | ✅ | |
| Weather — rainfall & land surface temperature | ✅ (fetched **and** used as model features) | |
| Mine location (Dongri Buzurg) | ✅ | |
| Soil moisture | | ✅ (rainfall-driven synthetic process, physically realistic) |
| Geological sub-surface layer | | ✅ (synthetic proxy, anchored to real mine) |
| Equipment downtime / blasting delay records | | ✅ (statistically realistic synthetic data) |

All four satellite/space inputs named in the problem statement — rainfall,
soil moisture, vegetation index (NDVI), and land surface temperature — are
now represented as actual model features, not just fetched and left unused.

---

## 7. Known Limitations / Future Scope

- **Sub-surface geological indicators are synthetic** (a proxy layer anchored
  to the real mine coordinate, not derived from actual drilling/survey data).
  This is the most significant simplification in the prototype — real GSI
  survey layers or drilling logs would directly replace this input with no
  change to the model architecture
- Soil moisture is a physically-motivated synthetic process (rainfall-driven
  decay model), since no free real-time soil moisture source exists for this
  exact point — a real dataset (e.g. SMAP) would be a direct drop-in
  replacement
- No real-time IoT/equipment telemetry — designed to be added as a live data
  feed replacing the static production CSV
- Equipment performance is represented as a single downtime metric, not
  per-equipment granularity (utilization %, maintenance history) — a
  reasonable next step for a fuller deployment
- Reserve tonnage uses stated assumptions (ore thickness, density) rather
  than measured values — intentional and disclosed, standard for a
  preliminary AI estimate

---

## 8. Project Structure

```
ManganeseMining/
├── backend/
│   └── main.py                  # FastAPI app serving processed data as JSON
├── data/
│   ├── satellite/
│   │   └── dongri_buzurg_features.tif
│   ├── geological/
│   │   └── geology_synthetic.csv
│   ├── weather/
│   │   └── weather_dongribuzurg.csv
│   ├── production/
│   │   └── production_data.csv
│   └── processed/
│       ├── feature_dataset.csv
│       ├── reserve_probability_map.csv
│       ├── reserve_summary.csv
│       ├── production_features.csv
│       ├── production_forecast.csv
│       ├── shortfall_risk.csv
│       ├── risk_contributors.csv
│       └── recommendations.csv
├── models/
│   ├── reserve_model.pkl
│   └── production_model.pkl
└── frontend/
    └── src/
        ├── App.jsx
        └── components/
            ├── SummaryCards.jsx
            ├── ReserveMap.jsx
            ├── ProductionChart.jsx
            ├── RiskPanel.jsx
            └── RecommendationsPanel.jsx
```

---

## 9. How to Run

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173` (Vite default) · API: `http://localhost:8000`

---

## 10. Team — VantaWenge

| Member | Role |
|---|---|
| Member 1 | Satellite/GIS — Sentinel-2 processing, indices, geospatial data |
| Member 2 | Reserve AI — classification model, reserve estimation |
| Member 3 | Production AI — forecasting, shortfall risk |
| Member 4 | Backend — FastAPI, API integration, database |
| Member 5 | Frontend — React dashboard, charts, map UI |
| Member 6 | Integration, recommendation engine, documentation, PPT/demo |
