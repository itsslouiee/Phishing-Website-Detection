import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split

import logistic_regression
import random_forest
import xg_boost
from evaluation import evaluate_model
from cross_validation import cross_validate

# 1. Load dataset
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
])

print("\nAfter removing duplicate website records:")
print("Total rows:", df.shape[0])
print(df["label"].value_counts())

# 3. Separate features (X) and target (Y)
# url and serial_number are identifiers, not features
X = df.drop(["url", "serial_number", "label"], axis=1)
Y = df["label"]

print("\nNumber of features:", X.shape[1])

# 4. Split into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    X,
    Y,
    test_size=0.2,
    random_state=10,
    stratify=Y
)

# XGBoost needs to know how imbalanced the classes are
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

# 5. The models we want to train
# name -> (function that builds a fresh model, file name for the .pkl)
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

summary = []

for name, (build_model, file_name) in models_to_train.items():

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    # 6. Single train/test split evaluation
    model = build_model()
    model.fit(x_train, y_train)

    print("\nSingle split:")
    evaluate_model(model, x_test, y_test)

    # 7. Stratified 5-fold cross-validation (see cross_validation.py)
    cv = cross_validate(build_model, X, Y, k=5)

    print("\n5-Fold Cross-Validation (mean):")
    print("Accuracy: ", round(cv["Accuracy"], 4))
    print("Precision:", round(cv["Precision"], 4))
    print("Recall:   ", round(cv["Recall"], 4))
    print("F1-Score: ", round(cv["F1"], 4))

    summary.append({"Model": name, **cv})

    # 8. Train the final model on ALL the data and save it
    final_model = build_model()
    final_model.fit(X, Y)

    joblib.dump(final_model, os.path.join("models", file_name))
    print(f"\nSaved to models/{file_name}")

# 9. Save the feature column order (the app needs it) and the best model
joblib.dump(list(X.columns), os.path.join("models", "feature_columns.pkl"))

summary_df = pd.DataFrame(summary).set_index("Model")
print("\n" + "=" * 50)
print("Summary (5-fold cross-validation)")
print("=" * 50)
print(summary_df.round(4))

# Save the summary table to a CSV file
summary_df.round(4).to_csv("results_summary.csv")

best_model_name = summary_df["F1"].idxmax()
joblib.dump(best_model_name, os.path.join("models", "best_model_name.pkl"))
print("\nBest model by F1-score:", best_model_name)