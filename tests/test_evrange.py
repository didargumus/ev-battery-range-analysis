"""Tests run on a synthetic EPA-format file, so they need no network access."""

import numpy as np
import pandas as pd
import pytest

from evrange import analysis, data, models, report


def synthetic_raw(n_families=40, seed=0) -> pd.DataFrame:
    """EPA-like table with known structure: SUVs use 25% more energy, each year 3% less."""
    rng = np.random.default_rng(seed)
    makes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    rows, rid = [], 0
    for f in range(n_families):
        make = makes[f % len(makes)]
        cls = "Small Sport Utility Vehicle 4WD" if f % 3 == 0 else "Midsize Cars"
        awd = f % 2 == 0
        kw = float(rng.choice([100, 150, 200, 300]))
        for year in range(2014, 2025):
            if rng.random() < 0.3:
                continue
            cons = 30 * (1.25 if "Sport Utility" in cls else 1.0) * 0.97 ** (year - 2014) * np.exp(rng.normal(0, 0.03))
            energy = 40 + 4 * (year - 2014) + rng.normal(0, 3)
            rng_mi = 100 * energy / cons
            motor = f"{kw:.0f} kW AC PMSM" if f % 4 else f"{kw/2:.0f} (front) {kw/2:.0f} (rear) ({energy*0.9:.0f} kW-hr battery pack)"
            rows.append({"id": rid, "make": make, "model": f"Model{f} {'AWD' if awd else ''}".strip(), "year": year,
                         "VClass": cls, "drive": "All-Wheel Drive" if awd else "Front-Wheel Drive", "atvType": "EV",
                         "fuelType1": "Electricity", "range": round(rng_mi), "rangeCity": rng_mi * 1.05,
                         "rangeHwy": rng_mi * 0.95, "combE": cons, "cityE": cons * 0.9, "highwayE": cons * 1.1,
                         "comb08": 3370 / cons, "city08": 3370 / (cons * 0.9), "highway08": 3370 / (cons * 1.1),
                         "evMotor": motor, "charge240": 8.0})
            rid += 1
    for i in range(300):                                   # gasoline cars: better on the highway
        city = rng.uniform(15, 35)
        rows.append({"id": rid + i, "make": "Gas", "model": f"G{i}", "year": 2015 + i % 9, "VClass": "Midsize Cars",
                     "drive": "Front-Wheel Drive", "atvType": np.nan, "fuelType1": "Regular Gasoline", "range": 0,
                     "rangeCity": 0, "rangeHwy": 0, "combE": 0, "cityE": 0, "highwayE": 0, "comb08": city * 1.15,
                     "city08": city, "highway08": city * rng.uniform(1.2, 1.5), "evMotor": np.nan, "charge240": 0})
    rows.append({**rows[0], "id": 99999, "year": 1999})          # pre-2011 entry must be dropped
    rows.append({**rows[0], "id": 99998, "atvType": "Plug-in Hybrid"})
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def frames():
    raw = synthetic_raw()
    return raw, data.clean_ev(raw), data.clean_gasoline(raw)


# --------------------------------------------------------------------------- parsing and cleaning
@pytest.mark.parametrize("text,kw", [
    ("150 kW ACPM", 150), ("193 (front) 193 (rear) (100 kW-hr battery pack)", 386),
    ("270 kW AC Induction (85 kW-hr battery pack)", 270), ("Front: 160 kW Rear: 160 kW", 320),
    ("80 and 80 kW", 160), ("67 KW AC Induction", 67)])
def test_parse_motor_kw(text, kw):
    assert data.parse_motor_kw(text) == kw


def test_parse_missing_values():
    assert np.isnan(data.parse_motor_kw(None))
    assert np.isnan(data.parse_motor_kw("288V Ni-MH"))
    assert data.parse_battery_kwh("270 kW AC Induction (85 kW-hr battery pack)") == 85
    assert np.isnan(data.parse_battery_kwh("150 kW ACPM"))


@pytest.mark.parametrize("vclass,expected", [
    ("Small Sport Utility Vehicle 4WD", "SUV"), ("Standard Pickup Trucks 4WD", "Pickup"),
    ("Minivan - 2WD", "Van"), ("Midsize Cars", "Car"), ("Small Station Wagons", "Car")])
