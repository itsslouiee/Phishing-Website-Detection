"""Settings. Everything has a sensible default; override with environment variables."""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# The existing project root (the folder holding models/, feature_extraction/,
# results_summary.csv). By default it is the folder that contains backend/.
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", BACKEND_DIR.parent)).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference_config import PHISHING_THRESHOLD

MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_CSV = PROJECT_ROOT / "results_summary.csv"

# Comma-separated list of browser origins allowed to call the API.
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

MAX_URL_LENGTH = 2048
DECISION_THRESHOLD = PHISHING_THRESHOLD  # label is "phishing" when probability >= this
