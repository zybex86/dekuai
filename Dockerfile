# ===================================================================
# 🎮 AutoGen DekuDeals - Production Docker Image
# Multi-stage build for optimized production deployment
# ===================================================================

# ===================================================================
# STAGE 1: Builder - Install dependencies and prepare application
# ===================================================================
FROM python:3.13.3-slim as builder

LABEL maintainer="AutoGen DekuDeals Team"
LABEL description="AutoGen DekuDeals Game Analysis System - Builder Stage"
LABEL version="6.3.0"

# Set build arguments
ARG BUILD_DATE
ARG VERSION=6.3.0
ARG VCS_REF

# Environment variables for build optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user (security best practice)
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .

# Switch to appuser for pip install --user
USER appuser
RUN pip install --no-cache-dir --user -r requirements.txt

# Switch back to root for file operations
USER root

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/cache && \
    chown -R appuser:appuser /app

# ===================================================================
# STAGE 2: Production - Final optimized image
# ===================================================================
FROM python:3.13.3-slim as production

LABEL maintainer="AutoGen DekuDeals Team"
LABEL description="AutoGen DekuDeals Game Analysis System - Production"
LABEL version="6.3.0"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.title="AutoGen DekuDeals"
LABEL org.opencontainers.image.description="Enterprise-level game analysis with AutoGen agents"

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH=/home/appuser/.local/bin:$PATH \
    APP_ENV=production \
    WORKERS=1

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy Python packages from builder
COPY --from=builder /home/appuser/.local /home/appuser/.local

# Set work directory
WORKDIR /app

# Copy application code from builder
COPY --from=builder --chown=appuser:appuser /app .

# Create data directories with proper permissions
RUN mkdir -p /app/logs /app/cache /app/data && \
    chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Switch to non-root user (security best practice)
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port for API (when we add it)
EXPOSE 8000

# Volume for persistent data
VOLUME ["/app/cache", "/app/logs", "/app/data"]

# Entry point
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden)
CMD ["api"] 