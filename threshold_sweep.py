"""
Threshold sweep for the phishing URL detector.
Shows how precision / recall / F1 change as we vary the decision threshold.
"""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tldextract

from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---- Rebuild the same honest test split used during training ----
RANDOM_STATE = 10

HTML_FEATURES = [
    "no_of_forms", "no_of_Images", "no_of_hyperlinks", "no_of_external_links",
    "no_of_internal_links", "no_of_null_links", "no_of_selfreference_links",
    "no_of_empty_links", "EmptyToExternalLinksRatio", "Risky_extensions_In_Html",
    "presence_of_shorten_url_html", "hidden_elements_html",
    "Script_loaded_from_ext_domain", "suspicious_inline_js",
    "is_footer_mismatch", "is_header_mismatch", "is_copyright_mismatch",
    "is_socials_mismatch", "is_favicon_mismatch", "has_missing_title",
    "title_mismatch_with_domain", "has_inline_event_handlers", "form_action_external",
]
BROKEN_FEATURES = [
    "url_more_than_mean", "domain_more_than_mean", "count_www",
    "count_com", "special_characters_count",
]
NOT_FEATURES = ["serial_number", "url", "label"] + HTML_FEATURES + BROKEN_FEATURES

df = pd.read_csv(ROOT / "original_data.csv")
df = df.drop_duplicates(subset=["url"] + [
    c for c in df.columns if c not in ["serial_number", "url"]
]).reset_index(drop=True)

drop_cols = [c for c in NOT_FEATURES if c in df.columns]
X = df.drop(columns=drop_cols)
Y = df["label"]

def registrable_domain(url):
    e = tldextract.extract(str(url))
    return f"{e.domain}.{e.suffix}".lower()

groups = df["url"].apply(registrable_domain)
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
_, test_idx = next(gss.split(df, groups=groups))

# Reindex X columns to the trained model's expected order
FEATURES = joblib.load(ROOT / "models" / "feature_columns.pkl")
X_test = X.loc[test_idx, FEATURES]
y_test = Y.loc[test_idx]

best_name = joblib.load(ROOT / "models" / "best_model_name.pkl")
file_map = {
    "Logistic Regression": "logistic_regression.pkl",
    "Random Forest": "random_forest.pkl",
    "XGBoost": "xgboost.pkl",
}
model = joblib.load(ROOT / "models" / file_map[best_name])
print(f"Using model: {best_name}")
print(f"Test set: {len(y_test)} rows, {int(y_test.sum())} phishing / {int((1-y_test).sum())} legit\n")

# ---- Predict probabilities once ----
y_proba = model.predict_proba(X_test)[:, 1]

# ---- Sweep thresholds ----
print(f"{'thr':>6} {'prec':>8} {'recall':>8} {'f1':>8} {'num_flagged':>12} {'num_missed':>10}")
print("-" * 62)

rows = []
for t in np.arange(0.05, 0.96, 0.05):
    yp = (y_proba >= t).astype(int)
    p = precision_score(y_test, yp, zero_division=0)
    r = recall_score(y_test, yp)
    f = f1_score(y_test, yp)
    n_flagged = int(yp.sum())
    n_missed = int(((y_test == 1) & (yp == 0)).sum())
    rows.append({"threshold": round(t, 2), "precision": p, "recall": r,
                 "f1": f, "flagged": n_flagged, "missed": n_missed})
    print(f"{t:>6.2f} {p:>8.4f} {r:>8.4f} {f:>8.4f} {n_flagged:>12d} {n_missed:>10d}")

thr_df = pd.DataFrame(rows)

# ---- Best F1 ----
best_f1_row = thr_df.loc[thr_df["f1"].idxmax()]
print(f"\n>>> Best threshold by F1: {best_f1_row['threshold']:.2f}")
print(f"    F1 = {best_f1_row['f1']:.4f}  (recall {best_f1_row['recall']:.4f}, "
      f"precision {best_f1_row['precision']:.4f})")

# ---- Best threshold for "catch >= 95% of phishing" ----
recall_target = 0.95
hits = thr_df[thr_df["recall"] >= recall_target]
if len(hits):
    # among thresholds that meet recall target, pick the one with highest precision
    row = hits.loc[hits["precision"].idxmax()]
    print(f"\n>>> For recall >= {recall_target:.2f}, "
          f"best threshold = {row['threshold']:.2f}")
    print(f"    precision = {row['precision']:.4f}, recall = {row['recall']:.4f}, "
          f"F1 = {row['f1']:.4f}")
    print(f"    flagged {int(row['flagged'])} URLs, missed {int(row['missed'])} phishing")
else:
    print(f"\n>>> No threshold achieves recall >= {recall_target:.2f}")

# Save the table
thr_df.to_csv(ROOT / "threshold_sweep.csv", index=False)
print(f"\nWrote threshold_sweep.csv")