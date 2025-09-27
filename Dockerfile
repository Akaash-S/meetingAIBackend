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
COPY requirements-complete.txt .

# Install Python dependencies with multiple fallbacks
RUN pip install --no-cache-dir -r requirements-complete.txt || \
    pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r requirements-simple.txt || \
    pip install --no-cache-dir -r requirements-minimal.txt || \
    pip install --no-cache-dir -r requirements-stable.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Create necessary directories
RUN mkdir -p uploads logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Render will override with $PORT)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start the application with startup script
CMD ["./start.sh"]
