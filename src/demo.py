"""Live demo: estimate the resale price of a collectible.
Example:
  python src/demo.py --product_type trading_card --franchise pokemon --condition mint --rarity ultra_rare --age_years 25 --edition_size 5000 --search_volume 2000 --graded 1
"""
import argparse, os, sys
import numpy as np, pandas as pd
from sklearn.base import clone
sys.path.insert(0, os.path.dirname(__file__))
from features import load
from models import zoo

p = argparse.ArgumentParser()
p.add_argument("--data", default="data/collectibles_synthetic.csv")
p.add_argument("--product_type", default="trading_card"); p.add_argument("--franchise", default="pokemon")
p.add_argument("--condition", default="near_mint"); p.add_argument("--rarity", default="rare")
p.add_argument("--age_years", type=float, default=10); p.add_argument("--edition_size", type=int, default=10000)
p.add_argument("--search_volume", type=int, default=500)
p.add_argument("--graded", type=int, default=0); p.add_argument("--original_packaging", type=int, default=1)
a = vars(p.parse_args()); data = a.pop("data")
X, y = load(data); item = pd.DataFrame([a])[X.columns]
print("Item:", {k: v for k, v in a.items()})
for name in ["Ridge", "Gradient Boosting", "Random Forest"]:
    m = clone(zoo()[name]).fit(X, y)
    print(f"  {name:18s} -> ${m.predict(item)[0]:,.0f}")
print("(typical error of the best model: about +/-30% median; synthetic training data)")
