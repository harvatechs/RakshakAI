# RakshakAI ML Pipeline Dockerfile
# Container for ML training and inference services

FROM nvidia/cuda:12.1-runtime-ubuntu22.04 as base

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3.11-venv \
    build-essential \
    libsndfile1 \
    libsndfile1-dev \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install ML dependencies
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install audio processing and ML libraries
RUN pip install --no-cache-dir \
    tensorflow-gpu==2.15.0 \
    transformers==4.35.0 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    numpy==1.24.3 \
    scikit-learn==1.3.2 \
    pandas==2.0.3 \
    scipy==1.11.3 \
    matplotlib==3.8.0 \
    seaborn==0.13.0 \
    mlflow==2.8.0 \
    tensorboard==2.15.0 \
    pydantic==2.5.0 \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    websockets==12.0 \
    redis==5.0.1 \
    psycopg2-binary==2.9.9 \
    pymilvus==2.3.3 \
    openai==1.3.0 \
    python-multipart==0.0.6 \
    aiofiles==23.2.1

# Production stage
FROM base as production

# Set working directory
WORKDIR /app

# Copy installed packages
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Copy application code
COPY --chown=mluser:mluser . /app

# Create model and data directories
RUN mkdir -p /models /data && chown -R mluser:mluser /app /models /data

# Switch to non-root user
USER mluser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run the ML service
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
