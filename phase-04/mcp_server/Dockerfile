FROM python:3.12.6-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies needed for building wheels, psycopg2, etc.
RUN apk add --no-cache gcc libpq-dev

# Install uv package manager
RUN pip install --no-cache-dir uv

# --- Builder stage ---
FROM base AS builder

# Copy dependency files first for better cache usage
COPY --link pyproject.toml uv.lock* ./

# Create virtual environment, activate it, and install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && \
    . .venv/bin/activate && \
    uv sync --locked

# Copy the rest of the application code
COPY --link src ./src

# Clean up build dependencies that aren't needed at runtime
RUN apk del gcc libpq-dev

# --- Final stage ---
FROM python:3.12.6-alpine AS final

# Install only runtime dependencies and create non-root user in one layer
RUN apk add --no-cache libpq && \
    adduser -D appuser

# Set working directory before creating the user
WORKDIR /app

# Create a non-root user
USER appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
# Copy application code from builder
COPY --from=builder /app/src /app/src

# Copy entrypoint files
COPY --link pyproject.toml ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False
ENV PORT=8080
ENV DATABASE_URL=sqlite:///./test.db
ENV JWT_SECRET_KEY=test-secret-key

# Expose the port used by the MCP server (see main.py: port=8080)
EXPOSE 8080

# Default command to run the MCP server
CMD ["python", "-m", "src.mcp_server.main"]
