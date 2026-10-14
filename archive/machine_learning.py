import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn import svm, tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from xgboost import XGBClassifier

# read csv file and create pandas dataframe
legitimate_df = pd.read_csv("dataset/structured_legitimate_data.csv")
phishing_df = pd.read_csv("dataset/structured_phishing_data.csv")

print("Original dataset:")
print("Legitimate rows:", legitimate_df.shape[0])
print("Phishing rows:", phishing_df.shape[0])

# combine the dataframes and shuffle
combined_df = pd.concat(
    [legitimate_df, phishing_df],
    axis=0,
    ignore_index=True
)
combined_df = combined_df.sample(frac=1, random_state=10).reset_index(drop=True)

print("\nAfter combining:")
print("Total rows:", combined_df.shape[0])

# remove duplicates
combined_df = combined_df.drop_duplicates()
print("\nAfter removing exact duplicate rows:")
print("Total rows:", combined_df.shape[0])
print("\nClass distribution:")
print(combined_df["label"].value_counts())

# create x and y
# URL is not used as a feature
X = combined_df.drop(["URL", "label"], axis=1)

# label: 0 = legitimate and 1 = phishing
Y = combined_df["label"]

# used by XGBoost to handle class imbalance:
# ratio of negative (legitimate) to positive (phishing) samples
n_legitimate = (Y == 0).sum()
n_phishing = (Y == 1).sum()
scale_pos_weight = n_legitimate / n_phishing

# splitting the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.2, random_state=10, stratify=Y
)

# creating ML models using sklearn
svm_model = svm.LinearSVC(class_weight='balanced', random_state=10)
rf_model = RandomForestClassifier(n_estimators=60, random_state=10)
dt_model = tree.DecisionTreeClassifier(random_state=10)
ab_model = AdaBoostClassifier(random_state=10)
nb_model = GaussianNB()
lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=10)
xgb_model = XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    eval_metric='logloss',
    random_state=10
)

# Single train/test split evaluation for SVM only 
svm_model.fit(x_train, y_train)
predictions = svm_model.predict(x_test)

tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
print("\n--- Single split (SVM) ---")
print("True Positives: ", tp)
print("True Negatives: ", tn)
print("False Positives: ", fp)
print("False Negatives: ", fn)

accuracy = (tp + tn) / (tp + tn + fp + fn)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = (
    2 * (precision * recall) / (precision + recall)
    if (precision + recall) > 0
    else 0
)
print("Accuracy: ", accuracy)
print("Precision: ", precision)
print("Recall: ", recall)
print("F1-Score: ", f1)

# K-fold cross validation (every fold has a proportional mix of both classes)
K = 5
skf = StratifiedKFold(n_splits=K, shuffle=True, random_state=10)

svm_accuracy_list, svm_precision_list, svm_recall_list = [], [], []
rf_accuracy_list, rf_precision_list, rf_recall_list = [], [], []
dt_accuracy_list, dt_precision_list, dt_recall_list = [], [], []
ab_accuracy_list, ab_precision_list, ab_recall_list = [], [], []
nb_accuracy_list, nb_precision_list, nb_recall_list = [], [], []
lr_accuracy_list, lr_precision_list, lr_recall_list = [], [], []
xgb_accuracy_list, xgb_precision_list, xgb_recall_list = [], [], []


def calculate_measures(TN, TP, FN, FP):
    model_accuracy = (TP + TN) / (TP + TN + FN + FP)
    model_precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    model_recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    return model_accuracy, model_precision, model_recall


