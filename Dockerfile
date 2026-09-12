FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=7860 \
    RECALLX_ENV=production

# Install system dependencies including font utilities for report/image export
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as user ID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install CPU-optimized PyTorch first for fast lightweight build
COPY --chown=user:user backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download Sentence Transformer weights into cache to eliminate startup cold-start delays
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy backend application and data
COPY --chown=user:user backend/ ./backend/
COPY --chown=user:user data/ ./data/

# Expose standard Hugging Face Spaces port
EXPOSE 7860

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Launch FastAPI with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
