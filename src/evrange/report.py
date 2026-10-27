"""Figures, the results page and the auto-generated part of the README.

Everything with a number in it is produced here from the data, so the README
can never drift from the analysis when GitHub Actions refreshes the data.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# categorical palette in fixed order (checked for colour-vision-deficiency separation)
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, GRID, SURF, MUTED = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#b9b8b2"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "legend.frameon": False, "lines.linewidth": 2, "figure.dpi": 130,
})

START, END = "<!-- results:start -->", "<!-- results:end -->"


def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- figures
def fig_range_trend(ev: pd.DataFrame, ys: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(9, 4.4))
    sub = ev[ev["year"].isin(ys.index)]
    jitter = np.random.default_rng(0).uniform(-0.25, 0.25, len(sub))
    ax.scatter(sub["year"] + jitter, sub["range"], s=9, color=MUTED, alpha=0.6, lw=0, label="One vehicle configuration")
    ax.fill_between(ys.index, ys["range_q25"], ys["range_q75"], color=C[0], alpha=0.18, lw=0, label="Middle 50%")
    ax.plot(ys.index, ys["range_median"], color=C[0], marker="o", ms=5, label="Median")
    ax.set_xlabel("Model year")
    ax.set_ylabel("EPA range (miles)")
    ax.set_title("EPA-rated range of battery-electric vehicles by model year", loc="left")
    ax.legend(loc="upper left")
    _save(fig, path)


def fig_decomposition(dec: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for col, color, label in [("range_index", C[0], "Range"), ("energy_index", C[1], "Energy per full charge"),
                              ("consumption_index", C[2], "Consumption (kWh per 100 mi)")]:
        ax.plot(dec.index, dec[col], color=color, marker="o", ms=4, label=label)
        ax.annotate(f"{dec[col].iloc[-1]:.0f}", (dec.index[-1], dec[col].iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK)
    ax.axhline(100, color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("Model year")
    ax.set_ylabel(f"Geometric mean, {dec.index[0]} = 100")
    ax.set_title("Range = energy per charge ÷ consumption: where the range gains came from", loc="left")
    ax.legend(loc="upper left")
    _save(fig, path)


def fig_city_highway(ev: pd.DataFrame, gas: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(9, 4))
    bins = np.linspace(0.5, 2.0, 61)
    ax.hist(gas["hwy_city_ratio"].clip(0.5, 2.0), bins=bins, density=True, color=C[1], alpha=0.55, label="Gasoline cars")
    ax.hist(ev["hwy_city_ratio"].clip(0.5, 2.0), bins=bins, density=True, color=C[0], alpha=0.7, label="Battery-electric")
    ax.axvline(1.0, color=INK, lw=1, ls="--")
    ax.text(1.01, ax.get_ylim()[1] * 0.92, "same efficiency\nin town and on highway", fontsize=8, color=INK2)
    ax.set_xlabel("Highway efficiency ÷ city efficiency")
    ax.set_ylabel("Density")
    ax.set_title("EVs are more efficient in town; combustion cars on the highway", loc="left")
    ax.legend(loc="upper right")
    _save(fig, path)


def fig_make_effects(me: pd.DataFrame, path: Path):
    me = me.sort_values("consumption", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 0.34 * len(me) + 1.4))
    y = np.arange(len(me))
    ax.errorbar(me["consumption"], y, xerr=[me["consumption"] - me["ci_low"], me["ci_high"] - me["consumption"]],
                fmt="o", color=C[0], ecolor=C[0], elinewidth=1.4, capsize=0, ms=6, mec=SURF, mew=1.5)
    ax.set_yticks(y, [f"{m} (n={n})" for m, n in zip(me["make"], me["n"])])
    ax.set_xlabel("Predicted consumption, kWh per 100 miles (lower is better)")
    ax.set_title(f"Manufacturer efficiency for one reference vehicle: {_ref_text(me)} (95% CI)", loc="left", fontsize=10)
    _save(fig, path)


def fig_models(cv: pd.DataFrame, imp: pd.DataFrame, path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    ax = axes[0]
    y = np.arange(len(cv))
    ax.barh(y, cv["mae"], height=0.55, color=[MUTED, C[0], C[1]][: len(cv)])
    for yi, v in zip(y, cv["mae"]):
        ax.text(v, yi, f" {v:.2f}", va="center", fontsize=9, color=INK)
    ax.set_yticks(y, cv.index)
    ax.invert_yaxis()
    ax.set_xlabel("Mean absolute error, kWh per 100 mi (grouped CV)")
    ax.set_title("Predicting consumption for unseen model lines", loc="left")
    ax = axes[1]
    y = np.arange(len(imp))
    ax.barh(y, imp["importance"], xerr=imp["std"], height=0.55, color=C[1], ecolor=INK2, capsize=0)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y, imp["feature"])
    ax.invert_yaxis()
    ax.set_xlabel("Increase in error when the feature is shuffled")
    ax.set_title("Permutation importance (gradient boosting)", loc="left")
    _save(fig, path)


# --------------------------------------------------------------------------- text
def _pct(x: float) -> str:
    return f"{x:+.0f}%"


def _ref_text(me: pd.DataFrame) -> str:
    ref = me.attrs.get("reference")
    if not ref:
        return "the reference vehicle"
    drive = "all-wheel-drive" if ref["awd"] else "two-wheel-drive"
    cls = {"SUV": "SUV", "Car": "car", "Pickup": "pickup", "Van": "van"}.get(ref["vehicle_class"], ref["vehicle_class"])
    return f"{drive} {cls}, {np.exp(ref['log_motor_kw']):.0f} kW, model year {ref['year']}"


def _next(lines: list[str]) -> int:
    """Number for the next item of the numbered findings list."""
    return sum(1 for line in lines if line.split(".", 1)[0].isdigit()) + 1


def _share(x: float) -> str:
    """Percentage that never rounds 99.6% up to 100% or 0.4% down to 0%."""
    if 0.995 <= x < 1 or 0 < x <= 0.005:
        return f"{x:.1%}"
    return f"{x:.0%}"


def findings_markdown(h: dict, ols_tab: pd.DataFrame, me: pd.DataFrame, cv: pd.DataFrame, vintage: str) -> str:
    """Findings written from the numbers. Wording adapts to the sign of each effect."""
    lines = []
    lines.append(
        f"Data: {h['n_vehicles']:,} battery-electric vehicle configurations from {h['n_makes']} manufacturers, "
        f"model years {h['year_min']} to {h['year_max']} (EPA file obtained {vintage}). Trend figures use model "
        f"years with at least 10 configurations ({h['first_year']} to {h['last_year']}).")
    lines.append("")
    e, c = h["energy_change_pct"], h["consumption_change_pct"]
    if c < 0:
        share_battery = np.log1p(e / 100) / (np.log1p(e / 100) - np.log1p(c / 100))
        source = (f"Bigger batteries account for {share_battery:.0%} of the (log) range gain and lower "
                  f"consumption for the remaining {1 - share_battery:.0%}.")
    else:
        source = "All of the range gain came from bigger batteries; average consumption per mile did not fall."
    yr = "Model year (+1)"
    if yr in ols_tab.index and ols_tab.loc[yr, "ci_high_pct"] < 0 and c > -5:
        source += (f" This hides a real improvement: holding class, drivetrain and motor power fixed, consumption falls "
                   f"{abs(ols_tab.loc[yr, 'effect_pct']):.1f}% per model year. The gap comes from the changing mix of vehicles "
                   f"on offer, with more SUVs and pickups, more all-wheel drive and more power.")
    lines.append(
        f"1. The median EPA range went from {h['median_range_first']:.0f} miles in {h['first_year']} to "
        f"{h['median_range_last']:.0f} miles in {h['last_year']}. The geometric-mean range changed by "
        f"{_pct(h['range_change_pct'])}, energy per full charge by {_pct(e)} and consumption by {_pct(c)}. {source}")
    if h.get("n_battery_stated", 0) >= 10:
        lines.append(
            f"2. The derived energy per charge passes a sanity check. For the {h['n_battery_stated']} configurations "
            f"whose battery size EPA lists, the stated capacity is a median {h['battery_to_energy_median']:.2f} times "
            f"the energy drawn from the wall"
            + (f", consistent with charging losses of about {1 - h['battery_to_energy_median']:.0%}."
               if 0.8 <= h["battery_to_energy_median"] <= 0.97 else
               ", outside the 80 to 97 percent range expected from charging losses, so treat it with care."))
    suv_rose = h["suv_share_last"] > h["suv_share_first"]
    suv = (f"{_next(lines)}. The share of SUVs and pickups among EV "
           f"configurations went from {_share(h['suv_share_first'])} to {_share(h['suv_share_last'])}.")
    if "Class: SUV (vs car)" in ols_tab.index:
        suv += (f" In the regression below an SUV uses {ols_tab.loc['Class: SUV (vs car)', 'effect_pct']:.0f}% more "
                f"energy per mile than a car of the same model year and motor power"
                + (", so the shift towards SUVs pushes average consumption up." if suv_rose else "."))
    lines.append(suv)
    n = _next(lines)
    lines.append(
        f"{n}. EVs reverse the usual city/highway pattern. The median EV's highway efficiency is "
        f"{h['ev_hwy_city_median']:.2f} times its city efficiency, against {h['gas_hwy_city_median']:.2f} for gasoline "
        f"cars. {_share(h['gas_share_better_hwy'])} of gasoline cars but only {_share(h['ev_share_better_hwy'])} of "
        f"EVs are more efficient on the highway.")
    if len(me) >= 2:
        best, worst = me.iloc[0], me.iloc[-1]
        n = _next(lines)
        lines.append(
            f"{n}. For the same reference vehicle ({_ref_text(me)}), predicted consumption ranges from "
            f"{best['consumption']:.1f} kWh/100 mi ({best['make']}) "
            f"to {worst['consumption']:.1f} kWh/100 mi ({worst['make']}).")
    n = _next(lines)
    base = cv.loc["Baseline: class median", "mae"]
    best_name = cv["mae"].idxmin()
    if best_name == "Baseline: class median":
        lines.append(
            f"{n}. On model lines the models had never seen, neither OLS nor gradient boosting beat the class-median "
            f"baseline (MAE {base:.2f} kWh/100 mi). With this sample, the listed specifications do not predict "
            f"consumption much better than vehicle class alone.")
    else:
        gain = 100 * (1 - cv.loc[best_name, "mae"] / base)
        lines.append(
            f"{n}. On model lines the models had never seen, {best_name} had the lowest error "
            f"(MAE {cv.loc[best_name, 'mae']:.2f} kWh/100 mi, {cv.loc[best_name, 'mape_pct']:.1f}% of the true value), "
            f"{gain:.0f}% below the class-median baseline.")
    return "\n".join(lines)


def tables_markdown(ols_tab: pd.DataFrame, fit, cv: pd.DataFrame) -> str:
    lines = ["#### Explanatory regression: log consumption (HC3 robust standard errors)", "",
             f"n = {int(fit.nobs)}, R² = {fit.rsquared:.2f}", "",
             "| Term | Effect on consumption | 95% CI | p-value |", "|---|---:|---:|---:|"]
    for term, r in ols_tab.iterrows():
        lines.append(f"| {term} | {r.effect_pct:+.1f}% | [{r.ci_low_pct:+.1f}%, {r.ci_high_pct:+.1f}%] | {r.p_value:.3f} |")
    lines += ["", "#### Predictive models: grouped 5-fold cross-validation by model line", "",
              "| Model | MAE (kWh/100 mi) | MAPE | R² |", "|---|---:|---:|---:|"]
    for name, r in cv.iterrows():
        lines.append(f"| {name} | {r.mae:.2f} | {r.mape_pct:.1f}% | {r.r2:.2f} |")
    return "\n".join(lines)


def update_readme(readme: Path, block: str) -> None:
    """Replace the text between the results markers in README.md."""
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError("README is missing the results markers")
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: f"{START}\n{block}\n{END}", text, flags=re.S)
    readme.write_text(new, encoding="utf-8")
