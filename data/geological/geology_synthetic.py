import numpy as np
import pandas as pd
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from pipeline_paths import get_mine, input_path

parser = argparse.ArgumentParser(description="Generate a clearly synthetic geology proxy for one mine")
parser.add_argument("--mine-id", default="dongri_buzurg")
args = parser.parse_args()
mine = get_mine(args.mine_id)

np.random.seed(42)

# Approximate AOI around the registered mine coordinate. This is a synthetic
# proxy and must be replaced by drilling/survey layers in a real deployment.
min_lon = mine['lon'] - 0.03
max_lon = mine['lon'] + 0.03
min_lat = mine['lat'] - 0.03
max_lat = mine['lat'] + 0.03

# Generate synthetic points
num_points = 10000

lon = np.random.uniform(min_lon, max_lon, num_points)
lat = np.random.uniform(min_lat, max_lat, num_points)

known_mines = [(mine['lon'], mine['lat'])]


def geology_score(lon, lat):
    base = np.random.uniform(0.1, 0.4)

    for mlon, mlat in known_mines:
        dist = np.sqrt((lon - mlon)**2 + (lat - mlat)**2)
        base += 0.6 * np.exp(-dist**2 / 0.001)

    return min(base, 1.0)


scores = [
    geology_score(x, y)
    for x, y in zip(lon, lat)
]

# Create dataset
df = pd.DataFrame({
    "longitude": lon,
    "latitude": lat,
    "geology_favorability": scores
})

# Save CSV
output = input_path("geological", args.mine_id, "geology_synthetic.csv")
output.parent.mkdir(parents=True, exist_ok=True)
if args.mine_id != "dongri_buzurg":
    output = output.with_name(f"{args.mine_id}.csv")
df.to_csv(output, index=False)

print(f"Synthetic geological proxy saved: {output}")
print(df.head())
print("Rows:", len(df))
