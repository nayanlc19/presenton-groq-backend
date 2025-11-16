# Multi-stage build for smaller final image
FROM python:3.11-slim-bookworm AS builder

# Install uv for faster dependency resolution
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy only dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (faster than pip)
RUN uv sync --frozen --no-dev --no-install-project

# Final stage
FROM python:3.11-slim-bookworm

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create necessary directories
RUN mkdir -p /app_data /tmp/presenton

# Set environment variables
ENV APP_DATA_DIRECTORY=/app_data \
    TEMP_DIRECTORY=/tmp/presenton \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy only necessary application code (excludes tests, chroma, etc.)
COPY api ./api
COPY constants ./constants
COPY enums ./enums
COPY models ./models
COPY services ./services
COPY utils ./utils
COPY assets ./assets
COPY static ./static
COPY server.py ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server
CMD ["python", "server.py", "--port", "8000", "--reload", "false"]
