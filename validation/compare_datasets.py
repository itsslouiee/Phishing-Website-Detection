import numpy as np
import pandas as pd

a = pd.read_csv("original_data.csv").set_index("serial_number")
b = pd.read_csv("reextracted_data.csv").set_index("serial_number")
assert a.index.is_unique and b.index.is_unique
print("rows:", len(a), len(b), "| same serials:", set(a.index) == set(b.index))
b = b.loc[a.index]                                   # same row order
print("urls identical:", (a["url"] == b["url"]).all(), "| labels identical:", (a["label"] == b["label"]).all())

features = [c for c in a.columns if c not in ("url", "label")]      # the 70 features
assert len(features) == 70
diff = pd.DataFrame({c: ~np.isclose(a[c].astype(float), b[c].astype(float), rtol=1e-6, atol=1e-9)
                     for c in features})
diff.index = a.index
n = len(a)

per_feature = diff.sum().sort_values(ascending=False)
print("\nFeatures that differ (count, % of rows):")
for c, k in per_feature[per_feature > 0].items():
    kind = "URL" if features.index(c) < 47 else "HTML"
    print(f"  {c:32s} {kind:4s} {k:6d}  {100 * k / n:5.2f}%")
print("features with zero differences:", int((per_feature == 0).sum()), "of", len(features))

url_bad = diff[features[:47]].any(axis=1)
html_bad = diff[features[47:]].any(axis=1)
any_bad = url_bad | html_bad
print(f"\nrows with at least one difference: {any_bad.sum()} ({100 * any_bad.mean():.1f}%)")
print(f"  URL features differ: {url_bad.sum()} | HTML features differ: {html_bad.sum()}")
print("  differing rows by label:", a.loc[any_bad, "label"].value_counts().to_dict())

long_serial = a.index.astype(str).str.len() >= 10
print(f"\nlong-serial rows: {long_serial.sum()} (differing: {(any_bad & long_serial).sum()})")
print(f"short-serial rows: {(~long_serial).sum()} (differing: {(any_bad & ~long_serial).sum()})")

print("\nrows with 0 hyperlinks, by label:")
print(pd.DataFrame({
    "original": a.loc[a["no_of_hyperlinks"] == 0, "label"].value_counts(),
    "reextracted": b.loc[b["no_of_hyperlinks"] == 0, "label"].value_counts(),
}).fillna(0).astype(int).to_string())