for train_index, test_index in skf.split(X, Y):
    X_train_fold, X_test_fold = X.iloc[train_index], X.iloc[test_index]
    Y_train_fold, Y_test_fold = Y.iloc[train_index], Y.iloc[test_index]

    # ----- SUPPORT VECTOR MACHINE ----- #
    svm_model.fit(X_train_fold, Y_train_fold)
    svm_predictions = svm_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, svm_predictions).ravel()
    svm_accuracy, svm_precision, svm_recall = calculate_measures(tn, tp, fn, fp)
    svm_accuracy_list.append(svm_accuracy)
    svm_precision_list.append(svm_precision)
    svm_recall_list.append(svm_recall)

    # ----- RANDOM FOREST ----- #
    rf_model.fit(X_train_fold, Y_train_fold)
    rf_predictions = rf_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, rf_predictions).ravel()
    rf_accuracy, rf_precision, rf_recall = calculate_measures(tn, tp, fn, fp)
    rf_accuracy_list.append(rf_accuracy)
    rf_precision_list.append(rf_precision)
    rf_recall_list.append(rf_recall)

    # ----- DECISION TREE ----- #
    dt_model.fit(X_train_fold, Y_train_fold)
    dt_predictions = dt_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, dt_predictions).ravel()
    dt_accuracy, dt_precision, dt_recall = calculate_measures(tn, tp, fn, fp)
    dt_accuracy_list.append(dt_accuracy)
    dt_precision_list.append(dt_precision)
    dt_recall_list.append(dt_recall)

    # ----- ADABOOST ----- #
    ab_model.fit(X_train_fold, Y_train_fold)
    ab_predictions = ab_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, ab_predictions).ravel()
    ab_accuracy, ab_precision, ab_recall = calculate_measures(tn, tp, fn, fp)
    ab_accuracy_list.append(ab_accuracy)
    ab_precision_list.append(ab_precision)
    ab_recall_list.append(ab_recall)

    # ----- GAUSSIAN NAIVE BAYES ----- #
    nb_model.fit(X_train_fold, Y_train_fold)
    nb_predictions = nb_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, nb_predictions).ravel()
    nb_accuracy, nb_precision, nb_recall = calculate_measures(tn, tp, fn, fp)
    nb_accuracy_list.append(nb_accuracy)
    nb_precision_list.append(nb_precision)
    nb_recall_list.append(nb_recall)

    # ----- LOGISTIC REGRESSION (own addition) ----- #
    lr_model.fit(X_train_fold, Y_train_fold)
    lr_predictions = lr_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, lr_predictions).ravel()
    lr_accuracy, lr_precision, lr_recall = calculate_measures(tn, tp, fn, fp)
    lr_accuracy_list.append(lr_accuracy)
    lr_precision_list.append(lr_precision)
    lr_recall_list.append(lr_recall)

    # ----- XGBOOST (own addition) ----- #
    xgb_model.fit(X_train_fold, Y_train_fold)
    xgb_predictions = xgb_model.predict(X_test_fold)
    tn, fp, fn, tp = confusion_matrix(Y_test_fold, xgb_predictions).ravel()
    xgb_accuracy, xgb_precision, xgb_recall = calculate_measures(tn, tp, fn, fp)
    xgb_accuracy_list.append(xgb_accuracy)
    xgb_precision_list.append(xgb_precision)
    xgb_recall_list.append(xgb_recall)


print("\n--- 5-Fold Cross Validation Results ---")

SVM_accuracy = sum(svm_accuracy_list) / len(svm_accuracy_list)
SVM_precision = sum(svm_precision_list) / len(svm_precision_list)
SVM_recall = sum(svm_recall_list) / len(svm_recall_list)
print("Support Vector Machine accuracy ==> ", SVM_accuracy)
print("Support Vector Machine precision ==> ", SVM_precision)
print("Support Vector Machine recall ==> ", SVM_recall)

RF_accuracy = sum(rf_accuracy_list) / len(rf_accuracy_list)
RF_precision = sum(rf_precision_list) / len(rf_precision_list)
RF_recall = sum(rf_recall_list) / len(rf_recall_list)
print("Random Forest accuracy ==> ", RF_accuracy)
print("Random Forest precision ==> ", RF_precision)
print("Random Forest recall ==> ", RF_recall)

DT_accuracy = sum(dt_accuracy_list) / len(dt_accuracy_list)
DT_precision = sum(dt_precision_list) / len(dt_precision_list)
DT_recall = sum(dt_recall_list) / len(dt_recall_list)
print("Decision Tree accuracy ==> ", DT_accuracy)
print("Decision Tree precision ==> ", DT_precision)
print("Decision Tree recall ==> ", DT_recall)

