# ========================================
# Optimized Multi-Stage Dockerfile
# Python FastAPI Backend Application with uv Package Manager
# ========================================

# --- Base stage ---
FROM python:3.12.6-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies needed for building wheels
RUN apk add --no-cache gcc libpq-dev

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- Builder stage ---
FROM base AS builder

# Install system dependencies needed for building wheels
RUN apk add --no-cache gcc libpq-dev

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files first for better cache usage
COPY .python-version pyproject.toml uv.lock* ./

# Install dependencies using uv sync with locked versions
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Copy the rest of the application code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY jwks.json ./

# Clean up build dependencies that aren't needed at runtime
RUN apk del gcc libpq-dev

# --- Final stage ---
FROM python:3.12.6-alpine AS final

# Install only runtime dependencies and create non-root user in one layer
RUN apk add --no-cache libpq && \
    adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Create logs directory with proper permissions before switching to non-root user
RUN mkdir -p logs && chown -R appuser:appuser /app
USER appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/alembic /app/alembic
COPY --from=builder --chown=appuser:appuser /app/alembic.ini /app/alembic.ini
COPY --from=builder --chown=appuser:appuser /app/jwks.json /app/jwks.json

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
