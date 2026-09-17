import rasterio
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import argparse
from pipeline_paths import ROOT, input_path, processed_dir

parser = argparse.ArgumentParser(description="Create reserve features for one mine")
parser.add_argument("--mine-id", default="dongri_buzurg")
args = parser.parse_args()
mine_id = args.mine_id
satellite_file = ROOT / "data" / "satellite" / f"{mine_id}_features.tif"
if not satellite_file.exists() and mine_id == "dongri_buzurg":
    satellite_file = ROOT / "data" / "satellite" / "dongri_buzurg_features.tif"
if not satellite_file.exists():
    raise FileNotFoundError(f"Missing satellite GeoTIFF: {satellite_file}")

# 1. Read satellite GeoTIFF
with rasterio.open(satellite_file) as src:
    bands = src.read()  # shape: (8, height, width) -> B2,B3,B4,B8,B11,B12,NDVI,NDMI
    transform = src.transform
    height, width = src.height, src.width

# 2. Build pixel coordinate grid
rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
xs, ys = rasterio.transform.xy(transform, rows, cols)
pixel_lon = np.array(xs)
pixel_lat = np.array(ys)

# 3. Load geology points
geo = pd.read_csv(input_path("geological", mine_id, "geology_synthetic.csv"))

# 4. Interpolate geology onto satellite pixel grid
geology_grid = griddata(
    points=geo[['longitude', 'latitude']].values,
    values=geo['geology_favorability'].values,
    xi=(pixel_lon, pixel_lat),
    method='linear',
    fill_value=geo['geology_favorability'].mean()  # avoid NaN at edges
)

# 5. Flatten everything into one feature table
band_names = ['B2','B3','B4','B8','B11','B12','NDVI','NDMI']
data = {name: bands[i].flatten() for i, name in enumerate(band_names)}
data['longitude'] = pixel_lon.flatten()
data['latitude'] = pixel_lat.flatten()
data['geology_favorability'] = geology_grid.flatten()

df = pd.DataFrame(data)
df.to_csv(processed_dir(mine_id) / "feature_dataset.csv", index=False)

print("Feature dataset created:", df.shape)
print(df.head())
