import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from pipeline_paths import input_path

parser = argparse.ArgumentParser(description="Generate synthetic operational data from one mine's real weather")
parser.add_argument("--mine-id", default="dongri_buzurg")
args = parser.parse_args()

np.random.seed(42)

# 1. Load REAL weather data (Open-Meteo) instead of generating fake rainfall
weather = pd.read_csv(input_path("weather", args.mine_id, "weather_dongribuzurg.csv"))
weather['time'] = pd.to_datetime(weather['time'])
weather = weather.rename(columns={
    'time': 'date',
    'precipitation_sum': 'rainfall_mm',
    'temperature_2m_max': 'temp_max_c',
    'temperature_2m_min': 'temp_min_c'
})

# Use first 365 days to match original production period
weather = weather.sort_values('date').reset_index(drop=True).iloc[:365]
dates = weather['date']
rainfall = weather['rainfall_mm'].values
temp_max = weather['temp_max_c'].values
temp_min = weather['temp_min_c'].values

# 2. Synthetic soil moisture — AR(1) process driven by REAL rainfall
#    (labeled synthetic: no free real-time soil moisture source for this
#    exact point, but behavior is physically realistic — rises after rain,
#    decays gradually otherwise)
soil_moisture = np.zeros(len(dates))
soil_moisture[0] = 30.0  # starting %, mid-range
decay = 0.92
for i in range(1, len(dates)):
    rain_input = min(rainfall[i], 100) * 0.4  # rainfall boosts moisture
    soil_moisture[i] = decay * soil_moisture[i-1] + rain_input
soil_moisture = np.clip(soil_moisture + np.random.normal(0, 2, len(dates)), 5, 95)

# 3. Equipment downtime / blasting delay — now driven by REAL rainfall
downtime_hrs = np.random.poisson(2, len(dates)) + (rainfall > 50) * np.random.poisson(3, len(dates))
blasting_delay = np.random.poisson(1, len(dates)) + (rainfall > 80) * np.random.poisson(2, len(dates))

# 4. Production — same causal logic, now using real rainfall + real temperature
target_production = 1000 + np.zeros(len(dates))
actual_production = target_production \
    - downtime_hrs * 15 \
    - blasting_delay * 25 \
    - rainfall * 1.2 \
    - np.clip(temp_max - 35, 0, None) * 5 \
    + np.random.normal(0, 30, len(dates))
actual_production = np.clip(actual_production, 300, None)

df = pd.DataFrame({
    'date': dates,
    'rainfall_mm': rainfall.round(1),
    'temp_max_c': temp_max.round(1),
    'temp_min_c': temp_min.round(1),
    'soil_moisture_pct': soil_moisture.round(1),
    'downtime_hrs': downtime_hrs,
    'blasting_delay_hrs': blasting_delay,
    'target_production_t': target_production,
    'actual_production_t': actual_production.round(1)
})
output = input_path("production", args.mine_id, "production_data.csv")
output.parent.mkdir(parents=True, exist_ok=True)
if args.mine_id != "dongri_buzurg":
    output = output.with_name(f"{args.mine_id}.csv")
df.to_csv(output, index=False)

print(f"{output.name} regenerated using REAL weather + synthetic soil moisture")
print(df.head())
