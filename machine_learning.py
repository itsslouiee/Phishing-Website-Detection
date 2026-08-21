import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn import svm, tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

#read csv file and create pandas dataframe
legitimate_df = pd.read_csv("dataset/structured_legitimate_data.csv")
phishing_df = pd.read_csv("dataset/structured_phishing_data.csv")

#combine the dataframes and shuffle
combined_df = pd.concat([legitimate_df, phishing_df], axis=0)
combined_df = combined_df.sample(frac=1)

#remove the URL column and duplicates
combined_df = combined_df.drop('URL', axis=1)
combined_df = combined_df.drop_duplicates()

#create x and y
X = combined_df.drop('label', axis=1) #input
Y = combined_df['label'] # output

#splitting the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(X, Y,test_size=0.2, random_state=10)

#creating ML model using sklearn
svm_model = svm.LinearSVC()

#training the model
svm_model.fit(x_train, y_train)

#making predictions using the test data
predictions = svm_model.predict(x_test)

#creating the confusion matrix and classification report
tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
print("True Positives: ", tp)
print("True Negatives: ", tn)
print("False Positives: ", fp)
print("False Negatives: ", fn)

#accuracy, precision, and recall calculations
accuracy = (tp + tn) / (tp + tn + fp + fn)
precision = tp / (tp + fp)
recall = tp / (tp + fn) 

print("Accuracy: ", accuracy)
print("Precision: ", precision)
print("Recall: ", recall)

