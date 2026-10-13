"""Model zoo. Every regressor predicts log(price) and is mapped back to dollars."""
import numpy as np
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import BaggingRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from features import preprocessor

SEED = 30


def wrap(est, scale=True):
    return TransformedTargetRegressor(make_pipeline(preprocessor(scale), est), func=np.log, inverse_func=np.exp)


def zoo():
    return {
        "Median baseline": wrap(DummyRegressor(strategy="median")),
        "Linear Regression": wrap(LinearRegression()),
        "Ridge": wrap(Ridge(alpha=3.0)),
        "kNN (k=10)": wrap(KNeighborsRegressor(10, weights="distance")),
        "SVR (RBF)": wrap(SVR(C=3.0, epsilon=0.05, gamma="scale")),
        "Decision Tree": wrap(DecisionTreeRegressor(min_samples_leaf=5, random_state=SEED), scale=False),
        "Bagged Trees": wrap(BaggingRegressor(DecisionTreeRegressor(min_samples_leaf=3), n_estimators=100, random_state=SEED), scale=False),
        "Random Forest": wrap(RandomForestRegressor(300, min_samples_leaf=2, random_state=SEED, n_jobs=-1), scale=False),
        "Gradient Boosting": wrap(GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, random_state=SEED), scale=False),
    }
