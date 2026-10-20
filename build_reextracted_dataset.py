"""Re-extract the 70 features for every row of original_data.csv from the original HTML files.

    python build_reextracted_dataset.py --html-dir /home/louisa/All_HTML --out test_reextracted.csv --limit 100
    python build_reextracted_dataset.py --html-dir /home/louisa/All_HTML

HTML files are only READ as text. Never open them in a browser.
Safe to stop and re-run: rows already written to the output file are skipped.
"""
import argparse
import csv
import time
from pathlib import Path

import pandas as pd

from feature_extraction.extractor import url_to_features

ap = argparse.ArgumentParser()
ap.add_argument("--original", default="original_data.csv")
ap.add_argument("--out", default="reextracted_data.csv")
ap.add_argument("--html-dir", required=True)
ap.add_argument("--limit", type=int, default=None, help="process only this many random rows (for a test)")
args = ap.parse_args()

original = pd.read_csv(args.original)
columns = list(original.columns)          # same 73 columns, same order as the original
if args.limit:
    original = original.sample(args.limit, random_state=10)

html_files = {p.stem: p for p in Path(args.html_dir).rglob("*.txt")}
print("HTML files found:", len(html_files))

out_path = Path(args.out)
done = set()
if out_path.exists():
    done = set(pd.read_csv(out_path, usecols=["serial_number"])["serial_number"].astype(str))
    print("rows already done:", len(done))

errors = []
start = time.time()
with open(out_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    if not done:
        writer.writeheader()
    for i, row in enumerate(original.itertuples(index=False), start=1):
        key = str(row.serial_number)
        if key in done:
            continue
        path = html_files.get(key)
        if path is None:
            errors.append((key, "no HTML file"))
            continue
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
            features = url_to_features(row.url, html)
            writer.writerow({"serial_number": row.serial_number, "url": row.url,
                             "label": row.label, **features})
            f.flush()
        except Exception as e:
            errors.append((key, repr(e)))
        if i % 100 == 0:
            print(f"{i} rows, {time.time() - start:.0f} s")

print(f"\nfinished in {time.time() - start:.0f} s | errors: {len(errors)}")
if errors:
    pd.DataFrame(errors, columns=["serial_number", "error"]).to_csv("reextraction_errors.csv", index=False)
    print("first errors:", errors[:3])
