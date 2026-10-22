import os
import joblib
import numpy as np
import pandas as pd
import tldextract

from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    make_scorer,
)

from classifiers import logistic_regression, random_forest, xg_boost

RANDOM_STATE = 10

# 1. 
# Only keeping features that can be computed from the URL string alone.
#cuz these features need us to fetch the HTML page to compute them, which will cost us response time and security risk.
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

# inference-undefined features.
# - *_more_than_mean: mean computed on the training set, undefined at inference.
# - count_www / count_com: count substrings like "www"/"com" inside the URL which is not needed.
# - special_characters_count: just the sum of columns you already have.
BROKEN_FEATURES = [
    "url_more_than_mean",
    "domain_more_than_mean",
    "count_www",
    "count_com",
    "special_characters_count",
]

NOT_FEATURES = ["serial_number", "url", "label"] + HTML_FEATURES + BROKEN_FEATURES


df = pd.read_csv("original_data.csv")

print("Original dataset:")
print("Total rows:", df.shape[0])
print("Total columns:", df.shape[1])

print("\nClass distribution:")
print(df["label"].value_counts())


# 2. Remove duplicate website records
df = df.drop_duplicates(subset=["url"] + [
    col for col in df.columns
    if col not in ["serial_number", "url"]
]).reset_index(drop=True)

print("\nAfter removing duplicate website records:")
print("Total rows:", df.shape[0])
print(df["label"].value_counts())

 
#3.Build feature matrix X and target Y
missing = [c for c in NOT_FEATURES if c not in df.columns]
if missing:
    print(f"\nWARNING: these expected drop-columns were not in the CSV: {missing}")
    print("Continuing with the columns that do exist.")

drop_cols = [c for c in NOT_FEATURES if c in df.columns]
X = df.drop(columns=drop_cols)
Y = df["label"]

print("\nDropped columns:", drop_cols)
print("Number of features after drops:", X.shape[1])
print("Feature columns:")
print(list(X.columns))

# 4. Group split by registrable domain  (fixes leakage)
# because before data with the same domain / campaign appeared in both train and test, so the model memorizes instead of learning.
# THIS guarantees that every domain is entirely in train OR entirely in test.
def registrable_domain(url):
    e = tldextract.extract(str(url))
    return f"{e.domain}.{e.suffix}".lower()

groups = df["url"].apply(registrable_domain)

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
train_idx, test_idx = next(gss.split(df, groups=groups))

# index into df to keep X / Y / groups aligned
x_train, x_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = Y.iloc[train_idx], Y.iloc[test_idx]
groups_train, groups_test = groups.iloc[train_idx], groups.iloc[test_idx]

print("\nGroup split (by registrable domain):")
print(f"Train rows: {len(x_train)}  |  Test rows: {len(x_test)}")
print("Train label counts:", y_train.value_counts().to_dict())
print("Test  label counts:", y_test.value_counts().to_dict())

# sanity: no domain in both splits
overlap = set(groups_train) & set(groups_test)
print("Domains present in BOTH train and test:", len(overlap))
assert len(overlap) == 0, "Domain leakage between train and test!"

# 5. Handle class imbalance for XGBoost
scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
print("\nscale_pos_weight (for XGB):", round(scale_pos_weight, 4))


#6. Models

models_to_train = {
    "Logistic Regression": (
        logistic_regression.create_model,
        "logistic_regression.pkl"
    ),
    "Random Forest": (
        random_forest.create_model,
        "random_forest.pkl"
    ),
    "XGBoost": (
        lambda: xg_boost.create_model(scale_pos_weight),
        "xgboost.pkl"
    ),
}

os.makedirs("models", exist_ok=True)


#7. Scoring for cross-validation
# using needs_proba=True can silently produce NaN scores. Use response_method="predict_proba" instead.
scoring = {
    "accuracy":  make_scorer(accuracy_score),
    "precision": make_scorer(precision_score, zero_division=0),
    "recall":    make_scorer(recall_score),
    "f1":        make_scorer(f1_score),
    "pr_auc":    make_scorer(average_precision_score, response_method="predict_proba"),
    "roc_auc":   make_scorer(roc_auc_score,        response_method="predict_proba"),
}


