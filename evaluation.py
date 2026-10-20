from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

def evaluate_model(model, x_test, y_test):
    predictions = model.predict(x_test)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision: {precision_score(y_test, predictions, pos_label=1, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, predictions, pos_label=1, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_test, predictions, pos_label=1, zero_division=0):.4f}")

    print("\nConfusion Matrix:")
    print(f"TN: {tn} | FP: {fp}")
    print(f"FN: {fn} | TP: {tp}")

    print("\nClassification Report:")
    print(classification_report(y_test, predictions, zero_division=0))
