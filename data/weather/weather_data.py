import requests
import pandas as pd
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from pipeline_paths import get_mine, input_path

parser = argparse.ArgumentParser(description="Fetch real Open-Meteo weather for one registered mine")
parser.add_argument("--mine-id", default="dongri_buzurg")
parser.add_argument("--start-date", default="2025-01-01")
parser.add_argument("--end-date", default="2026-01-01")
args = parser.parse_args()
mine = get_mine(args.mine_id)

url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={mine['lat']}&longitude={mine['lon']}"
    f"&start_date={args.start_date}&end_date={args.end_date}"
    "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
)

response = requests.get(url, timeout=30)
response.raise_for_status()
data = response.json()

df = pd.DataFrame(data["daily"])

output = input_path("weather", args.mine_id, "weather_dongribuzurg.csv")
output.parent.mkdir(parents=True, exist_ok=True)
if args.mine_id != "dongri_buzurg":
    output = output.with_name(f"{args.mine_id}.csv")
df.to_csv(output, index=False)

print(f"Real Open-Meteo weather saved: {output}")
print(df.head())
