#!/bin/bash
set -e

echo "Starting Gunicorn on port 8000"

exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 300 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    main:app