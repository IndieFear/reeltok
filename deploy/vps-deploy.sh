#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "→ Pull latest code..."
git pull origin main

echo "→ Build & restart containers..."
docker compose build
docker compose up -d

echo "→ Status:"
docker compose ps

echo "✓ Deploy done — check https://${DOMAIN:-your-domain}"
