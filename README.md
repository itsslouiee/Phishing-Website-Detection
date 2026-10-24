# Phishing Website Detection

An end-to-end machine learning application that classifies URLs as **phishing** or **legitimate** in real time. Built with a Python ML pipeline, a FastAPI backend, a Next.js frontend, and containerized with Docker.

The current implementation uses **42 lexical features** extracted from the URL string without fetching the page or parsing the HTML. This pipeline estimates the probability that a URL is associated with phishing and applies a decision threshold to classify it.

Three classifiers are trained and evaluated: **Logistic Regression, Random Forest, and XGBoost**. While XGBoost is the main model, the system includes a side-by-side `/api/v1/compare` endpoint to see how all three algorithms evaluate the same URL.

## Approach & Dataset

I initially started with a **content-based approach**, which extracted features from a webpage's HTML to train the ML model. You can find that original implementation here: [`archive/`](archive/).

However, I encountered a major setback with data collection: I was scraping live websites from PhishTank and Tranco datasets, but phishing URLs are frequently taken down. This made live data collection highly unreliable, as a URL labeled as phishing often had no webpage left to extract HTML from.

To solve this, I pivoted to a **URL-only approach** and switched to the **CompPhish v4 dataset**, which provided pre-extracted URL and HTML features from legitimate and phishing websites. This allowed me to focus on building a robust ML pipeline and evaluating it.

- **Source:** [CompPhish on Mendeley Data](https://data.mendeley.com/datasets/fmbs4kp9wz/4)
- **Citation:** Goenka, Richa (2026), "CompPhish", Mendeley Data, V4, doi: [10.17632/fmbs4kp9wz.4](https://doi.org/10.17632/fmbs4kp9wz.4)
- **Documentation:** [Read the dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13583946/)

While this decision was mainly driven by the challenges I encountered, I later discovered other advantages of URL-only classification:

- **Latency:** URL features can be extracted in milliseconds without waiting for a webpage to load.
- **SSRF Risk:** It avoids the need for the backend server to fetch attacker-controlled URLs, reducing exposure to Server-Side Request Forgery (SSRF) risks.

## Limitations

Although URL-only classification is fast and avoids fetching webpage content, it has some limitations. The model relies on patterns in the URL, which means that small differences in a URL can affect its prediction, even when the URLs belong to the same legitimate website.

For example, during testing, the following Coursera URLs received different predictions:

- `https://www.coursera.org/learn/machine-learning/home/module/1` was flagged as phishing.
- `https://www.coursera.org/learn` was classified as legitimate.

Similarly, some shortened URLs may be flagged as phishing because they provide limited information. For example, `https://bit.ly` was flagged as phishing during testing.

These examples show that the model can incorrectly flag legitimate URLs as phishing, which is a **false positive**. The opposite can also happen when a phishing URL looks similar to a legitimate one and is classified as safe, resulting in a **false negative**.

Since the model identifies patterns associated with phishing and does not verify whether a website is actually trustworthy, its predictions should therefore be treated as estimates rather than definitive judgments.

## How It Works

The following workflow outlines the main steps involved in processing a URL: 

1. **URL input:** The user submits a URL through the web interface.
2. **Feature extraction:** The backend extracts lexical features from the URL, such as its length, the number of special characters, and other URL patterns associated with phishing.
3. **Consistent preprocessing:** The extracted features are prepared in the same format used during model training.
4. **Prediction and classification:** The features are passed to the trained classifiers: **Logistic Regression, Random Forest, and XGBoost**, which estimate the probability that a URL is associated with phishing. 
5. **Threshold:** The application applies a decision threshold (0.35) to the probability score to classify the URL as either phishing or legitimate, and returns the final result.

### Why the threshold matters

A model's default threshold of 0.5 is not necessarily the best operating point for a phishing detector.

- **Lower thresholds** can detect more phishing URLs but may produce more false positives.
- **Higher thresholds** can reduce false positives but may allow more phishing URLs to go undetected.

The current threshold of 0.35 was selected based on the project's threshold analysis, to prioritize phishing recall while maintaining a useful level of precision.

See `threshold_sweep.csv` for the measured trade-offs.

## Model Evaluation & Results

The models were evaluated using **5-fold StratifiedGroupKFold cross-validation**, grouping URLs by registrable domain (e.g., URLs from `google.com` belong to the same group). This helps prevent domain-level data leakage by ensuring that URLs from the same domain do not appear in both the training and validation sets of a fold.

The metrics below are the mean scores across the five folds:

| **Model** | **Accuracy** | **Precision** | **Recall** | **F1-Score** | **PR-AUC** | **ROC-AUC** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Logistic Regression | 0.9016 | 0.9161 | 0.8701 | 0.8924 | 0.9565 | 0.9558 |
| Random Forest | 0.9310 | 0.9284 | 0.9240 | 0.9262 | 0.9718 | 0.9750 |
| **XGBoost** | **0.9291** | **0.9333** | **0.9140** | **0.9234** | **0.9776** | **0.9793** |

## Project Structure

```text
Phishing-Website-Detection/
├── archive/                # Previous implementation
├── feature_extraction/     #  Original dataset feature extraction pipeline with some missing files added
├── validation/              # Dataset validation using HTML content that came with it
├── classifiers/              # Logistic Regression, Random Forest, XGBoost
├── models/                   # Trained model (.pkl) files
├── backend/                  # API and prediction logic
├── frontend/                 # Web interface
├── train_model.py            # Model training and evaluation
├── threshold_sweep.py        # Decision threshold analysis and results are in threshold_sweep.csv
├── inference_config.py       # Inference configuration
├── original_data.csv   
├── results_summary.csv       # Model evaluation results
└── dockerfile                # Container configuration

```

## Quickstart

You can run the full stack locally using Docker or by running the frontend and backend separately.

### Option A: Run via Docker (Recommended)
Make sure you have Docker installed, then run:

```bash
# Build the image
docker build -t phishing-detector .

# Run the container (maps port 8000)
docker run -p 8000:8000 phishing-detector
```
### Option B: Manual Setup

**1. Backend**

```bash
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```
**2. Frontend**

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_GITHUB_URL=https://github.com/itsslouiee" >> .env.local
npm run dev
``` 

## API Reference

The backend exposes a REST API for URL classification, model comparison, and evaluation.

| **Method** | **Endpoint** | **Description** |
| :--- | :--- | :--- |
| `GET` | `/health` | Check API status and whether the models are loaded. |
| `POST` | `/api/v1/predict` | Classify a URL using the main model (XGBoost). |
| `POST` | `/api/v1/compare` | Compare predictions from all three models (Logistic Regression, Random Forest, and XGBoost). |
| `GET` | `/api/v1/evaluation` | Retrieve evaluation metrics for the trained models. |

## A note on reliability

This is an educational project, and its predictions should not be treated as definitive proof that a URL is safe or malicious. A low predicted probability does not guarantee a website is legitimate.

## Author

[Louisa Hadji](https://github.com/itsslouiee)

