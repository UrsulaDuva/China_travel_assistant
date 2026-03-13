# China Travel Pro - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Frontend Build
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY src/frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY src/frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY uv.lock* ./
COPY src/ ./src/
COPY tests/ ./tests/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./src/frontend/dist

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Default environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000

# Run the application
CMD ["uv", "run", "python", "-m", "uvicorn", "src.orchestrator.api.app:app", "--host", "0.0.0.0", "--port", "10000"]