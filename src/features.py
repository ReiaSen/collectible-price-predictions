"""Shared loading + preprocessing pipeline."""
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline

NOMINAL = ["product_type", "franchise"]
ORDINAL = {"condition": ["fair", "good", "near_mint", "mint"], "rarity": ["common", "uncommon", "rare", "ultra_rare"]}
LOGNUM = ["edition_size", "search_volume"]        # heavy-tailed -> log
PLAINNUM = ["age_years"]
BINARY = ["graded", "original_packaging"]
FEATURES = NOMINAL + list(ORDINAL) + LOGNUM + PLAINNUM + BINARY


def load(path="data/collectibles_synthetic.csv"):
    df = pd.read_csv(path)
    return df[FEATURES], df["price"].to_numpy()


def preprocessor(scale=True):
    """One-hot nominals, ordinal-encode ordered categoricals, log-transform heavy-tailed numerics."""
    num = [("log", FunctionTransformer(np.log1p))] + ([("sc", StandardScaler())] if scale else [])
    plain = [("sc", StandardScaler())] if scale else [("id", FunctionTransformer())]
    return ColumnTransformer([
        ("nom", OneHotEncoder(handle_unknown="ignore"), NOMINAL),
        ("ord", Pipeline([("o", OrdinalEncoder(categories=list(ORDINAL.values()), handle_unknown="use_encoded_value", unknown_value=-1))] +
                         ([("sc", StandardScaler())] if scale else [])), list(ORDINAL)),
        ("log", Pipeline(num), LOGNUM),
        ("num", Pipeline(plain), PLAINNUM),
        ("bin", "passthrough", BINARY)])
