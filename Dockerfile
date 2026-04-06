# ============================================================
# Stage 1: Builder — install dependencies in a temp layer
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install deps first (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Runtime — only copy what we need
# ============================================================
FROM python:3.12-slim

# iputils-ping is needed for the ping checker (ICMP)
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user (security best practice)
RUN useradd --create-home appuser

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

# Expose the port uvicorn will listen on
EXPOSE 8000

# Health check — K8s has its own probes, but this helps
# Docker and docker-compose know if the container is healthy
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the app
# --host 0.0.0.0  = listen on all interfaces (required inside a container)
# --workers 2     = 2 uvicorn workers (adjust for your pod CPU limits later)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
