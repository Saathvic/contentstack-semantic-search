# Gunicorn Configuration for Render Deployment
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = 2048

# Worker processes - optimized for memory efficiency
workers = int(os.environ.get('WEB_CONCURRENCY', 1))  # Single worker for memory efficiency
worker_class = "sync"
worker_connections = 100  # Reduced connections
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))  # Configurable timeout
keepalive = 30  # Reduced keepalive

# Restart workers frequently to prevent memory accumulation
max_requests = 20  # Frequent restarts for memory management
max_requests_jitter = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "contentstack-semantic-search"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning - optimized for memory
preload_app = False  # Disable preload to reduce startup memory
worker_tmp_dir = "/dev/shm"
graceful_timeout = 30  # Graceful shutdown timeout