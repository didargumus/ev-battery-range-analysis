r"""Descriptive analysis: range trends, the range decomposition, and the city/highway pattern.

Range decomposition
-------------------
For every vehicle, range is energy per charge divided by consumption:

.. math:: R_i = 100\,\frac{E_i}{c_i}
   \quad\Longrightarrow\quad \log R_i = \log 100 + \log E_i - \log c_i .

Averaging the logs within a model year gives an *exact* decomposition of
the geometric-mean range into a battery effect and an efficiency effect:

.. math:: \Delta \overline{\log R} = \Delta \overline{\log E} - \Delta \overline{\log c}.

Medians do not decompose this way, which is why the geometric mean is used.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["yearly_summary", "range_decomposition", "city_highway_comparison", "headline_numbers"]


def yearly_summary(ev: pd.DataFrame, min_models: int = 10) -> pd.DataFrame:
    """Per model year: number of configurations and quartiles of range and consumption."""
    g = ev.groupby("year")
    out = pd.DataFrame({
        "n": g.size(),
        "range_q25": g["range"].quantile(0.25),
        "range_median": g["range"].median(),
        "range_q75": g["range"].quantile(0.75),
        "consumption_median": g["consumption"].median(),
        "energy_median": g["energy_kwh"].median(),
        "share_suv_pickup": g["vehicle_class"].apply(lambda s: s.isin(["SUV", "Pickup"]).mean()),
        "share_awd": g["awd"].mean(),
    })
    return out[out["n"] >= min_models]


def range_decomposition(ev: pd.DataFrame, min_models: int = 10) -> pd.DataFrame:
    """Geometric-mean range, energy and consumption by year, indexed to the first year (=100).

    The identity ``range_index = energy_index / consumption_index * 100`` holds exactly.
    """
    d = ev.assign(log_r=np.log(ev["range"]), log_e=np.log(ev["energy_kwh"]), log_c=np.log(ev["consumption"]))
    g = d.groupby("year").agg(n=("log_r", "size"), log_r=("log_r", "mean"), log_e=("log_e", "mean"),
                              log_c=("log_c", "mean"))
    g = g[g["n"] >= min_models]
    base = g.iloc[0]
    out = pd.DataFrame({
        "n": g["n"],
        "gm_range": np.exp(g["log_r"]),
        "gm_energy_kwh": np.exp(g["log_e"]),
        "gm_consumption": np.exp(g["log_c"]),
        "range_index": 100 * np.exp(g["log_r"] - base["log_r"]),
        "energy_index": 100 * np.exp(g["log_e"] - base["log_e"]),
        "consumption_index": 100 * np.exp(g["log_c"] - base["log_c"]),
    })
    return out


def city_highway_comparison(ev: pd.DataFrame, gas: pd.DataFrame) -> pd.DataFrame:
    """Highway/city efficiency ratio for EVs and for gasoline cars.

    A ratio below 1 means the vehicle is *less* efficient on the highway. For
    combustion engines the ratio is usually above 1 (idling and low-load
    operation waste fuel in town); EVs recover braking energy in town and
    suffer more aerodynamic drag at highway speed.
    """
    rows = []
    for label, df in (("Battery electric", ev), ("Gasoline", gas)):
        r = df["hwy_city_ratio"].replace([np.inf, -np.inf], np.nan).dropna()
        rows.append({"group": label, "n": len(r), "median_ratio": r.median(),
                     "share_better_on_highway": (r > 1).mean()})
    return pd.DataFrame(rows).set_index("group")


def headline_numbers(ev: pd.DataFrame, gas: pd.DataFrame, min_models: int = 10) -> dict:
    """The numbers quoted in the README, computed from the data."""
    ys = yearly_summary(ev, min_models)
    dec = range_decomposition(ev, min_models)
    ch = city_highway_comparison(ev, gas)
    first, last = int(dec.index[0]), int(dec.index[-1])
    stated = ev.dropna(subset=["battery_kwh_stated"])
    ratio = (stated["battery_kwh_stated"] / stated["energy_kwh"]) if len(stated) else pd.Series(dtype=float)
    return {
        "n_battery_stated": int(len(stated)),
        "battery_to_energy_median": float(ratio.median()) if len(ratio) else float("nan"),
        "n_vehicles": int(len(ev)), "n_families": int(ev["family"].nunique()), "n_makes": int(ev["make"].nunique()),
        "year_min": int(ev["year"].min()), "year_max": int(ev["year"].max()),
        "first_year": first, "last_year": last,
        "median_range_first": float(ys.loc[first, "range_median"]),
        "median_range_last": float(ys.loc[last, "range_median"]),
        "range_change_pct": float(dec.loc[last, "range_index"] - 100),
        "energy_change_pct": float(dec.loc[last, "energy_index"] - 100),
        "consumption_change_pct": float(dec.loc[last, "consumption_index"] - 100),
        "suv_share_first": float(ys.loc[first, "share_suv_pickup"]),
        "suv_share_last": float(ys.loc[last, "share_suv_pickup"]),
        "ev_hwy_city_median": float(ch.loc["Battery electric", "median_ratio"]),
        "gas_hwy_city_median": float(ch.loc["Gasoline", "median_ratio"]),
        "ev_share_better_hwy": float(ch.loc["Battery electric", "share_better_on_highway"]),
        "gas_share_better_hwy": float(ch.loc["Gasoline", "share_better_on_highway"]),
    }
