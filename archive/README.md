# Previous Approach: Content-Based Phishing Detection

This is the original implementation of my phishing website detection project. It extracts **48 features (43 HTML/DOM elements and 5 URL lexical features)** from live webpages to train a machine learning classifier and predict whether a website is phishing or legitimate. 

This approach was eventually archived in favor of the current URL-only pipeline. This document explains how the original system worked and why the approach was changed.

## Why was this approach dropped?

The content-based approach had a useful advantage: it could analyze a webpage's HTML structure, including elements such as login forms and password fields. However, it introduced a major challenge: **phishing websites often have very short lifespans.**

The original plan relied on downloading live URLs from PhishTank. By the time the URLs were processed and the script attempted to fetch their webpages, many phishing sites were already offline.

This led to:

- Numerous failed requests, timeouts, and SSL errors.
- A smaller dataset than expected, with potential sampling bias.
- More time spent troubleshooting data collection than developing and evaluating the models.

Rather than continue building around unreliable data, the project shifted to a pre-extracted dataset, CompPhish, and a URL-only feature extraction pipeline. This made it possible to focus on model training and evaluation without depending on the availability of live webpages.

## How the original pipeline worked

The original workflow followed five steps:

1. **Collect URLs:** Gather phishing URLs from PhishTank and legitimate URLs from Tranco.
2. **Fetch webpages:**  Use requests to retrieve live webpages and BeautifulSoup to parse their HTML.
3. **Extract features:** Parse the HTML and DOM to identify potentially suspicious structures, focusing on signals such as:
   - **Element presence:** Forms, inputs, buttons, images, and links.
   - **Element counts:** Numbers of tables, divs, spans, scripts, and links.
   - **Page content:** Title and text length, and the presence of heading tags.
   - **Login-related elements:** Password fields, email fields, and other form elements associated with login pages.
   - **Potentially suspicious structures:** Hidden inputs and iframe usage.
   - **URL lexical features:** URL length, number of dots and hyphens, IP address usage, and HTTPS presence. 
4. **Save data:** Store the extracted feature vectors in CSV files.
5. **Train and evaluate:** Train and compare seven machine learning classifiers: Naive Bayes, SVM, Decision Tree, Random Forest, AdaBoost, Logistic Regression, and XGBoost.

## Project structure

- `data_collector.py` — loads URL lists from CSV, fetches pages, extracts feature vectors, and writes structured dataset files
- `features.py` — core feature detection functions
- `machine_learning.py` — combines the dataset, splits train/test sets, trains and evaluates classifiers
- `dataset/` — raw and structured datasets used for training and testing
- `app.py` — Streamlit web interface

## Dataset

The project uses the following CSV files:

- `PhishTank_2026.csv` — phishing URLs
- `structured_phishing_data.csv` — feature vectors labeled as phishing
- `structured_legitimate_data.csv` — feature vectors labeled as legitimate
- `tranco_K9LNW.csv` — source for legitimate URLs
- The dataset files are not included in this repository. You must download the required datasets from their original sources and place them in the `dataset/` directory.

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

## Notes

- The script currently selects a range of rows from the source CSV using indexes in `data_collector.py`.
- Some URLs may fail to load due to network restrictions, invalid domains, or SSL/timeouts, so the collector prints those failures instead of crashing.

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
## License

This project is for educational purposes.
