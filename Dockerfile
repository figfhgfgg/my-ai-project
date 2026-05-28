# ============================================================
# Stage: Runtime
# Base image: Official Python 3.14 (slim variant for smaller size)
# Note: Python 3.14 is currently in release-candidate phase.
#       Use "3.14-rc-slim" until the stable tag is published.
# ============================================================
FROM python:3.14-rc-slim

# ---------- Metadata ----------
LABEL maintainer="your-name"
LABEL description="Flask Service Dashboard — Python 3.14"
LABEL version="1.0"

# ---------- Environment variables ----------
# Prevent .pyc files from being written to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Disable stdout/stderr buffering so logs appear immediately
ENV PYTHONUNBUFFERED=1
# Flask environment
ENV FLASK_ENV=production

# ---------- Working directory ----------
WORKDIR /app

# ---------- Install system dependencies ----------
# Only install what is strictly necessary; clean up apt cache to keep the
# image layer small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
# Copy requirements first so Docker can cache this layer independently
# of the application source code.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Application source ----------
# Copy the rest of the project into the container
COPY run.py .
COPY src/ ./src/

# ---------- Expose port ----------
# This matches the port used in run.py (19191)
EXPOSE 19191

# ---------- Health check ----------
# Docker will query /health every 30s; marks container unhealthy after
# 3 consecutive failures.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:19191/health')"

# ---------- Entry point ----------
# Run the Flask app via run.py
CMD ["python", "run.py"]
