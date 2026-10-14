import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from logistic_regression import create_model
from evaluation import evaluate_model

# 1. Load dataset
df = pd.read_csv("data.csv")

print("Original dataset:")
print("Total rows:", df.shape[0])
print("Total columns:", df.shape[1])

print("\nClass distribution:")
print(df["label"].value_counts())

df = df.drop_duplicates(subset=["url"] + [
    col for col in df.columns
    if col not in ["serial_number", "url"]
])

print("\nAfter removing duplicate website records:")
print("Total rows:", df.shape[0])

print("\nClass distribution after removing duplicates:")
print(df["label"].value_counts())


# 3. Separate features and target
# URL and serial_number are identifiers, not model features
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

print("\nTraining samples:", x_train.shape[0])
print("Testing samples:", x_test.shape[0])

# 5. Create Logistic Regression model
lr_model = create_model()

# 6. Single train/test split evaluation
lr_model.fit(x_train, y_train)

print("\nSingle Split (Logistic Regression)")
evaluate_model(lr_model, x_test, y_test)

# 7. Stratified 5-fold cross-validation
K = 5

skf = StratifiedKFold(
    n_splits=K,
    shuffle=True,
    random_state=10
)

accuracy_list = []
precision_list = []
recall_list = []
f1_list = []

for fold, (train_index, test_index) in enumerate(
    skf.split(X, Y), start=1
):
    X_train_fold = X.iloc[train_index]
    X_test_fold = X.iloc[test_index]
    Y_train_fold = Y.iloc[train_index]
    Y_test_fold = Y.iloc[test_index]

    lr_model.fit(X_train_fold, Y_train_fold)
    fold_predictions = lr_model.predict(X_test_fold)

    accuracy_list.append(accuracy_score(Y_test_fold, fold_predictions))
    precision_list.append(
        precision_score(Y_test_fold, fold_predictions, zero_division=0)
    )
    recall_list.append(
        recall_score(Y_test_fold, fold_predictions, zero_division=0)
    )
    f1_list.append(f1_score(Y_test_fold, fold_predictions, zero_division=0))

    print(f"\nFold {fold}:")
    print("Accuracy:", round(accuracy_list[-1], 4))
    print("Precision:", round(precision_list[-1], 4))
    print("Recall:", round(recall_list[-1], 4))
    print("F1-Score:", round(f1_list[-1], 4))

print("\n5-Fold Cross-Validation Results")
print("Mean Accuracy:", round(sum(accuracy_list) / K, 4))
print("Mean Precision:", round(sum(precision_list) / K, 4))
print("Mean Recall:", round(sum(recall_list) / K, 4))
print("Mean F1-Score:", round(sum(f1_list) / K, 4))
