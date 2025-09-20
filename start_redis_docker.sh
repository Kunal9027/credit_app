#!/bin/bash

echo "Starting Redis using Docker..."
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH. Please install Docker and try again."
    exit 1
fi

# Check if Redis container is already running
if docker ps --filter "name=credit_app_redis" --format "{{.Names}}" | grep -q "credit_app_redis"; then
    echo "Redis container is already running."
    exit 0
fi

# Check if Redis container exists but is stopped
if docker ps -a --filter "name=credit_app_redis" --format "{{.Names}}" | grep -q "credit_app_redis"; then
    echo "Starting existing Redis container..."
    docker start credit_app_redis
    exit 0
fi

# Start a new Redis container
echo "Creating and starting new Redis container..."
docker run -d --name credit_app_redis -p 6379:6379 redis:7

echo ""
echo "Redis should now be available at localhost:6379"
echo "You can now run the application with python setup_local.py"
echo ""