def test_vehicle_class(vclass, expected):
    assert data.vehicle_class(vclass) == expected


def test_model_family_merges_trims():
    assert data.model_family("Model S 100D") == data.model_family("Model S P85D") == "model s"
    assert data.model_family("Ioniq 5 AWD (Long Range)") == data.model_family("Ioniq 5")


def test_clean_ev_filters(frames):
    raw, ev, _ = frames
    assert ev["year"].min() >= 2011
    assert set(ev["vehicle_class"]) <= {"Car", "SUV", "Pickup", "Van"}
    assert (ev["energy_kwh"] == ev["range"] * ev["consumption"] / 100).all()
    assert 99998 not in set(ev["id"])


def test_load_raw_rejects_wrong_format(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"a": [1]}).to_csv(p, index=False)
    with pytest.raises(ValueError):
        data.load_raw(p)


# --------------------------------------------------------------------------- analysis
def test_decomposition_identity_is_exact(frames):
    _, ev, _ = frames
    dec = analysis.range_decomposition(ev)
    np.testing.assert_allclose(dec["range_index"], 100 * dec["energy_index"] / dec["consumption_index"], rtol=1e-12)
    assert dec["range_index"].iloc[0] == pytest.approx(100)


def test_city_highway_direction(frames):
    _, ev, gas = frames
    ch = analysis.city_highway_comparison(ev, gas)
    assert ch.loc["Battery electric", "median_ratio"] < 1 < ch.loc["Gasoline", "median_ratio"]


def test_headline_numbers(frames):
    _, ev, gas = frames
    h = analysis.headline_numbers(ev, gas)
    assert h["consumption_change_pct"] < 0               # built in: -3% per year
    assert 0.85 < h["battery_to_energy_median"] < 0.95   # built in: stated = 0.9 x energy


# --------------------------------------------------------------------------- models
def test_ols_recovers_built_in_effects(frames):
    _, ev, _ = frames
    tab = models.ols_effects_table(models.explanatory_ols(models.prepare_features(ev)))
    assert tab.loc["Class: SUV (vs car)", "effect_pct"] == pytest.approx(25, abs=3)
    assert tab.loc["Model year (+1)", "effect_pct"] == pytest.approx(-3, abs=0.5)
    assert tab.loc["All-wheel drive", "ci_low_pct"] < 0 < tab.loc["All-wheel drive", "ci_high_pct"]


def test_grouped_cv_beats_baseline_and_keeps_families_apart(frames):
    _, ev, _ = frames
    d = models.prepare_features(ev)
    cv = models.cross_validate_models(d)
    assert cv.loc["OLS (log scale)", "mae"] < cv.loc["Baseline: class median", "mae"]
    from sklearn.model_selection import GroupKFold
    for tr, te in GroupKFold(5).split(d, groups=d["family"]):
        assert not set(d["family"].iloc[tr]) & set(d["family"].iloc[te])


def test_make_effects_and_importance(frames):
    _, ev, _ = frames
    d = models.prepare_features(ev)
    me = models.make_effects(d)
    assert (me["ci_low"] <= me["consumption"]).all() and (me["consumption"] <= me["ci_high"]).all()
    imp = models.permutation_importances(d, n_repeats=5)
    assert imp.iloc[0]["feature"] in {"Vehicle class", "Model year"}


# --------------------------------------------------------------------------- report
def test_findings_and_readme_update(frames, tmp_path):
    _, ev, gas = frames
    d = models.prepare_features(ev)
    fit = models.explanatory_ols(d)
    tab = models.ols_effects_table(fit)
    text = report.findings_markdown(analysis.headline_numbers(ev, gas), tab, models.make_effects(d),
                                    models.cross_validate_models(d), "test")
    assert "—" not in text and "1." in text
    readme = tmp_path / "README.md"
    readme.write_text(f"intro\n{report.START}\nold\n{report.END}\noutro\n")
    report.update_readme(readme, text)
    out = readme.read_text()
    assert "old" not in out and text in out and out.startswith("intro") and out.rstrip().endswith("outro")
