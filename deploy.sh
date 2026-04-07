#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "  QueueLess — Deployment Script"
echo "============================================"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker is not installed."; exit 1; }
command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 || { echo "ERROR: docker compose is not installed."; exit 1; }

# Determine compose command
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  COMPOSE_CMD="docker-compose"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-up}" in
  up)
    echo "Building and starting containers..."
    $COMPOSE_CMD up -d --build
    echo ""
    echo "Waiting for health check..."
    sleep 5
    echo ""
    echo "============================================"
    echo "  QueueLess is running!"
    echo "  URL: http://localhost:8000"
    echo "  Admin: username=admin, password=admin123"
    echo "============================================"
    echo ""
    echo "View logs:  $COMPOSE_CMD logs -f"
    echo "Stop:       $COMPOSE_CMD down"
    ;;
  down)
    echo "Stopping containers..."
    $COMPOSE_CMD down
    echo "Done."
    ;;
  logs)
    $COMPOSE_CMD logs -f
    ;;
  restart)
    echo "Restarting..."
    $COMPOSE_CMD down
    $COMPOSE_CMD up -d --build
    echo "Done."
    ;;
  reset-db)
    echo "WARNING: This will delete all bookings and settings!"
    read -p "Are you sure? (y/N) " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      $COMPOSE_CMD down
      docker volume rm queueless_db-data 2>/dev/null || true
      echo "Database volume removed."
    fi
    ;;
  *)
    echo "Usage: $0 {up|down|logs|restart|reset-db}"
    exit 1
    ;;
esac
