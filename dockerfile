FROM python:3.11-slim

# libgomp1 is REQUIRED for XGBoost on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend dependencies.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir \
    --timeout 120 \
    --retries 10 \
    -r ./backend/requirements.txt

# Copy the project layout the backend expects at runtime.
COPY backend ./backend
COPY inference_config.py ./inference_config.py
COPY models ./models
COPY feature_extraction ./feature_extraction
COPY results_summary.csv ./results_summary.csv

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]