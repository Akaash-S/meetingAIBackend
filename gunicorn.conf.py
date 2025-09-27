# Gunicorn configuration for Render deployment
# This file contains optimized settings for production

# Server socket
bind = "0.0.0.0:${PORT}"
backlog = 2048

# Worker processes
workers = 4
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
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

# Performance
worker_tmp_dir = "/dev/shm"
