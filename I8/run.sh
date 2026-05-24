#!/usr/bin/env bash
# run.sh — convenience helper for the I8 demo.
# Usage: bash run.sh
#
# Seeds the NoSQL store, then starts the Flask API on port 5002.
# Run "ngrok http 5002" in a separate terminal to expose it publicly,
# then run "python access_api.py" to demo all endpoints.

set -e

echo "=== Seeding NoSQL store ==="
python seed_db.py

echo ""
echo "=== Starting Flask API on http://localhost:5002 ==="
echo "    Hit Ctrl+C to stop."
echo ""
flask --app app run -p 5002
