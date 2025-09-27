# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files for better caching
COPY requirements-simple.txt .
COPY requirements-minimal.txt .
COPY requirements-stable.txt .
COPY requirements.txt .

# Install Python dependencies with multiple fallbacks
RUN pip install --no-cache-dir -r requirements-simple.txt || \
    pip install --no-cache-dir -r requirements-minimal.txt || \
    pip install --no-cache-dir -r requirements-stable.txt || \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Render will override with $PORT)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/health || exit 1

# Start the application with dynamic port
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app
