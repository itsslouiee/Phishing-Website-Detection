import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn import svm, tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

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

# ---------------------------------------------------------
# Single train/test split evaluation (SVM only, as before)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# K-fold cross validation (stratified, so every fold has
# a proportional mix of both classes -- avoids the
# "only one class in training data" crash)
# ---------------------------------------------------------
K = 5
skf = StratifiedKFold(n_splits=K, shuffle=True, random_state=10)

svm_accuracy_list, svm_precision_list, svm_recall_list = [], [], []
rf_accuracy_list, rf_precision_list, rf_recall_list = [], [], []
dt_accuracy_list, dt_precision_list, dt_recall_list = [], [], []
ab_accuracy_list, ab_precision_list, ab_recall_list = [], [], []
nb_accuracy_list, nb_precision_list, nb_recall_list = [], [], []


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