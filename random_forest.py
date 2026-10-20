from sklearn.ensemble import RandomForestClassifier


def create_model():
    model = RandomForestClassifier(
        n_estimators=100,       # number of trees
        class_weight="balanced",
        n_jobs=-1,              # use all CPU cores
        random_state=10
    )
    return model