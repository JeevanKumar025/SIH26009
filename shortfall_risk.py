import pandas as pd
import numpy as np
import joblib
import argparse
from pipeline_paths import processed_dir, model_path

parser = argparse.ArgumentParser(description="Calculate production risk for one mine")
parser.add_argument("--mine-id", default="dongri_buzurg")
args = parser.parse_args()
out = processed_dir(args.mine_id)

model = joblib.load(model_path(args.mine_id, "production_model.pkl"))
df = pd.read_csv(out / "production_features.csv")
forecast = pd.read_csv(out / "production_forecast.csv").iloc[0]

feature_cols = [
    'rainfall_mm', 'temp_max_c', 'soil_moisture_pct',
    'downtime_hrs', 'blasting_delay_hrs',
    'rainfall_lag1', 'downtime_lag1', 'soil_moisture_lag1',
    'production_lag1', 'production_lag7', 'rolling_avg_7'
]

predicted = forecast['predicted_production_t']
target = forecast['target_production_t']
shortfall = forecast['expected_shortfall_t']

df['shortfall_t'] = df['target_production_t'] - df['actual_production_t']
historical_shortfalls = df['shortfall_t'].values
shortfall_probability = (historical_shortfalls >= shortfall).mean() * 100
shortfall_probability = np.clip(shortfall_probability, 5, 95)

if shortfall_probability >= 65 or shortfall > 0.15 * target:
    risk = "HIGH"
elif shortfall_probability >= 35 or shortfall > 0.05 * target:
    risk = "MEDIUM"
else:
    risk = "LOW"

importances = model.feature_importances_
contrib_df = pd.DataFrame({'feature': feature_cols, 'importance': importances}) \
    .sort_values('importance', ascending=False)

label_map = {
    'downtime_hrs': 'Equipment downtime',
    'downtime_lag1': 'Equipment downtime (recent trend)',
    'rainfall_mm': 'Rainfall',
    'rainfall_lag1': 'Rainfall (recent trend)',
    'temp_max_c': 'Land surface temperature',
    'soil_moisture_pct': 'Soil moisture',
    'soil_moisture_lag1': 'Soil moisture (recent trend)',
    'blasting_delay_hrs': 'Blasting delay',
    'production_lag1': 'Recent production trend',
    'production_lag7': 'Weekly production trend',
    'rolling_avg_7': 'Weekly production trend'
}
contrib_df['cause'] = contrib_df['feature'].map(label_map)
contrib_summary = contrib_df.groupby('cause')['importance'].sum().sort_values(ascending=False)
contrib_pct = (contrib_summary / contrib_summary.sum() * 100).round(1)

print("=== SHORTFALL RISK ASSESSMENT ===")
print(f"Predicted production : {predicted:.0f} T")
print(f"Target production    : {target:.0f} T")
print(f"Shortfall             : {shortfall:.0f} T")
print(f"Shortfall probability : {shortfall_probability:.0f}%")
print(f"Risk level             : {risk}")
print("\nRisk contributors:")
print(contrib_pct)

risk_summary = pd.DataFrame([{
    "predicted_production_t": round(predicted, 0),
    "target_production_t": round(target, 0),
    "shortfall_t": round(shortfall, 0),
    "shortfall_probability_pct": round(shortfall_probability, 0),
    "risk_level": risk
}])
risk_summary.to_csv(out / "shortfall_risk.csv", index=False)
contrib_pct.reset_index().rename(columns={"importance": "contribution_pct"}).to_csv(
    out / "risk_contributors.csv", index=False
)
print("\nSaved: shortfall_risk.csv, risk_contributors.csv")
