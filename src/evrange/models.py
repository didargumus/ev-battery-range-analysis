r"""What makes an EV efficient? Explanatory regression and a predictive model.

Target: consumption (kWh per 100 miles). Range itself is mostly a choice of
battery size, which EPA does not report consistently, so the models explain
the part of range that engineering controls: how much energy a mile costs.

1. **Explanatory OLS** on log consumption with heteroskedasticity-robust (HC3)
   standard errors. Because the target is in logs, a coefficient *b* means
   consumption changes by about ``100 * (exp(b) - 1)`` percent.
2. **Make effects**: the same regression with manufacturer dummies gives
   each make's consumption for an identical reference vehicle, i.e. brand
   efficiency after controlling for size, drivetrain, power and year.
3. **Predictive comparison** of a class-median baseline, OLS and gradient
   boosting, scored with *grouped* cross-validation: every trim and model year
   of a model line stays in the same fold. Ordinary K-fold would put the 2023
   and 2024 versions of the same car in train and test and overstate accuracy.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

__all__ = ["FEATURES", "prepare_features", "explanatory_ols", "ols_effects_table", "make_effects", "cross_validate_models",
           "permutation_importances"]

FEATURES = ["year", "vehicle_class", "awd", "log_motor_kw", "make_grouped"]
NUMERIC = ["year", "log_motor_kw"]
CATEGORICAL = ["vehicle_class", "awd", "make_grouped"]


def prepare_features(ev: pd.DataFrame, min_make_count: int = 5) -> pd.DataFrame:
    """Model-ready frame: rows with a parsed motor power, rare makes pooled into "Other"."""
    d = ev.dropna(subset=["motor_kw"]).copy()
    d = d[d["motor_kw"] > 0]
    counts = d["make"].value_counts()
    d["make_grouped"] = d["make"].where(d["make"].map(counts) >= min_make_count, "Other")
    d["log_motor_kw"] = np.log(d["motor_kw"])
    d["log_consumption"] = np.log(d["consumption"])
    d["awd"] = d["awd"].astype(int)
    return d.reset_index(drop=True)


def explanatory_ols(d: pd.DataFrame):
    """log(consumption) ~ year + class + AWD + log(motor kW), HC3 standard errors."""
    formula = "log_consumption ~ year + C(vehicle_class, Treatment('Car')) + awd + log_motor_kw"
    return smf.ols(formula, data=d).fit(cov_type="HC3")


def ols_effects_table(fit) -> pd.DataFrame:
    """Coefficients as percentage effects on consumption with 95% CIs."""
    ci = fit.conf_int()
    rows = []
    for name in fit.params.index:
        if name == "Intercept":
            continue
        b, lo, hi = fit.params[name], ci.loc[name, 0], ci.loc[name, 1]
        label = (name.replace("C(vehicle_class, Treatment('Car'))[T.", "Class: ").replace("]", " (vs car)")
                 .replace("awd", "All-wheel drive").replace("log_motor_kw", "Motor power (+10%)")
                 .replace("year", "Model year (+1)"))
        scale = np.log(1.1) if name == "log_motor_kw" else 1.0          # elasticity -> +10% power
        rows.append({"term": label, "effect_pct": 100 * (np.exp(b * scale) - 1),
                     "ci_low_pct": 100 * (np.exp(lo * scale) - 1), "ci_high_pct": 100 * (np.exp(hi * scale) - 1),
                     "p_value": fit.pvalues[name]})
    return pd.DataFrame(rows).set_index("term")


def make_effects(d: pd.DataFrame, reference: dict | None = None) -> pd.DataFrame:
    """Predicted consumption of the same reference vehicle for each make, with 95% CIs.

    Reference vehicle: the most common class and drivetrain in the latest
    model year, with that year's median motor power. Makes pooled as "Other"
    are excluded. Returns the table and the reference used.
    """
    formula = ("log_consumption ~ year + C(vehicle_class, Treatment('Car')) + awd + log_motor_kw"
               " + C(make_grouped)")
    fit = smf.ols(formula, data=d).fit(cov_type="HC3")
    if reference is None:
        latest = d[d["year"] == d["year"].max()]
        reference = {"year": int(latest["year"].iloc[0]),
                     "vehicle_class": latest["vehicle_class"].mode().iloc[0],
                     "awd": int(latest["awd"].mode().iloc[0]),
                     "log_motor_kw": float(latest["log_motor_kw"].median())}
    ref = reference
    makes = sorted(m for m in d["make_grouped"].unique() if m != "Other")
    grid = pd.DataFrame([{**ref, "make_grouped": m} for m in makes])
    pred = fit.get_prediction(grid).summary_frame(alpha=0.05)
    out = pd.DataFrame({"make": makes, "consumption": np.exp(pred["mean"].values),
                        "ci_low": np.exp(pred["mean_ci_lower"].values), "ci_high": np.exp(pred["mean_ci_upper"].values),
                        "n": [int((d["make_grouped"] == m).sum()) for m in makes]})
    out = out.sort_values("consumption").reset_index(drop=True)
    out.attrs["reference"] = ref
    return out


def _models(random_state: int = 0) -> dict:
    ols = make_pipeline(
        ColumnTransformer([("num", "passthrough", NUMERIC),
                           ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORICAL)]),
        LinearRegression())
    gbm = make_pipeline(
        ColumnTransformer([("num", "passthrough", NUMERIC),
                           ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CATEGORICAL)]),
        HistGradientBoostingRegressor(categorical_features=[2, 3, 4], max_iter=300, learning_rate=0.05,
                                      max_leaf_nodes=15, min_samples_leaf=10, l2_regularization=1.0,
                                      random_state=random_state))
    return {"OLS (log scale)": ols, "Gradient boosting": gbm}


def cross_validate_models(d: pd.DataFrame, n_splits: int = 5, random_state: int = 0) -> pd.DataFrame:
    """Grouped K-fold comparison. Errors are reported in kWh/100 mi on the original scale."""
    X, y, groups = d[FEATURES], d["consumption"].to_numpy(), d["family"].to_numpy()
    n_splits = min(n_splits, len(np.unique(groups)))
    cv = GroupKFold(n_splits=n_splits)
    preds = {"Baseline: class median": np.empty(len(d))}
    for name in _models():
        preds[name] = np.empty(len(d))
    warnings.filterwarnings("ignore", message="Found unknown categories")   # a make absent from a training fold
    for tr, te in cv.split(X, y, groups):
        med = d.iloc[tr].groupby("vehicle_class")["consumption"].median()
        preds["Baseline: class median"][te] = d.iloc[te]["vehicle_class"].map(med).fillna(np.median(y[tr])).to_numpy()
        for name, model in _models(random_state).items():
            model.fit(X.iloc[tr], np.log(y[tr]))
            preds[name][te] = np.exp(model.predict(X.iloc[te]))
    rows = [{"model": k, "mae": mean_absolute_error(y, p), "mape_pct": 100 * np.mean(np.abs(p - y) / y),
             "r2": r2_score(y, p)} for k, p in preds.items()]
    return pd.DataFrame(rows).set_index("model")


def permutation_importances(d: pd.DataFrame, n_repeats: int = 20, random_state: int = 0) -> pd.DataFrame:
    """Permutation importance of the gradient-boosting model on held-out model lines.

    Fitted on 80% of model families and scored on the other 20%, so importance
    reflects generalisation to unseen cars, not memorisation.
    """
    fams = d["family"].unique()
    rng = np.random.default_rng(random_state)
    test_fams = set(rng.choice(fams, size=max(1, len(fams) // 5), replace=False))
    te = d["family"].isin(test_fams).to_numpy()
    model = _models(random_state)["Gradient boosting"]
    model.fit(d.loc[~te, FEATURES], d.loc[~te, "log_consumption"])
    res = permutation_importance(model, d.loc[te, FEATURES], d.loc[te, "log_consumption"],
                                 n_repeats=n_repeats, random_state=random_state, scoring="neg_mean_absolute_error")
    labels = {"year": "Model year", "vehicle_class": "Vehicle class", "awd": "All-wheel drive",
              "log_motor_kw": "Motor power", "make_grouped": "Manufacturer"}
    return (pd.DataFrame({"feature": [labels[f] for f in FEATURES], "importance": res.importances_mean,
                          "std": res.importances_std}).sort_values("importance", ascending=False)
            .reset_index(drop=True))
