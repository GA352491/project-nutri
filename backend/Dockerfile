# ==============================================================================
# NutriPlan — Universal Microservice Dockerfile
# Multi-stage lightweight build for Python FastAPI microservices
# ==============================================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/shared/src"

WORKDIR /app

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install root dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy shared library code
COPY backend/shared /app/backend/shared

# Copy all backend services
COPY backend /app/backend

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
