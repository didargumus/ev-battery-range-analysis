"""Download, clean and enrich the EPA fuel economy data for battery-electric vehicles.

Source: the U.S. EPA / DOE fuel economy dataset published at
https://www.fueleconomy.gov/feg/download.shtml (file ``vehicles.csv.zip``).
One row is one vehicle configuration (make, model, model year, drivetrain...).

Units used throughout
---------------------
range         EPA combined range, miles
consumption   EPA combined consumption ``combE``, kWh per 100 miles, measured
              at the wall plug, so it includes charging losses
energy_kwh    range * consumption / 100: the energy drawn from the wall for one
              full charge. It is an upper bound on usable battery capacity
              (wall-to-battery charging efficiency is roughly 85-90%).
"""

from __future__ import annotations

import io
import re
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["EPA_URL", "download_epa", "load_raw", "clean_ev", "clean_gasoline", "vehicle_class", "parse_motor_kw",
           "parse_battery_kwh", "model_family"]

EPA_URL = "https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip"
FIRST_MODERN_YEAR = 2011          # earlier "EVs" are mostly lead-acid fleet conversions

_COLUMNS = ["id", "make", "model", "year", "VClass", "drive", "atvType", "fuelType1", "range", "rangeCity",
            "rangeHwy", "combE", "cityE", "highwayE", "comb08", "city08", "highway08", "evMotor", "charge240"]


def download_epa(dest: str | Path, url: str = EPA_URL, timeout: int = 120) -> Path:
    """Download ``vehicles.csv.zip`` and store the extracted CSV at ``dest``."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ev-battery-range-analysis)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".csv"))
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(zf.read(name))
    return dest


def load_raw(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    missing = [c for c in _COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"unexpected EPA file format, missing columns: {missing}")
    return df[_COLUMNS]


def vehicle_class(vclass: str) -> str:
    """Collapse EPA size classes into car / SUV / pickup / van."""
    v = str(vclass).lower()
    if "sport utility" in v:
        return "SUV"
    if "pickup" in v:
        return "Pickup"
    if "van" in v:
        return "Van"
    return "Car"


_KW = re.compile(r"(\d+(?:\.\d+)?)\s*-?\s*kw(?!\s*-?\s*hr?)", re.I)
_AXLE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:kw\s*)?\((?:front|rear)\)", re.I)
_PAIR = re.compile(r"(\d+(?:\.\d+)?)\s*(?:kw)?\s*(?:and|/|\+)\s*(\d+(?:\.\d+)?)\s*kw", re.I)
_BATT = re.compile(r"(\d+(?:\.\d+)?)\s*kw[- ]?hr?", re.I)


def parse_motor_kw(text) -> float:
    """Total motor power in kW from EPA's free-text ``evMotor`` field.

    Handles the common formats ``"150 kW ACPM"``, ``"193 (front) 193 (rear)"``,
    ``"Front: 160 kW Rear: 160 kW"``, ``"80 and 80 kW"``. Returns NaN when no power is given.
    """
    if not isinstance(text, str):
        return np.nan
    axle = [float(x) for x in _AXLE.findall(text)]
    if axle:
        return float(sum(axle))
    pair = _PAIR.search(text)
    if pair:
        return float(pair.group(1)) + float(pair.group(2))
    clean = _BATT.sub("", text)
    kw = [float(x) for x in _KW.findall(clean)]
    return float(sum(kw)) if kw else np.nan


def parse_battery_kwh(text) -> float:
    """Battery size in kWh when the manufacturer put it in ``evMotor`` (often missing)."""
    if not isinstance(text, str):
        return np.nan
    m = _BATT.search(text)
    return float(m.group(1)) if m else np.nan


def model_family(model: str) -> str:
    """A stable name for a model line across years and trims, used to group
    cross-validation folds (e.g. "Model S 100D" -> "model s")."""
    m = re.sub(r"\(.*?\)", " ", str(model).lower())
    m = re.sub(r"[^a-z0-9\- ]", " ", m)
    tokens = [t for t in m.split() if t not in {"awd", "fwd", "rwd", "4wd", "2wd", "ev", "electric"}]
    return " ".join(tokens[:2]) if tokens else str(model).lower()


def clean_ev(raw: pd.DataFrame, first_year: int = FIRST_MODERN_YEAR) -> pd.DataFrame:
    """Battery-electric vehicles with valid range and consumption, plus derived columns."""
    ev = raw[(raw["atvType"] == "EV") & (raw["fuelType1"] == "Electricity")].copy()
    ev = ev[(ev["year"] >= first_year) & (ev["range"] > 0) & (ev["combE"] > 0)]
    ev = ev.rename(columns={"combE": "consumption"})
    ev["vehicle_class"] = ev["VClass"].map(vehicle_class)
    ev["awd"] = ev["drive"].fillna("").str.contains("All-Wheel|4-Wheel", case=False)
    ev["motor_kw"] = ev["evMotor"].map(parse_motor_kw)
    ev["battery_kwh_stated"] = ev["evMotor"].map(parse_battery_kwh)
    ev["energy_kwh"] = ev["range"] * ev["consumption"] / 100.0
    ev["hwy_city_ratio"] = ev["highway08"] / ev["city08"]
    ev["family"] = ev["make"].str.lower() + " | " + ev["model"].map(model_family)
    cols = ["id", "year", "make", "model", "family", "vehicle_class", "VClass", "drive", "awd", "range",
            "consumption", "energy_kwh", "motor_kw", "battery_kwh_stated", "city08", "highway08",
            "hwy_city_ratio", "charge240"]
    return ev[cols].sort_values(["year", "make", "model"]).reset_index(drop=True)


def clean_gasoline(raw: pd.DataFrame, first_year: int = FIRST_MODERN_YEAR) -> pd.DataFrame:
    """Conventional gasoline cars over the same model years (for the city/highway comparison)."""
    gas = raw[raw["fuelType1"].isin(["Regular Gasoline", "Premium Gasoline", "Midgrade Gasoline"])
              & raw["atvType"].isna() & (raw["year"] >= first_year) & (raw["city08"] > 0)].copy()
    gas["hwy_city_ratio"] = gas["highway08"] / gas["city08"]
    return gas[["year", "make", "model", "city08", "highway08", "hwy_city_ratio"]].reset_index(drop=True)


def data_vintage(path: str | Path) -> str:
    """Date the raw file was obtained (file modification date)."""
    p = Path(path)
    return date.fromtimestamp(p.stat().st_mtime).isoformat() if p.exists() else "unknown"
