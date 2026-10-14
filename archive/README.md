# Phishing Website Detection

A phishing website detection project that builds structured webpage features from URLs, trains a machine learning model, and predicts whether a site is phishing or legitimate.

## Overview

This project uses a feature-based approach:

- collect URLs from phishing and legitimate sources
- fetch the corresponding webpages
- extract HTML and DOM-based features
- save the structured output as CSV files
- train a classifier on the structured data

The project currently focuses on DOM and HTML signals such as:

- presence of forms, inputs, buttons, images, and links
- number of elements like tables, divs, spans, scripts, and links
- title/text length and heading tags
- login-related elements such as password or email fields
- hidden inputs and iframe usage

## Project structure

- `data_collector.py` — loads URL lists from CSV, fetches pages, extracts feature vectors, and writes structured dataset files
- `features.py` — core feature detection functions for HTML elements and counts
- `feature_extraction.py` — helper functions for parsing and organizing HTML features
- `machine_learning.py` — combines the dataset, splits train/test sets, trains a classifier, and prints metrics
- `dataset/` — raw and structured datasets used for training and testing
- `requirements.txt` — required Python packages

## Dataset

The project uses CSV files in the `dataset/` folder, including:

- `PhishTank_2026.csv` — phishing URLs
- `structured_phishing_data.csv` — feature vectors labeled as phishing
- `structured_legitimate_data.csv` — feature vectors labeled as legitimate
- `tranco_K9LNW.csv` — source for legitimate URLs

## Environment setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install numpy scikit-learn
```

## Run the workflow

1. Collect structured data for phishing or legitimate URLs:

```bash
python data_collector.py
```

This script reads a CSV of URLs, scrapes the page contents, extracts features, and appends them to a structured dataset file.

2. Train the ML model:

```bash
python machine_learning.py
```

This script:

- reads the structured CSV datasets
- combines the data
- removes the URL column and duplicates
- splits into train/test data
- trains a `LinearSVC` classifier
- prints accuracy, precision, and recall

## Notes

- The script currently selects a range of rows from the source CSV using indexes in `data_collector.py`.
- Some URLs may fail to load due to network restrictions, invalid domains, or SSL/timeouts, so the collector prints those failures instead of crashing.
- The feature design is based on HTML structure and page elements, not on external URL reputation or browser behavior.

## Example output

The model script prints metrics similar to:

```text
True Positives: ...
True Negatives: ...
False Positives: ...
False Negatives: ...
Accuracy: ...
Precision: ...
Recall: ...
```

## Future improvements

- clean and validate the generated CSV data more strictly
- add more URL-based lexical or network features
- compare multiple classifiers such as RandomForest, AdaBoost, and GaussianNB
- add a CLI for selecting phishing vs legitimate dataset generation
- save model artifacts for reuse in prediction scripts

## License

This project is for educational and research purposes.
