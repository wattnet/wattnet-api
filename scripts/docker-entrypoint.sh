#!/bin/sh
set -e

# Read a WATTNET_API_* setting honouring the same priority as pydantic-settings:
# 1. OS environment variable  2. /etc/wattnet/api.env  3. /app/.env  4. default
_cfg() {
    key="$1"; default="$2"
    eval "val=\${${key}:-}"
    if [ -n "$val" ]; then echo "$val"; return; fi
    for f in /etc/wattnet/api.env /app/.env; do
        if [ -f "$f" ]; then
            val=$(grep -E "^${key}=" "$f" 2>/dev/null | head -1 | cut -d= -f2-)
            if [ -n "$val" ]; then echo "$val"; return; fi
        fi
    done
    echo "$default"
}

WORKERS=$(_cfg WATTNET_API_WORKERS 1)
PORT=$(_cfg WATTNET_API_PORT 8000)

exec gunicorn wattnet.api:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "$WORKERS" \
    --bind "0.0.0.0:$PORT" \
    --access-logfile - \
    --error-logfile -
