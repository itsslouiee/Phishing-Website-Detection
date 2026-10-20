from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


def cross_validate(build_model, X, Y, k=5):
    """
    Stratified k-fold cross-validation.
    build_model: a function that returns a fresh, untrained model
    Returns the mean accuracy, precision, recall and F1 over the k folds.
    """
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=10)

    accuracy_list, precision_list, recall_list, f1_list = [], [], [], []

    for train_index, test_index in skf.split(X, Y):
        X_train_fold = X.iloc[train_index]
        X_test_fold = X.iloc[test_index]
        Y_train_fold = Y.iloc[train_index]
        Y_test_fold = Y.iloc[test_index]

        model = build_model()   # fresh model for every fold
        model.fit(X_train_fold, Y_train_fold)
        predictions = model.predict(X_test_fold)

        accuracy_list.append(accuracy_score(Y_test_fold, predictions))
        precision_list.append(precision_score(Y_test_fold, predictions, zero_division=0))
        recall_list.append(recall_score(Y_test_fold, predictions, zero_division=0))
        f1_list.append(f1_score(Y_test_fold, predictions, zero_division=0))

    return {
        "Accuracy": sum(accuracy_list) / k,
        "Precision": sum(precision_list) / k,
        "Recall": sum(recall_list) / k,
        "F1": sum(f1_list) / k,
    }