import pandas as pd

# 1. Load all upstream outputs
risk = pd.read_csv("data/processed/shortfall_risk.csv").iloc[0]
contrib = pd.read_csv("data/processed/risk_contributors.csv")
reserve = pd.read_csv("data/processed/reserve_summary.csv").iloc[0]
prod_features = pd.read_csv("data/processed/production_features.csv")

latest = prod_features.iloc[-1]

recommendations = []

# 2. Rule-based logic — thresholds tuned to your synthetic data's scale
if latest['downtime_hrs'] > 4:
    recommendations.append({
        "action": "Redeploy available equipment to reduce downtime",
        "reason": f"Equipment downtime is {latest['downtime_hrs']:.0f} hrs, above normal range",
        "priority": "HIGH"
    })

if latest['rainfall_mm'] > 50:
    recommendations.append({
        "action": "Adjust mining schedule around rainfall forecast",
        "reason": f"Rainfall at {latest['rainfall_mm']:.0f}mm is significantly impacting operations",
        "priority": "MEDIUM"
    })

if latest['blasting_delay_hrs'] > 2:
    recommendations.append({
        "action": "Reschedule blasting operations to next viable window",
        "reason": f"Blasting delay of {latest['blasting_delay_hrs']:.0f} hrs detected",
        "priority": "MEDIUM"
    })

if risk['risk_level'] == "HIGH":
    recommendations.append({
        "action": "Increase equipment allocation for this period",
        "reason": f"Shortfall probability at {risk['shortfall_probability_pct']:.0f}%, predicted shortfall {risk['shortfall_t']:.0f}T",
        "priority": "HIGH"
    })

if reserve['high_zone_km2'] > 0:
    recommendations.append({
        "action": "Prioritize exploration/extraction in high-probability zone",
        "reason": f"{reserve['high_zone_km2']:.2f} km² identified as high manganese probability",
        "priority": "LOW"
    })

# Fallback if nothing triggered
if not recommendations:
    recommendations.append({
        "action": "Maintain current operations — no significant risk factors detected",
        "reason": "All monitored indicators within normal range",
        "priority": "LOW"
    })

# 3. Sort by priority (HIGH first) and save
priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
rec_df = pd.DataFrame(recommendations)
rec_df['sort_key'] = rec_df['priority'].map(priority_order)
rec_df = rec_df.sort_values('sort_key').drop(columns='sort_key')

rec_df.to_csv("data/processed/recommendations.csv", index=False)
print("=== RECOMMENDED ACTIONS ===")
print(rec_df.to_string(index=False))
print("\nSaved: recommendations.csv")