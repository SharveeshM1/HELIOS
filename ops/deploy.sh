#!/bin/bash

# HELIOS Deployment Script
# This script pulls the latest code, builds the containers, and restarts the system.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "🚀 Starting HELIOS Deployment..."

# 1. Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull --ff-only origin main

# 2. Build and restart containers
echo "🏗️ Building and restarting Docker containers..."
docker compose up -d --build

echo "✅ HELIOS Deployment Successful!"
