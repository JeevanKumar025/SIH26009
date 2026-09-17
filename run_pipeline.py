"""Run the existing prototype modules for one mine in their required order.

Satellite GeoTIFF creation is intentionally not faked here. Put a real
Sentinel-2-derived `<mine_id>_features.tif` in data/satellite first.
"""
import argparse
import subprocess
import sys
from pipeline_paths import ROOT, get_mine

parser = argparse.ArgumentParser(description="Run VantaWenge's mine-scoped pipeline")
parser.add_argument("--mine-id", required=True)
parser.add_argument("--refresh-weather", action="store_true", help="Fetch fresh real Open-Meteo weather first")
parser.add_argument("--regenerate-synthetic-inputs", action="store_true", help="Regenerate disclosed synthetic geology and operations inputs")
args = parser.parse_args()

mine = get_mine(args.mine_id)
satellite = ROOT / "data" / "satellite" / f"{args.mine_id}_features.tif"
if not satellite.exists() and args.mine_id == "dongri_buzurg":
    satellite = ROOT / "data" / "satellite" / "dongri_buzurg_features.tif"
if not satellite.exists():
    raise SystemExit(f"Missing real satellite input: {satellite}")

def run(script):
    subprocess.run([sys.executable, script, "--mine-id", args.mine_id], cwd=ROOT, check=True)

if args.refresh_weather:
    run("data/weather/weather_data.py")
if args.regenerate_synthetic_inputs:
    run("data/geological/geology_synthetic.py")
    run("data/production/production_data.py")

for script in [
    "satellite_processing.py", "reserve_detection.py", "reserve_estimation.py",
    "production_forecasting.py", "shortfall_risk.py", "recommendation_engine.py",
]:
    run(script)

print(f"Completed mine-scoped outputs for {mine['name']}.")
