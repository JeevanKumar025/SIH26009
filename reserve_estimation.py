import pandas as pd

# 1a. Load Part 4 output
df = pd.read_csv("data/processed/reserve_probability_map.csv")

# 1b. Bring in NDVI from the feature dataset (join on coordinates)
features = pd.read_csv("data/processed/feature_dataset.csv")[
    ['longitude', 'latitude', 'NDVI']
]
df = df.merge(features, on=['longitude', 'latitude'], how='left')

avg_ndvi_high_zone = df.loc[df['risk_class'] == 'HIGH', 'NDVI'].mean()

PIXEL_AREA_KM2 = 0.0004  # 20m x 20m pixel

# 2. Area calculations
total_pixels = len(df)
total_area_km2 = total_pixels * PIXEL_AREA_KM2

high_pixels = (df['risk_class'] == 'HIGH').sum()
medium_pixels = (df['risk_class'] == 'MEDIUM').sum()

high_area_km2 = high_pixels * PIXEL_AREA_KM2
medium_area_km2 = medium_pixels * PIXEL_AREA_KM2
potential_zone_km2 = high_area_km2 + medium_area_km2  # HIGH + MEDIUM combined

# 3. Tonnage estimate (transparent, stated assumptions)
# Typical shallow manganese gondite ore body assumptions for a preliminary estimate:
AVG_ORE_THICKNESS_M = 3        # assumed workable ore thickness
ORE_DENSITY_T_PER_M3 = 2.7     # typical manganese ore bulk density (t/m3)
HIGH_ZONE_CONFIDENCE = 0.82    # confidence weight, reduces overestimation risk

high_area_m2 = high_area_km2 * 1_000_000
estimated_reserve_tonnes = (
    high_area_m2 * AVG_ORE_THICKNESS_M * ORE_DENSITY_T_PER_M3 * HIGH_ZONE_CONFIDENCE
)

# 4. Report
print("=== AI-BASED PRELIMINARY RESERVE ESTIMATE ===")
print(f"Total study area        : {total_area_km2:.2f} km²")
print(f"Potential zone (M+H)     : {potential_zone_km2:.2f} km²")
print(f"High-probability zone    : {high_area_km2:.2f} km²")
print(f"Estimated reserve        : {estimated_reserve_tonnes:,.0f} tonnes")
print(f"Confidence                : {HIGH_ZONE_CONFIDENCE*100:.0f}%")
print(f"Avg NDVI (high zone)     : {avg_ndvi_high_zone:.3f}")

# 5. Save summary for dashboard
summary = pd.DataFrame([{
    "total_area_km2": round(total_area_km2, 2),
    "potential_zone_km2": round(potential_zone_km2, 2),
    "high_zone_km2": round(high_area_km2, 2),
    "estimated_reserve_tonnes": round(estimated_reserve_tonnes, 0),
    "confidence_pct": HIGH_ZONE_CONFIDENCE * 100,
    "avg_ndvi_high_zone": round(avg_ndvi_high_zone, 3)
}])
summary.to_csv("data/processed/reserve_summary.csv", index=False)
print("\nSaved: reserve_summary.csv")