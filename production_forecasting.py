import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Load production dataset (now with real weather + soil moisture)
df = pd.read_csv("data/production/production_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# 2. Feature engineering — lag features so model sees recent trend
df['rainfall_lag1'] = df['rainfall_mm'].shift(1)
df['downtime_lag1'] = df['downtime_hrs'].shift(1)
df['soil_moisture_lag1'] = df['soil_moisture_pct'].shift(1)
df['production_lag1'] = df['actual_production_t'].shift(1)
df['production_lag7'] = df['actual_production_t'].shift(7)
df['rolling_avg_7'] = df['actual_production_t'].rolling(7).mean()

df = df.dropna().reset_index(drop=True)

# 3. Features / target — now includes temperature + soil moisture
feature_cols = [
    'rainfall_mm', 'temp_max_c', 'soil_moisture_pct',
    'downtime_hrs', 'blasting_delay_hrs',
    'rainfall_lag1', 'downtime_lag1', 'soil_moisture_lag1',
    'production_lag1', 'production_lag7', 'rolling_avg_7'
]
X = df[feature_cols]
y = df['actual_production_t']

# 4. Time-based split (NOT random — production is a time series)
split_idx = int(len(df) * 0.85)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# 5. Train
model = RandomForestRegressor(n_estimators=300, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 6. Evaluate
preds = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, preds))
print("R2 :", r2_score(y_test, preds))

# 7. Predict "next period" using the most recent row's features
latest_features = X.iloc[[-1]]
next_prediction = model.predict(latest_features)[0]
target_production = df['target_production_t'].iloc[-1]

print(f"\nPredicted next-period production: {next_prediction:.0f} T")
print(f"Target production               : {target_production:.0f} T")
print(f"Expected shortfall              : {max(0, target_production - next_prediction):.0f} T")

# 8. Save
joblib.dump(model, "models/production_model.pkl")
df.to_csv("data/processed/production_features.csv", index=False)

forecast_summary = pd.DataFrame([{
    "predicted_production_t": round(next_prediction, 0),
    "target_production_t": round(target_production, 0),
    "expected_shortfall_t": round(max(0, target_production - next_prediction), 0)
}])
forecast_summary.to_csv("data/processed/production_forecast.csv", index=False)
print("\nSaved: production_model.pkl, production_features.csv, production_forecast.csv")