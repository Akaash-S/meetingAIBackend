#!/bin/bash

# Startup script for Docker deployment
# This script ensures proper configuration and starts the application

set -e  # Exit on any error

# Set default PORT if not provided
export PORT=${PORT:-5000}

# Log the configuration
echo "=========================================="
echo "Starting AI Meeting Assistant Backend..."
echo "=========================================="
echo "PORT: $PORT"
echo "FLASK_ENV: $FLASK_ENV"
echo "WORKERS: ${GUNICORN_WORKERS:-auto}"
echo "LOG_LEVEL: ${LOG_LEVEL:-info}"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." # Only show first 20 chars for security
echo "=========================================="

# Wait for database to be ready (if DATABASE_URL is set)
if [ ! -z "$DATABASE_URL" ]; then
    echo "Checking database connection..."
    python -c "
import psycopg2
import os
import sys
import time

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.close()
        print('Database connection successful!')
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f'Database connection attempt {retry_count}/{max_retries} failed: {e}')
        if retry_count < max_retries:
            time.sleep(2)
        else:
            print('Failed to connect to database after maximum retries')
            sys.exit(1)
"
fi

# Create necessary directories if they don't exist
mkdir -p uploads logs instance

# Set proper permissions
chmod 755 uploads logs instance

echo "Starting Gunicorn server..."

# Start the application with gunicorn
exec gunicorn --config gunicorn.conf.py app:app
