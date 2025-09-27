# Gunicorn configuration for Docker deployment
# Optimized for containerized production environment

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes - optimized for container environment
# Use 2x CPU cores + 1, but cap at 8 for memory efficiency
worker_count = min(multiprocessing.cpu_count() * 2 + 1, 8)
workers = int(os.getenv('GUNICORN_WORKERS', worker_count))
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging - optimized for container logs
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ai-meeting-assistant"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Application
preload_app = True
reload = False
reload_extra_files = []

# Environment
raw_env = [
    "PYTHONPATH=/app",
    "PYTHONUNBUFFERED=1",
    "PYTHONDONTWRITEBYTECODE=1",
]

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance - optimized for containers
worker_tmp_dir = "/tmp"

# Memory management
max_requests_jitter = 50

# Graceful shutdown
graceful_timeout = 30
