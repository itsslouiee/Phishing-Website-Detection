import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
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
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=10, stratify=Y)

# creating ML model using sklearn
svm_model = svm.LinearSVC(class_weight='balanced', random_state=10)

# training the model
svm_model.fit(x_train, y_train)

# making predictions using the test data
predictions = svm_model.predict(x_test)

# creating the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
print("True Positives: ", tp)
print("True Negatives: ", tn)
print("False Positives: ", fp)
print("False Negatives: ", fn)

# accuracy, precision, recall, and f1 calculations
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

