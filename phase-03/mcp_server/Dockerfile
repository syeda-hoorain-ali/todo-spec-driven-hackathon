FROM python:3.12.6-alpine

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install uv package manager
RUN pip install uv

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy project files
COPY src ./

# Expose port
EXPOSE 8080

# Run the application
CMD ["uv", "run", "-m", "--with", "mcp", "src.mcp_server.main"]
