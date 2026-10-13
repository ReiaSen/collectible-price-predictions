# Collectible Merchandise Price Prediction - a machine-learning case study

UE24CS352A Machine Learning mini-project - **Team 30, Problem 50**
Reia S (PES2UG24CS921) and Ritesh Babu Reddy (PES2UG24CS403)

Inspired by: Lu, *Application of Machine Learning Methods to Evaluate Collectibles*, Stanford CS229, 2021
(https://cs229.stanford.edu/proj2021spr/report2/81980743.pdf). That report classifies Funko Pop prices into bins;
we generalise to **regression over six collectible categories** (trading cards, vinyl figures, action figures,
comic books, LEGO sets, memorabilia) and predict the actual dollar price.

## Problem
Given a listing's attributes (product type, franchise, condition, rarity, age, edition size, search interest,
graded?, original packaging?), predict its resale price in USD. Prices are right-skewed, so models predict
`log(price)` and are mapped back to dollars.

## IMPORTANT: dataset
No licensed real-market dataset was available. `data/generate_synthetic.py` creates **1,200 synthetic listings** from a
latent log-linear price model with interactions, a vintage premium and heavy-tailed noise. Because the generator is
(mostly) log-linear, linear models have a built-in advantage; conclusions describe the methods on this data, **not the
real market**. To use real data, provide a CSV with columns
`product_type, franchise, condition, rarity, age_years, edition_size, search_volume, graded, original_packaging, price`
and run `python src/run_experiments.py path/to/data.csv`.

## Setup & run
```bash
pip install -r requirements.txt
python data/generate_synthetic.py       # -> data/collectibles_synthetic.csv
python src/run_experiments.py           # CV evaluation of 9 models -> results/metrics.json + figures
python src/demo.py --rarity ultra_rare --condition mint --graded 1 --age_years 25 --edition_size 5000 --search_volume 2000
```

## Layout
| Path | Purpose |
|---|---|
| `data/generate_synthetic.py` | synthetic dataset builder |
| `src/features.py` | preprocessing: one-hot, ordinal, log transforms, scaling (inside CV pipelines, no leakage) |
| `src/models.py` | median baseline, Linear, Ridge, kNN, SVR, Decision Tree, Bagged Trees, Random Forest, Gradient Boosting |
| `src/run_experiments.py` | 5-fold x3 CV, hold-out error-by-tier analysis, permutation importance, plots |
| `src/demo.py` | price estimate for a listing typed on the command line |
| `docs/` | write-up PDF, slides, and the scripts that generate them |

## Metrics
RMSE and R2 on log(price); MAE in USD; median absolute percentage error (MedAPE); share of predictions within 25% of the true price.
