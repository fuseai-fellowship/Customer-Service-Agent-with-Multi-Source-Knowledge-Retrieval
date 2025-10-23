# Dockerfile (project root) - UPDATED
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PIP_NO_CACHE_DIR=1

# Install build-essential AND python3-dev, libffi-dev for cryptography build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gcc python3-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from backend and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy all backend sources into the image
COPY backend/ /app/

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]