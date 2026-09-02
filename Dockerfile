# Stage 1: Base image
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies (e.g. for building some python packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directories that might be needed
RUN mkdir -p data-layer/raw data-layer/processed modeling-layer/saved_models

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Command is overridden in docker-compose.yml
CMD ["python", "scripts/generate_synthetic_data.py"]
