#!/usr/bin/env bash
# sandbox/run_integration.sh
# Spins up the docker-compose sandbox and verifies that the sim-agent posts to the mock SEBEK server

set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
COMPOSE_DIR="$ROOT_DIR/sandbox"

echo "Starting sandbox..."
cd "$COMPOSE_DIR"

docker-compose up -d --build

# wait for mock to become healthy (simple wait)
echo "Waiting for sebek-mock to initialize..."
sleep 5

# allow sim-agent to post a few messages
echo "Allowing sim-agent to post messages (15s)..."
sleep 15

# Fetch the observations log from the running container
CONTAINER_ID=$(docker-compose ps -q sebek-mock)
if [ -z "$CONTAINER_ID" ]; then
  echo "Could not find sebek-mock container"
  exit 1
fi

echo "=== Observations log from sebek-mock ==="
docker exec "$CONTAINER_ID" sh -c 'if [ -f /data/observations.log ]; then cat /data/observations.log; else echo "/data/observations.log not found"; fi'

echo "Integration test complete. Bring down sandbox with: docker-compose down"
