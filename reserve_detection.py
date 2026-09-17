import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# 1. Load merged feature dataset from Part 3
df = pd.read_csv("data/processed/feature_dataset.csv")

# 2. Derive training labels from geology_favorability (proxy ground truth)
#    threshold chosen so ~top favorable zone = positive class
df['label'] = (df['geology_favorability'] >= 0.5).astype(int)

print("Label balance:\n", df['label'].value_counts())

# 3. Features = spectral only (NOT geology_favorability — avoid circularity)
feature_cols = ['B2','B3','B4','B8','B11','B12','NDVI','NDMI']
X = df[feature_cols]
y = df['label']

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Train model
model = RandomForestClassifier(
    n_estimators=300, max_depth=12, class_weight='balanced', random_state=42
)
model.fit(X_train, y_train)

# 6. Evaluate
preds = model.predict(X_test)
print(classification_report(y_test, preds))

# 7. Predict probability for EVERY pixel (full map, not just test set)
df['manganese_probability'] = model.predict_proba(X)[:, 1]

def classify(p):
    if p >= 0.7: return 'HIGH'
    elif p >= 0.4: return 'MEDIUM'
    else: return 'LOW'

df['risk_class'] = df['manganese_probability'].apply(classify)

# 8. Save outputs
df[['longitude','latitude','manganese_probability','risk_class']].to_csv(
    "data/processed/reserve_probability_map.csv", index=False
)
joblib.dump(model, "models/reserve_model.pkl")

print("Saved: reserve_probability_map.csv, reserve_model.pkl")
print(df['risk_class'].value_counts())