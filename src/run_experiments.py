"""Evaluate all regressors with repeated K-fold CV, then permutation importance + plots."""
import json, os, sys, warnings
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, RepeatedKFold, cross_val_predict, train_test_split
from sklearn.inspection import permutation_importance
from sklearn.base import clone

sys.path.insert(0, os.path.dirname(__file__))
from features import load
from models import zoo, SEED

warnings.filterwarnings("ignore")
os.makedirs("results", exist_ok=True)
X, y = load(sys.argv[1] if len(sys.argv) > 1 else "data/collectibles_synthetic.csv")


def metrics(yt, yp):
    ly = np.log(yt) - np.log(yp)
    ape = np.abs(yp - yt) / yt
    return dict(rmse_log=float(np.sqrt(np.mean(ly ** 2))), r2_log=float(1 - np.sum(ly ** 2) / np.sum((np.log(yt) - np.log(yt).mean()) ** 2)),
                mae_usd=float(np.mean(np.abs(yp - yt))), medape=float(np.median(ape)), within25=float(np.mean(ape <= 0.25)))


cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=SEED)
R = {}
for name, est in zoo().items():
    tr, va = [], []
    for a, b in cv.split(X):
        m = clone(est).fit(X.iloc[a], y[a])
        tr.append(metrics(y[a], m.predict(X.iloc[a]))); va.append(metrics(y[b], m.predict(X.iloc[b])))
    R[name] = dict(train={k: float(np.mean([s[k] for s in tr])) for k in tr[0]}, valid={k: float(np.mean([s[k] for s in va])) for k in va[0]},
                   valid_std_rmse=float(np.std([s["rmse_log"] for s in va])))
    v = R[name]["valid"]
    print(f"{name:20s} RMSE(log)={v['rmse_log']:.3f}  R2(log)={v['r2_log']:.3f}  MAE=${v['mae_usd']:.0f}  MedAPE={v['medape']:.1%}  within25%={v['within25']:.1%}")

best = min(R, key=lambda n: R[n]["valid"]["rmse_log"])
print("best:", best)

# hold-out analysis for the best model: error by price tier, predicted vs actual, importance
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)
m = clone(zoo()[best]).fit(Xtr, ytr); pred = m.predict(Xte)
q = np.append(np.quantile(y, [0, .5, .9]), np.inf); tiers = ["bottom 50%", "50-90%", "top 10%"]
tier_err = {}
for i, t in enumerate(tiers):
    mk = (yte >= q[i]) & (yte < q[i + 1])
    tier_err[t] = dict(n=int(mk.sum()), medape=float(np.median(np.abs(pred[mk] - yte[mk]) / yte[mk])), bias_log=float(np.mean(np.log(pred[mk]) - np.log(yte[mk]))))
print("error by tier:", {k: (v['n'], round(v['medape'], 3), round(v['bias_log'], 3)) for k, v in tier_err.items()})
pi = permutation_importance(m, Xte, np.log(yte), n_repeats=15, random_state=SEED, scoring=lambda e, X_, y_: -np.sqrt(np.mean((np.log(e.predict(X_)) - y_) ** 2)))
imp = pd.Series(pi.importances_mean, index=X.columns).sort_values()

json.dump(dict(n=len(y), best=best, models=R, tier_error=tier_err, importance=imp.to_dict(), holdout=metrics(yte, pred)), open("results/metrics.json", "w"), indent=1)

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(9, 3.1))
ax[0].hist(y.clip(0, 1500), bins=60, color="#2b6cb0"); ax[0].set(title="Price (clipped at $1,500)", xlabel="USD", ylabel="items")
ax[1].hist(np.log10(y), bins=40, color="#2b6cb0"); ax[1].set(title="log10(price): near-normal", xlabel="log10 USD")
plt.tight_layout(); plt.savefig("results/data_overview.png", dpi=200); plt.close()

names = list(R); order = sorted(names, key=lambda n: -R[n]["valid"]["rmse_log"])
fig, ax = plt.subplots(figsize=(6.2, 3.4)); yy = np.arange(len(order))
ax.barh(yy + .2, [R[n]["train"]["rmse_log"] for n in order], .4, color="#a0aec0", label="train")
ax.barh(yy - .2, [R[n]["valid"]["rmse_log"] for n in order], .4, color="#2b6cb0", label="validation")
ax.set_yticks(yy); ax.set_yticklabels(order); ax.set_xlabel("RMSE on log(price)  (lower is better)"); ax.legend(); plt.tight_layout(); plt.savefig("results/model_comparison.png", dpi=200); plt.close()

fig, ax = plt.subplots(figsize=(3.9, 3.6))
ax.scatter(yte, pred, s=10, alpha=.6, color="#2b6cb0"); lim = [min(y.min(), pred.min()), max(y.max(), pred.max())]
ax.plot(lim, lim, "--", color="#dd6b20"); ax.set(xscale="log", yscale="log", xlabel="actual price (USD)", ylabel="predicted price (USD)", title=f"{best}: hold-out"); plt.tight_layout(); plt.savefig("results/pred_vs_actual.png", dpi=200); plt.close()

fig, ax = plt.subplots(figsize=(4.6, 3.4)); ax.barh(imp.index, imp.values, color="#2b6cb0"); ax.set(xlabel="RMSE(log) increase when shuffled", title="Permutation importance (hold-out)")
plt.tight_layout(); plt.savefig("results/feature_importance.png", dpi=200); plt.close()
