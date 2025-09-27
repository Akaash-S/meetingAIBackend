#!/bin/bash

# Startup script for Render deployment
# This script ensures proper PORT handling and starts the application

# Set default PORT if not provided
export PORT=${PORT:-5000}

# Log the configuration
echo "Starting AI Meeting Assistant Backend..."
echo "PORT: $PORT"
echo "FLASK_ENV: $FLASK_ENV"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." # Only show first 20 chars for security

# Start the application with gunicorn
exec gunicorn --config gunicorn.conf.py app:app
