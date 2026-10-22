import os
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from feature_extraction.extractor import url_to_features
from inference_config import PHISHING_THRESHOLD


# Load model + feature list
FEATURES = joblib.load(ROOT / "models" / "feature_columns.pkl")
best_name = joblib.load(ROOT / "models" / "best_model_name.pkl")
file_map = {
    "Logistic Regression": "logistic_regression.pkl",
    "Random Forest": "random_forest.pkl",
    "XGBoost": "xgboost.pkl",
}
model = joblib.load(ROOT / "models" / file_map[best_name])
print(f"Best model: {best_name}")
print(f"Model expects {len(FEATURES)} features\n")


# Feature-parity diagnostic
# (catches the "silent zero-fill" trap before we run predictions)

test_urls = [
    "https://www.google.com/",
    "https://www.telegram.org/",
    "https://web.telegram.org/",
    "https://t.me/somechannel",
    "https://www.wikipedia.org/",
    "http://paypal-secure-login.com/verify/account.php?token=x",
    "http://192.168.1.1/login.php",
]

sample = url_to_features(test_urls[0], html="")
missing = set(FEATURES) - set(sample.keys())
extra   = set(sample.keys()) - set(FEATURES)

print("Feature-parity check (on first test URL):")
print(f"  Features expected by model:     {len(FEATURES)}")
print(f"  Features returned by extractor: {len(sample)}")
print(f"  Missing from extractor (filled with 0): {sorted(missing) if missing else 'none'}")
print(f"  Extra from extractor (ignored):          {sorted(extra) if extra else 'none'}")
if missing:
    print("  WARNING: missing features are silently 0 — predictions may be wrong!")
print()


# Predictions
rows = []
for u in test_urls:
    feats = url_to_features(u, html="")   # empty HTML = matches live pipeline
    row = pd.DataFrame([feats]).reindex(columns=FEATURES, fill_value=0)
    prob = model.predict_proba(row)[0, 1]
    rows.append({
        "url": u,
        "p_phishing": round(float(prob), 4),
        "predicted": int(prob >= PHISHING_THRESHOLD),
    })

print(pd.DataFrame(rows).to_string(index=False))