# 8. Train + evaluate each model

summary = []

for name, (build_model, file_name) in models_to_train.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    # ---------- 8a. Single group-split evaluation ----------
    model = build_model()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    print("\nSingle group-split test set:")
    print(f"  Accuracy : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"  Recall   : {recall_score(y_test, y_pred):.4f}")
    print(f"  F1       : {f1_score(y_test, y_pred):.4f}")
    print(f"  PR-AUC   : {average_precision_score(y_test, y_proba):.4f}")
    print(f"  ROC-AUC  : {roc_auc_score(y_test, y_proba):.4f}")
    print(f"  Confusion matrix  [[TN {tn}, FP {fp}], [FN {fn}, TP {tp}]]")

    # ---------- 8b. Stratified GROUP K-fold CV ----------
    # Group-aware CV: every fold holds out entire domains.
    cv_splitter = StratifiedGroupKFold(
        n_splits=5, shuffle=True, random_state=RANDOM_STATE
    )

    cv_results = cross_validate(
        build_model(),
        X, Y,
        cv=cv_splitter,
        groups=groups,
        scoring=scoring,
        n_jobs=-1,
        return_train_score=False,
    )

    print("\n5-fold StratifiedGroupKFold CV (mean):")
    for key in ["accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc"]:
        vals = cv_results.get("test_" + key)
        if vals is None:
            print(f"  {key:10s}: MISSING (not in cv_results)")
            continue
        mean_val = pd.Series(vals).mean()
        if pd.isna(mean_val):
            print(f"  {key:10s}: NaN  <-- this scorer failed; check make_scorer config")
        else:
            print(f"  {key:10s}: {mean_val:.4f}")

    summary.append({
        "Model": name,
        "Accuracy":  round(float(pd.Series(cv_results["test_accuracy"]).mean()), 4),
        "Precision": round(float(pd.Series(cv_results["test_precision"]).mean()), 4),
        "Recall":    round(float(pd.Series(cv_results["test_recall"]).mean()), 4),
        "F1":        round(float(pd.Series(cv_results["test_f1"]).mean()), 4),
        "PR_AUC":    round(float(pd.Series(cv_results["test_pr_auc"]).mean()), 4),
        "ROC_AUC":   round(float(pd.Series(cv_results["test_roc_auc"]).mean()), 4),
        "Split":     "grouped_by_domain",
    })

    # ---------- 8c. Save the model trained on TRAIN ONLY ----------
    joblib.dump(model, os.path.join("models", file_name))
    print(f"\nSaved to models/{file_name} (trained on {len(x_train)} rows)")


# 9. Save feature order + summary + best model name

joblib.dump(list(X.columns), os.path.join("models", "feature_columns.pkl"))

summary_df = pd.DataFrame(summary).set_index("Model")

print("\n" + "=" * 60)
print("Summary (5-fold StratifiedGroupKFold CV, mean)")
print("=" * 60)
print(summary_df.to_string())

print("\nSummary dtypes (should be float, no NaN):")
print(summary_df.dtypes)
print("\nAny NaN in summary?", summary_df.isna().any().to_dict())

summary_df.to_csv("results_summary.csv")
print("\nWrote results_summary.csv")

# Pick by PR-AUC (right metric under class imbalance), fall back to F1
if summary_df["PR_AUC"].notna().any():
    pick_col = "PR_AUC"
elif summary_df["F1"].notna().any():
    pick_col = "F1"
else:
    raise RuntimeError(
        "Neither PR_AUC nor F1 computed. Check make_scorer config and "
        "the per-fold scoring output above."
    )

best_model_name = summary_df[pick_col].idxmax()
joblib.dump(best_model_name, os.path.join("models", "best_model_name.pkl"))
print(f"\nBest model by {pick_col}: {best_model_name}")