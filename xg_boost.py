from xgboost import XGBClassifier


def create_model(scale_pos_weight=1.0):
    # scale_pos_weight = (number of legitimate) / (number of phishing)
    # it tells XGBoost how much more to care about the minority class
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        n_jobs=-1,
        random_state=10
    )
    return model