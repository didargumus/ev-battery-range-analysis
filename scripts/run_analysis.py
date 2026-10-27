"""Run the full analysis.

    python scripts/run_analysis.py                    # download the latest EPA file, then analyse
    python scripts/run_analysis.py --raw path.csv     # use a local copy of vehicles.csv

Writes data/ev_clean.csv, docs/figures/*.png, docs/results.md and the
results section of README.md.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evrange import analysis, data, models, report  # noqa: E402

warnings.filterwarnings("ignore", category=FutureWarning)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, help="local vehicles.csv (skips the download)")
    ap.add_argument("--vintage", help="label for the data source date (default: file date)")
    ap.add_argument("--no-readme", action="store_true", help="do not rewrite the README results section")
    args = ap.parse_args()

    raw_path = args.raw
    if raw_path is None:
        raw_path = ROOT / "data" / "raw" / "vehicles.csv"
        print(f"Downloading {data.EPA_URL} ...")
        data.download_epa(raw_path)
    vintage = args.vintage or data.data_vintage(raw_path)

    raw = data.load_raw(raw_path)
    ev, gas = data.clean_ev(raw), data.clean_gasoline(raw)
    ev.to_csv(ROOT / "data" / "ev_clean.csv", index=False)
    print(f"{len(ev)} battery-electric configurations, {len(gas)} gasoline configurations")

    ys = analysis.yearly_summary(ev)
    dec = analysis.range_decomposition(ev)
    head = analysis.headline_numbers(ev, gas)

    d = models.prepare_features(ev)
    fit = models.explanatory_ols(d)
    ols_tab = models.ols_effects_table(fit)
    me = models.make_effects(d)
    cv = models.cross_validate_models(d)
    imp = models.permutation_importances(d)

    fig = ROOT / "docs" / "figures"
    fig.mkdir(parents=True, exist_ok=True)
    report.fig_range_trend(ev, ys, fig / "range_trend.png")
    report.fig_decomposition(dec, fig / "decomposition.png")
    report.fig_city_highway(ev, gas, fig / "city_vs_highway.png")
    report.fig_make_effects(me, fig / "make_efficiency.png")
    report.fig_models(cv, imp, fig / "models.png")

    findings = report.findings_markdown(head, ols_tab, me, cv, vintage)
    tables = report.tables_markdown(ols_tab, fit, cv)
    results = ["# Results", "", findings, "", tables, "",
               "## Yearly summary", "", ys.round(3).to_markdown(), "",
               "## Range decomposition (geometric means)", "", dec.round(2).to_markdown(), "",
               "## Manufacturer efficiency (reference vehicle)", "", me.round(2).to_markdown(index=False), "",
               "## Permutation importance", "", imp.round(4).to_markdown(index=False), ""]
    (ROOT / "docs" / "results.md").write_text("\n".join(results), encoding="utf-8")
    (ROOT / "docs" / "headline.json").write_text(json.dumps({**head, "vintage": vintage}, indent=2), encoding="utf-8")

    if not args.no_readme:
        report.update_readme(ROOT / "README.md", findings + "\n\n" + tables)
    print(findings)


if __name__ == "__main__":
    main()
