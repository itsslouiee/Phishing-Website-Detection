import pandas as pd

orig = pd.read_csv("original_data.csv").set_index("serial_number")
re   = pd.read_csv("reextracted_data.csv").set_index("serial_number")
re   = re.loc[orig.index]

content_cols = list(orig.columns[47:])  # F48..F70

def differs(a, b):
    try:
        return not (float(a) == float(b))
    except (TypeError, ValueError):
        return a != b

mismatch_rows = []
for serial, row in orig.iterrows():
    bad_features = []
    for col in content_cols:
        if differs(row[col], re.loc[serial, col]):
            bad_features.append(col)
    if bad_features:
        mismatch_rows.append({
            "serial_number": serial,
            "url": row["url"],
            "label": row["label"],
            "n_mismatched_features": len(bad_features),
            "mismatched_features": ",".join(bad_features),
        })

df = pd.DataFrame(mismatch_rows)
df.to_csv("affected_rows.csv", index=False)

print(f"Total rows with any content-feature mismatch: {len(df)}")
print(f"  of which label=0 (legit)     : {(df['label'] == 0).sum()}")
print(f"  of which label=1 (phishing)  : {(df['label'] == 1).sum()}")
print()
print("Worst offenders (most mismatched features):")
print(df.sort_values("n_mismatched_features", ascending=False).head(20).to_string(index=False))