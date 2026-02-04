# ========================================
# Optimized Multi-Stage Dockerfile
# Python FastAPI Backend Application with uv Package Manager
# ========================================

# --- Base stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- Builder stage ---
FROM base AS builder

# Copy dependency files first for better cache usage
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv sync with locked versions
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Copy the rest of the application code
COPY src/ src/

# Clean up build dependencies that aren't needed at runtime
RUN apt-get purge -y build-essential gcc libpq-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- Final stage ---
FROM python:3.12-slim AS final

# Install only runtime dependencies and create non-root user in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Create logs directory with proper permissions before switching to non-root user
RUN mkdir -p logs && chown -R appuser:appuser /app
USER appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder --chown=appuser:appuser /app/src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the MCP server
CMD ["sh", "-c", "-m --with  mcp src.mcp_server.main"]
