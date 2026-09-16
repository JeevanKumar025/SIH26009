import numpy as np
import pandas as pd

np.random.seed(42)

# Corrected Dongri Buzurg study area
min_lon = 79.66
max_lon = 79.72
min_lat = 21.52
max_lat = 21.58

# Generate synthetic points
num_points = 10000

lon = np.random.uniform(min_lon, max_lon, num_points)
lat = np.random.uniform(min_lat, max_lat, num_points)

# Verified Dongri Buzurg MOIL mine coordinate
known_mines = [(79.68289, 21.54866)]


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
df.to_csv("geology_synthetic.csv", index=False)

print("Geological dataset created successfully!")
print(df.head())
print("Rows:", len(df))