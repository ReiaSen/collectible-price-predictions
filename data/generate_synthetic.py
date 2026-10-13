"""Generate a SYNTHETIC collectible-merchandise resale dataset (1,200 items).

No licensed real-market dataset was available, so prices are produced from a
latent log-linear model with interactions and noise. Features mimic what a
marketplace listing exposes. NOT real market data: replace with a real CSV that
has the same columns to reproduce on real data (see README).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(30)
N = 1200

TYPES = {            # name: (share, base log-price)
    "trading_card": (0.28, 3.2), "vinyl_figure": (0.20, 3.1), "action_figure": (0.17, 3.4),
    "comic_book": (0.13, 3.0), "lego_set": (0.10, 4.1), "memorabilia": (0.12, 3.8)}
FRANCHISES = {"pokemon": 0.35, "marvel": 0.20, "star_wars": 0.30, "anime": 0.15, "disney": 0.05,
              "sports": 0.20, "harry_potter": 0.10, "dc": 0.10, "other": -0.20}
CONDITION = ["fair", "good", "near_mint", "mint"]
RARITY = ["common", "uncommon", "rare", "ultra_rare"]


def build():
    t = rng.choice(list(TYPES), N, p=[v[0] for v in TYPES.values()])
    fr = rng.choice(list(FRANCHISES), N, p=[0.17, 0.15, 0.12, 0.12, 0.10, 0.10, 0.08, 0.08, 0.08])
    cond = rng.choice(CONDITION, N, p=[0.10, 0.25, 0.40, 0.25])
    rar = rng.choice(RARITY, N, p=[0.45, 0.28, 0.19, 0.08])
    age = rng.gamma(2.2, 5.0, N).clip(0, 45).round(1)
    edition = np.exp(rng.normal(8.0, 1.6, N)).clip(50, 2_000_000).round(0)
    search = np.exp(rng.normal(6.0, 1.4, N)).round(0)
    graded = rng.binomial(1, np.where(np.isin(cond, ["near_mint", "mint"]), 0.30, 0.04))
    boxed = rng.binomial(1, 0.55, N)

    c = np.array([CONDITION.index(x) for x in cond]); r = np.array([RARITY.index(x) for x in rar])
    z = lambda v: (np.log(v) - np.log(v).mean()) / np.log(v).std()
    latent = (np.array([TYPES[x][1] for x in t]) + np.array([FRANCHISES[x] for x in fr])
              + 0.22 * c + 0.45 * r
              + 0.07 * c * r                                  # condition matters more for rare items
              - 0.30 * z(edition)                             # smaller print runs are pricier
              + 0.20 * z(search)
              + 0.025 * age * (1 + 0.4 * r)                   # vintage premium, stronger for rare items
              + 0.40 * graded + 0.18 * boxed)
    noise = rng.normal(0, 0.42, N) + rng.binomial(1, 0.04, N) * rng.exponential(0.9, N)  # occasional "grail" outliers
    price = np.exp(latent + noise).round(2).clip(3, None)
    return pd.DataFrame(dict(product_type=t, franchise=fr, condition=cond, rarity=rar, age_years=age, edition_size=edition.astype(int),
                             search_volume=search.astype(int), graded=graded, original_packaging=boxed, price=price))


if __name__ == "__main__":
    df = build(); df.to_csv("data/collectibles_synthetic.csv", index=False)
    print(df.shape); print(df.price.describe().round(1))
