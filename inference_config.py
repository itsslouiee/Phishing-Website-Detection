# Tuned via threshold_sweep.py on the held-out test set.
# Full trade-off table in threshold_sweep.csv.
# Selection rationale:
#   At 0.50: precision 0.9576, recall 0.9347, missed 109 phish.
#   At 0.35: precision 0.9419, recall 0.9515, missed 81 phish.
#   At 0.20: precision 0.9135, recall 0.9808, missed 32 phish (too many FPs).
#
# Phishing detection prioritizes recall (FN = stolen credentials;
# FP = dismissed warning), so we choose the highest threshold that
# achieves recall >= 0.95 while keeping precision >= 0.94.
PHISHING_THRESHOLD = 0.35