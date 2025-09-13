FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Create necessary directories
RUN mkdir -p models training_data outputs server

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]