import streamlit as st
import joblib
import requests
from bs4 import BeautifulSoup
import features as fe
import pandas as pd
import time

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard | AI Phishing Detector",
    page_icon="🛡️",
    layout="centered",
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .title-text {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .subtitle-text {
        text-align: center;
        color: #8b949e;
        font-size: 1.05rem;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    .result-card-safe {
        background: linear-gradient(135deg, #0f3d2e, #0a1f18);
        border: 1px solid #2ea043;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    .result-card-danger {
        background: linear-gradient(135deg, #3d0f0f, #1f0a0a);
        border: 1px solid #f85149;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    .result-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .confidence-text {
        color: #8b949e;
        font-size: 0.95rem;
    }
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #30363d;
        padding: 0.7rem;
        font-size: 1rem;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        color: white;
        font-weight: 600;
        padding: 0.6rem;
        border: none;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        opacity: 0.85;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown('<p class="title-text">🛡️ PhishGuard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle-text">Phishing Website Detector — using content-based analysis</p>',
    unsafe_allow_html=True,
)

# ── Load models (cached so they only load once) ─────────
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
    st.error("⚠️ Model files not found. Run `machine_learning.py` first to generate `all_models.pkl`.")

# ── URL input + mode selector ───────────────────────────
url = st.text_input("", placeholder="🔗  Paste a URL to analyze, e.g. https://example.com")

mode = st.radio(
    "How should this be analyzed?",
    ["🏆 Best model only", "🎯 Choose a specific model", "📊 Run all models"],
    horizontal=True,
)

selected_model_name = None
if mode == "🎯 Choose a specific model" and model_ready:
    selected_model_name = st.selectbox("Select a model", list(all_models.keys()))

analyze = st.button("Analyze Website", disabled=not model_ready)

# ── Scraping + feature extraction ───────────────────────
def scrape_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, timeout=6, headers=headers, verify=False)
        if response.status_code == 200:
            return response.text
        return None
    except requests.exceptions.RequestException:
        return None


def build_feature_vector(html, url, feature_columns):
    soup = BeautifulSoup(html, "html.parser")
    vector = fe.create_vector(soup, url)
    df = pd.DataFrame([vector], columns=feature_columns)
    return df


# ── Result rendering helper ──────────────────────────────
def render_result_card(model_name, prediction, confidence):
    if prediction == 1:
        st.markdown(f"""
        <div class="result-card-danger">
            <div style="font-size: 3rem;">🚨</div>
            <div class="result-title" style="color:#f85149;">Phishing Detected</div>
            <div class="confidence-text">
                {model_name}{" · Confidence: " + f"{confidence:.1f}%" if confidence else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-card-safe">
            <div style="font-size: 3rem;">✅</div>
            <div class="result-title" style="color:#2ea043;">Looks Legitimate</div>
            <div class="confidence-text">
                {model_name}{" · Confidence: " + f"{confidence:.1f}%" if confidence else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)


def predict_with(model, X_input):
    prediction = model.predict(X_input)[0]
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_input)[0]
        confidence = proba[int(prediction)] * 100
    return prediction, confidence


# ── Run analysis ─────────────────────────────────────────
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
                "❌ Couldn't reach that URL. It may be down, blocking automated "
                "requests, or the link is invalid."
            )
        else:
            with st.spinner("🧠 Running through the model..."):
                time.sleep(0.4)
                X_input = build_feature_vector(html, url, feature_columns)

            # ── Best model only ──
            if mode == "🏆 Best model only":
                model = all_models[best_model_name]
                prediction, confidence = predict_with(model, X_input)
                render_result_card(f"Best model: {best_model_name}", prediction, confidence)

            # ── One chosen model ──
            elif mode == "🎯 Choose a specific model":
                model = all_models[selected_model_name]
                prediction, confidence = predict_with(model, X_input)
                render_result_card(selected_model_name, prediction, confidence)

            # ── Run all models ──
            else:
                st.markdown("#### Results across all models")
                rows = []
                phishing_votes = 0
                for name, model in all_models.items():
                    prediction, confidence = predict_with(model, X_input)
                    verdict = "🚨 Phishing" if prediction == 1 else "✅ Legitimate"
                    phishing_votes += int(prediction == 1)
                    rows.append({
                        "Model": name,
                        "Verdict": verdict,
                        "Confidence": f"{confidence:.1f}%" if confidence else "—",
                    })

                results_df = pd.DataFrame(rows)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

                total = len(all_models)
                consensus = "🚨 Phishing" if phishing_votes > total / 2 else "✅ Legitimate"
                st.markdown(f"""
                <div class="{'result-card-danger' if phishing_votes > total/2 else 'result-card-safe'}">
                    <div style="font-size: 2rem;">{consensus}</div>
                    <div class="confidence-text">Consensus: {phishing_votes}/{total} models flagged this as phishing</div>
                </div>
                """, unsafe_allow_html=True)

            # caption reflects the actual verdict shown for the mode used
            if mode == "📊 Run all models":
                is_phishing_verdict = phishing_votes > len(all_models) / 2
            else:
                is_phishing_verdict = prediction == 1

            if not is_phishing_verdict:
                st.caption("No strong phishing indicators found — but always stay cautious with unfamiliar sites.")
            else:
                st.caption("⚠️ This site shows structural patterns commonly associated with phishing. Avoid entering personal information.")

            with st.expander("🔬 See extracted features"):
                st.dataframe(X_input.T.rename(columns={0: "Value"}), use_container_width=True)

# ── Footer ───────────────────────────────────────────────
st.markdown("---")
st.caption("Built with scikit-learn, XGBoost & BeautifulSoup · Content + URL-based feature analysis")