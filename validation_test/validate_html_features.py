"""Validate our 23 HTML (content) features against the dataset's stored values.

Run from the project root (the folder that contains feature_extraction/ and data.csv):

    python validate_html_features.py --data data.csv --html-dir /home/louisa/All_HTML --n 500

What it does:
  1. Takes a random sample of rows from data.csv (half phishing, half legitimate).
  2. Reads the original HTML file of each row (named <serial_number>.txt).
  3. Runs our extractor on (url, html).
  4. Compares our 23 content features with the stored ones, feature by feature.

The HTML files may contain malicious scripts. This script only READS them as text
and parses them with the extractor. Never open them in a browser.
"""
import argparse
import traceback
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

import numpy as np
import pandas as pd

from feature_extraction.extractor import url_to_features

ID_COLS = ["serial_number", "url", "label"]
N_CONTENT = 23  # F48..F70, the last 23 feature columns


def to_dict(result):
    """Accept a dict, a Series or a one-row DataFrame."""
    if isinstance(result, pd.DataFrame):
        return result.iloc[0].to_dict()
    if isinstance(result, pd.Series):
        return result.to_dict()
    return dict(result)


def same(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return a == b
    if np.isnan(a) and np.isnan(b):
        return True
    return bool(np.isclose(a, b, rtol=1e-6, atol=1e-9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data.csv")
    ap.add_argument("--html-dir", required=True)
    ap.add_argument("--n", type=int, default=500, help="total rows to test")
    ap.add_argument("--seed", type=int, default=10)
    ap.add_argument("--encoding", default="utf-8")
    args = ap.parse_args()

    print("Library versions:")
    for pkg in ["beautifulsoup4", "lxml", "tldextract", "Levenshtein", "thefuzz"]:
        try:
            print(f"  {pkg}: {version(pkg)}")
        except PackageNotFoundError:
            print(f"  {pkg}: not installed")

    df = pd.read_csv(args.data)
    feature_cols = [c for c in df.columns if c not in ID_COLS]
    assert len(feature_cols) == 70, f"expected 70 features, found {len(feature_cols)}"
    content_cols = feature_cols[-N_CONTENT:]
    print(f"\nContent features: first = {content_cols[0]}, last = {content_cols[-1]}")

    # index the HTML files by serial number (file name without extension)
    html_dir = Path(args.html_dir)
    files = {p.stem: p for p in html_dir.rglob("*.txt")}
    print(f"HTML files found: {len(files)}")

    half = args.n // 2
    parts = [
        df[df["label"] == lab].sample(min(half, (df["label"] == lab).sum()),
                                      random_state=args.seed)
        for lab in (0, 1)
    ]
    sample = pd.concat(parts)

    mism = []          # one record per mismatching value
    row_ok = 0
    tested = 0
    missing_file = 0
    errors = []

    for _, row in sample.iterrows():
        key = str(row["serial_number"]).split(".")[0]
        path = files.get(key)
        if path is None:
            missing_file += 1
            continue
        html = path.read_text(encoding=args.encoding, errors="ignore")
        try:
            ours = to_dict(url_to_features(row["url"], html))
        except Exception:
            errors.append((key, traceback.format_exc()))
            continue
        absent = [c for c in content_cols if c not in ours]
        if absent:
            raise SystemExit(f"Our extractor output lacks columns: {absent}")
        tested += 1
        bad = 0
        for c in content_cols:
            if not same(ours[c], row[c]):
                bad += 1
                mism.append({"serial_number": key, "label": row["label"],
                             "feature": c, "stored": row[c], "ours": ours[c]})
        row_ok += bad == 0

    print(f"\nRows sampled: {len(sample)} | tested: {tested} | "
          f"missing HTML file: {missing_file} | extractor errors: {len(errors)}")
    if tested == 0:
        raise SystemExit("Nothing tested. Check --html-dir and file names.")
    print(f"Rows where all {N_CONTENT} content features match: "
          f"{row_ok}/{tested} ({100 * row_ok / tested:.1f}%)")

    mdf = pd.DataFrame(mism)
    per_feature = (mdf.groupby("feature").size().reindex(content_cols).fillna(0).astype(int)
                   if len(mdf) else pd.Series(0, index=content_cols))
    summary = pd.DataFrame({"mismatches": per_feature,
                            "mismatch_pct": (100 * per_feature / tested).round(2)})
    print("\nPer-feature mismatches (sorted):")
    print(summary.sort_values("mismatches", ascending=False).to_string())
    print(f"\nFeatures with zero mismatches: {(per_feature == 0).sum()}/{N_CONTENT}")

    summary.to_csv("html_validation_summary.csv")
    if len(mdf):
        mdf.to_csv("html_validation_mismatches.csv", index=False)
        print("\nFirst 3 examples per mismatching feature:")
        print(mdf.groupby("feature").head(3).to_string(index=False))
    if errors:
        print(f"\nFirst extractor error (of {len(errors)}), serial {errors[0][0]}:")
        print(errors[0][1])


if __name__ == "__main__":
    main()