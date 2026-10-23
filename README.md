# Phishing Website Detection

A machine learning project for detecting phishing URLs using URL-based features, with a focus on reliable evaluation, consistent inference, and understanding the limitations of phishing classification.

This project explores how machine learning can distinguish legitimate URLs from phishing URLs, and why good evaluation matters just as much as good model performance.

## Overview

The current implementation uses a **URL-only feature extraction pipeline** and an XGBoost classifier to estimate the probability that a URL is associated with phishing.

Rather than relying solely on accuracy scores, the project emphasizes:

- Preventing data leakage during model evaluation.
- Keeping training and inference features consistent.
- Evaluating generalization across previously unseen domains.
- Selecting a classification threshold based on precision and recall.
- Investigating false positives, false negatives, and model limitations.

## Current Approach

The current pipeline follows these steps:

1. **URL feature extraction:** Extract numerical features directly from a URL.
2. **Data preparation:** Remove identifiers and features that cannot be reliably reproduced during inference.
3. **Domain-aware splitting:** Separate training and testing data by registrable domain to reduce domain overlap.
4. **Model training and evaluation:** Train and compare models using appropriate evaluation metrics and grouped cross-validation.
5. **Threshold analysis:** Examine how different classification thresholds affect precision, recall, and missed phishing URLs.
6. **Inference:** Apply the same feature schema used during training to new URLs and classify them using the selected threshold.

The current model intentionally excludes HTML-derived features. These require page-content extraction and cannot be assumed to exist for every URL at inference time.

## Current Results

The following results are from the current evaluation. They are preliminary evidence of model performance, not a guarantee of real-world detection accuracy.

| Metric | Result |
|---|---:|
| Input features | 42 URL-only features |
| Evaluation split | Grouped by registrable domain |
| Cross-validation | StratifiedGroupKFold |
| XGBoost F1-score | 0.9234 |
| XGBoost PR-AUC | 0.9776 |
| XGBoost ROC-AUC | 0.9793 |
| Selected threshold | 0.35 |
| Telegram homepage phishing probability | 0.0128 |

The classification threshold was selected to prioritize phishing recall while maintaining a useful level of precision.

### Why the threshold matters

A model's default threshold of 0.5 is not necessarily the best operating point for a phishing detector.

- **Lower thresholds** can detect more phishing URLs but may produce more false positives.
- **Higher thresholds** can reduce false positives but may allow more phishing URLs to go undetected.

The current threshold of 0.35 was selected based on the project's threshold analysis, with a target recall of at least 0.95 and precision of at least 0.94.

See `threshold_sweep.csv` for the measured trade-offs.

## Lessons from Evaluation

One of the most important findings was that strong evaluation metrics do not automatically mean a model generalizes well.

The earlier pipeline achieved an XGBoost F1-score of 0.9711 but incorrectly assigned `telegram.org` a phishing probability of 0.92. Investigation revealed issues involving domain overlap between training and testing data, inconsistent feature availability, and features that indirectly encoded the labels.

After addressing these issues, the model achieved an F1-score of 0.9234 under the revised evaluation setup, while assigning `telegram.org` a phishing probability of 0.0128.

The lower F1-score reflects a more rigorous evaluation rather than evidence that the previous model was better.

This reinforced an important principle of machine learning: **a trustworthy evaluation is more valuable than an impressive but misleading score.**

For the earlier experiments, datasets, and methodology, see [`archive/README.md`](archive/README.md).

## Project Structure

```text
Phising-Website-Detection/
├── archive/
│   └── README.md
├── feature_extraction/
│   └── ...
├── backend/
│   └── ...
├── frontend/
│   └── ...
├── models/
│   └── ...
├── train_model.py
├── threshold_sweep.py
├── test_inference.py
├── inference_config.py
├── results_summary.csv
├── threshold_sweep.csv
└── README.md
```

*Note: This is a representative structure. Adjust the paths to match the current repository layout.*

### Key Files

| File | Purpose |
|---|---|
| `train_model.py` | Model training, evaluation, and selection |
| `threshold_sweep.py` | Analysis of classification thresholds |
| `test_inference.py` | Inference smoke tests and feature-parity diagnostics |
| `inference_config.py` | Central configuration for the phishing threshold |
| `results_summary.csv` | Recorded model evaluation results |
| `threshold_sweep.csv` | Precision and recall trade-offs across thresholds |
| `models/` | Trained models and feature-column information |
| `feature_extraction/` | URL feature extraction components |
| `backend/` | Backend inference and application logic |
| `frontend/` | User-facing interface |

## Known Limitations

The current implementation is a URL-only detector and has several limitations:

- **Shortener ambiguity:** `t.me`, Telegram's legitimate URL shortener, is incorrectly flagged as phishing. URL-only features may not reliably distinguish a benign shortener from a malicious one.
- **No page-content analysis:** The model does not inspect HTML, JavaScript, forms, or rendered page behavior.
- **No temporal evaluation:** Performance has not yet been established using a time-based train/test split.
- **No adversarial robustness evaluation:** The model has not yet been systematically tested against deliberately manipulated URLs.
- **Limited real-world validation:** Offline evaluation metrics do not establish how the detector will perform on live, evolving phishing campaigns.

Resolving redirects before classification is a potential future improvement, particularly for URL shorteners.

## Future Work

Potential next steps include:

- Improve handling of legitimate URL shorteners and redirect chains.
- Evaluate generalization using temporal splits.
- Investigate adversarial manipulation of URL features.
- Expand testing on diverse, previously unseen domains.
- Explore additional signals when reliable and consistent inference-time extraction is possible.

## A note on reliability

This is an educational project, and its predictions should not be treated as definitive proof that a URL is safe or malicious. A low predicted probability does not guarantee a website is legitimate.

## Author

**Louisa Hadji**

[GitHub](https://github.com/itsslouiee)

---

*This README documents the current URL-only approach. Earlier experiments and their methodology are documented separately in [`archive/README.md`](archive/README.md).*
