#!/usr/bin/env bash
# Start LocalFind API + static web UI (run from final/)
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env — add YELP_API_KEY for Yelp ratings/photos (optional)."
fi

export USE_MONGITA=true
set -a
source .env 2>/dev/null || true
set +a

if [ "${POPULATE_LIVE:-}" = "1" ]; then
  echo "Fetching real data from OSM/Yelp into cache..."
  .venv/bin/python scripts/populate_live_data.py
fi

lsof -ti :5002 | xargs kill -9 2>/dev/null || true
lsof -ti :8777 | xargs kill -9 2>/dev/null || true

.venv/bin/flask --app app run -p 5002 --host 127.0.0.1 &
API_PID=$!
python3 -m http.server 8777 --bind 127.0.0.1 &
WEB_PID=$!

sleep 2
echo ""
echo "LocalFind is running:"
echo "  Web UI:  http://127.0.0.1:8777/web/platform.html"
echo "           http://127.0.0.1:8777/web/index.html"
echo "  API:     http://127.0.0.1:5002/health"
echo ""
echo "First-time live fetch: POPULATE_LIVE=1 ./run_localfind.sh"
echo "Press Ctrl+C to stop."

trap "kill $API_PID $WEB_PID 2>/dev/null" EXIT
wait
