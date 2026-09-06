# -----------------------------------------------------------------------
# WiFi Fault Diagnosis — Backend container
# Python 3.11, FastAPI, Uvicorn
# -----------------------------------------------------------------------

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Expose the Uvicorn port
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
