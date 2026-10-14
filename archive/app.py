import streamlit as st
import joblib
import requests
from bs4 import BeautifulSoup
import features as fe
import pandas as pd
import time

st.set_page_config(
    page_title="PhishGuard | AI Phishing Detector",
    page_icon="🛡️",
    layout="centered",
)

st.markdown(
    """
    <style>

    .title-text {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .result-card-danger {
        background-color: #2d1616;
        border: 1px solid #f85149;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .result-card-safe {
        background-color: #13261a;
        border: 1px solid #2ea043;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .result-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .confidence-text {
        color: #8b949e;
        font-size: 0.95rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="title-text">🛡️ PhishGuard</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle-text">Phishing Website Detector — content-based machine learning analysis</p>',
    unsafe_allow_html=True
)


# ============================================================
# PROJECT DETAILS
# ============================================================

with st.expander("📚 PROJECT DETAILS", expanded=False):

    st.markdown(
        """
        ### Approach

        PhishGuard is a supervised machine learning application designed to classify websites as legitimate or potentially phishing based on features extracted from their HTML content.

        The application uses a content-based approach. The URL entered by the user is only used to retrieve the webpage. The classification itself is performed using features extracted from the webpage's HTML structure and content.

        The HTML is retrieved using the Requests library and parsed using BeautifulSoup. The extracted features are then passed to the trained machine learning models.

        ### Machine Learning Models

        Seven supervised classification models were evaluated using stratified 5-fold cross-validation:

        - **NB** — Gaussian Naive Bayes
        - **SVM** — Linear Support Vector Machine
        - **DT** — Decision Tree
        - **RF** — Random Forest
        - **AB** — AdaBoost
        - **LR** — Logistic Regression
        - **XGB** — XGBoost

        ### Dataset

        The dataset contains **26,585 website samples**, consisting of **16,061 legitimate websites** and **10,524 phishing websites**.

        Each website is represented using structured features extracted from its webpage content, with:

        - **0** → Legitimate
        - **1** → Phishing

        ### Content-Based Features

        The model does not classify a website based on the URL string itself. Instead, it uses features extracted from the webpage after retrieving and parsing its HTML content.

        Examples of content-related characteristics include HTML elements, forms, links, scripts, iframes, and other structural properties used by the feature extraction process.

        💡

        The URL is only the location used to retrieve the webpage. It is not itself used as a classification feature.

        ### Evaluation

        The models were evaluated using stratified 5-fold cross-validation. Accuracy, precision, and recall were calculated for each fold and then averaged to compare model performance.

        ### Cross-Validation Results

        The trained models are available in the application and can be compared using the model selection options below.
        """
    )


# ============================================================
# LOAD TRAINED MODELS
# ============================================================

@st.cache_resource
def load_models():
    models = joblib.load("all_models.pkl")
    columns = joblib.load("feature_columns.pkl")
    best_name = joblib.load("best_model_name.pkl")
    return models, columns, best_name


try:
    all_models, feature_columns, best_model_name = load_models()
    model_ready = True
except FileNotFoundError:
    model_ready = False
    st.error(
        "⚠️ Model files not found. Run `machine_learning.py` first to generate `all_models.pkl`."
    )


# ============================================================
# ANALYZE A WEBSITE
# ============================================================

st.markdown("### 🔍 Analyze a Website")

st.write(
    "Enter a webpage URL. PhishGuard will retrieve its HTML and analyze its content-based features."
)


url = st.text_input(
    "",
    placeholder="🔗  Paste a URL to analyze, e.g. https://example.com"
)


mode = st.radio(
    "How should this be analyzed?",
    ["🏆 Best model only", "🎯 Choose a specific model", "📊 Run all models"],
    horizontal=True,
)


selected_model_name = None

if mode == "🎯 Choose a specific model" and model_ready:
    selected_model_name = st.selectbox(
        "Select a model",
        list(all_models.keys())
    )


analyze = st.button(
    "Analyze Website",
    disabled=not model_ready
)


# ============================================================
# SCRAPE URL
# ============================================================

def scrape_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(
            url,
            timeout=6,
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            return response.text

        return None

    except requests.exceptions.RequestException:
        return None


# ============================================================
# BUILD FEATURE VECTOR
# ============================================================

def build_feature_vector(html, url, feature_columns):
    soup = BeautifulSoup(html, "html.parser")
    vector = fe.create_vector(soup, url)
    df = pd.DataFrame([vector], columns=feature_columns)
    return df


# ============================================================
# RESULT CARD
# ============================================================

def render_result_card(model_name, prediction, confidence):

    if prediction == 1:

        confidence_text = (
            f" · Confidence: {confidence:.1f}%"
            if confidence is not None
            else ""
        )

        st.markdown(
            f"""<div class="result-card-danger"><div style="font-size: 3rem;">🚨</div><div class="result-title" style="color:#f85149;">Phishing Detected</div><div class="confidence-text">{model_name}{confidence_text}</div></div>""",
            unsafe_allow_html=True
        )

    else:

        confidence_text = (
            f" · Confidence: {confidence:.1f}%"
            if confidence is not None
            else ""
        )

        st.markdown(
            f"""<div class="result-card-safe"><div style="font-size: 3rem;">✅</div><div class="result-title" style="color:#2ea043;">Looks Legitimate</div><div class="confidence-text">{model_name}{confidence_text}</div></div>""",
            unsafe_allow_html=True
        )


# ============================================================
# PREDICT
# ============================================================

def predict_with(model, X_input):

    prediction = model.predict(X_input)[0]

    confidence = None

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_input)[0]
        confidence = proba[int(prediction)] * 100

    return prediction, confidence


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not url.strip():

        st.warning("Please enter a URL first.")

    else:

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        with st.spinner("🔍 Scraping page and extracting features..."):

            time.sleep(0.4)

            html = scrape_url(url)

        if html is None:

            st.error(
                "❌ Couldn't reach that URL. It may be down, blocking automated requests, or the link is invalid."
            )

        else:

            with st.spinner("🧠 Running through the model..."):

                time.sleep(0.4)

                X_input = build_feature_vector(
                    html,
                    url,
                    feature_columns
                )


            # =================================================
            # BEST MODEL
            # =================================================

            if mode == "🏆 Best model only":

                model = all_models[best_model_name]

                prediction, confidence = predict_with(
                    model,
                    X_input
                )

                render_result_card(
                    f"Best model: {best_model_name}",
                    prediction,
                    confidence
                )

                is_phishing_verdict = prediction == 1


            # =================================================
            # SPECIFIC MODEL
            # =================================================

            elif mode == "🎯 Choose a specific model":

                model = all_models[selected_model_name]

                prediction, confidence = predict_with(
                    model,
                    X_input
                )

                render_result_card(
                    selected_model_name,
                    prediction,
                    confidence
                )

                is_phishing_verdict = prediction == 1


            # =================================================
            # ALL MODELS
            # =================================================

            else:

                st.markdown("#### Results across all models")

                rows = []

                phishing_votes = 0

                for name, model in all_models.items():

                    prediction, confidence = predict_with(
                        model,
                        X_input
                    )

                    verdict = (
                        "🚨 Phishing"
                        if prediction == 1
                        else "✅ Legitimate"
                    )

                    phishing_votes += int(prediction == 1)

                    rows.append(
                        {
                            "Model": name,
                            "Verdict": verdict,
                            "Confidence": (
                                f"{confidence:.1f}%"
                                if confidence is not None
                                else "—"
                            ),
                        }
                    )


                results_df = pd.DataFrame(rows)

                st.dataframe(
                    results_df,
                    use_container_width=True,
                    hide_index=True
                )


                # =================================================
                # CONSENSUS
                # =================================================

                total = len(all_models)

                is_phishing_consensus = (
                    phishing_votes > total / 2
                )


                if is_phishing_consensus:

                    st.markdown(
                        f"""<div class="result-card-danger"><div style="font-size: 2rem;">🚨 Potential Phishing</div><div class="confidence-text">Consensus: {phishing_votes}/{total} models flagged this website as phishing</div></div>""",
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""<div class="result-card-safe"><div style="font-size: 2rem;">✅ Legitimate</div><div class="confidence-text">Consensus: {phishing_votes}/{total} models flagged this website as phishing</div></div>""",
                        unsafe_allow_html=True
                    )


                is_phishing_verdict = is_phishing_consensus


            # =================================================
            # FINAL MESSAGE
            # =================================================

            if not is_phishing_verdict:

                st.caption(
                    "No strong phishing indicators found — but always stay cautious with unfamiliar sites."
                )

            else:

                st.caption(
                    "⚠️ This site shows structural patterns commonly associated with phishing. Avoid entering personal information."
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Built with scikit-learn, XGBoost, BeautifulSoup & Streamlit · Content-based phishing website detection"
)