AB_accuracy = sum(ab_accuracy_list) / len(ab_accuracy_list)
AB_precision = sum(ab_precision_list) / len(ab_precision_list)
AB_recall = sum(ab_recall_list) / len(ab_recall_list)
print("AdaBoost accuracy ==> ", AB_accuracy)
print("AdaBoost precision ==> ", AB_precision)
print("AdaBoost recall ==> ", AB_recall)

NB_accuracy = sum(nb_accuracy_list) / len(nb_accuracy_list)
NB_precision = sum(nb_precision_list) / len(nb_precision_list)
NB_recall = sum(nb_recall_list) / len(nb_recall_list)
print("Gaussian Naive Bayes accuracy ==> ", NB_accuracy)
print("Gaussian Naive Bayes precision ==> ", NB_precision)
print("Gaussian Naive Bayes recall ==> ", NB_recall)

LR_accuracy = sum(lr_accuracy_list) / len(lr_accuracy_list)
LR_precision = sum(lr_precision_list) / len(lr_precision_list)
LR_recall = sum(lr_recall_list) / len(lr_recall_list)
print("Logistic Regression accuracy ==> ", LR_accuracy)
print("Logistic Regression precision ==> ", LR_precision)
print("Logistic Regression recall ==> ", LR_recall)

XGB_accuracy = sum(xgb_accuracy_list) / len(xgb_accuracy_list)
XGB_precision = sum(xgb_precision_list) / len(xgb_precision_list)
XGB_recall = sum(xgb_recall_list) / len(xgb_recall_list)
print("XGBoost accuracy ==> ", XGB_accuracy)
print("XGBoost precision ==> ", XGB_precision)
print("XGBoost recall ==> ", XGB_recall)


# Results comparison table + bar chart
data = {
    'accuracy': [NB_accuracy, SVM_accuracy, DT_accuracy, RF_accuracy, AB_accuracy, LR_accuracy, XGB_accuracy],
    'precision': [NB_precision, SVM_precision, DT_precision, RF_precision, AB_precision, LR_precision, XGB_precision],
    'recall': [NB_recall, SVM_recall, DT_recall, RF_recall, AB_recall, LR_recall, XGB_recall],
}

index = ['NB', 'SVM', 'DT', 'RF', 'AB', 'LR', 'XGB']

df_results = pd.DataFrame(data=data, index=index)
print("\n--- Results Summary ---")
print(df_results)

# visualize the dataframe
# ax = df_results.plot.bar(rot=0)
plt.title("Model Comparison — 5-Fold Cross Validation")
plt.ylabel("Score")
# plt.tight_layout()
# plt.savefig("model_comparison.png")
# plt.show()

# ---------------------------------------------------------
#using all models in streamlit app
import joblib
 
all_models = {
    "Naive Bayes": nb_model,
    "SVM": svm_model,
    "Decision Tree": dt_model,
    "Random Forest": rf_model,
    "AdaBoost": ab_model,
    "Logistic Regression": lr_model,
    "XGBoost": xgb_model,
}
 
# retrain every model on the FULL dataset (not just one fold) before saving
for name, m in all_models.items():
    m.fit(X, Y)
 
joblib.dump(all_models, "all_models.pkl")
joblib.dump(list(X.columns), "feature_columns.pkl")
 
# also record which model performed best in cross-validation,
# based on recall (most important metric for a security tool)
cv_recall_scores = {
    "Naive Bayes": NB_recall,
    "SVM": SVM_recall,
    "Decision Tree": DT_recall,
    "Random Forest": RF_recall,
    "AdaBoost": AB_recall,
    "Logistic Regression": LR_recall,
    "XGBoost": XGB_recall,
}
best_model_name = max(cv_recall_scores, key=cv_recall_scores.get)
joblib.dump(best_model_name, "best_model_name.pkl")
 
print(f"\nAll 7 models saved to all_models.pkl")
print(f"Feature column order saved to feature_columns.pkl")
print(f"Best model by recall: {best_model_name} ({cv_recall_scores[best_model_name]:.3f})")