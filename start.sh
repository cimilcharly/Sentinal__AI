#!/bin/bash

# Unix/Linux/Mac startup script for InsiderThreat-AI SaaS

echo
echo "========================================"
echo "  SENTINEL AI - STARTUP"
echo "========================================"
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Install from: https://www.docker.com/"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    exit 1
fi

echo "Starting Sentinel AI services..."
echo "  - PostgreSQL database"
echo "  - Redis cache"
echo "  - FastAPI backend (port 8000)"
echo "  - Next.js frontend (port 3000)"
echo

docker-compose down 2>/dev/null

echo
echo "Pulling latest images..."
docker-compose pull

echo
echo "Starting services (this may take 30 seconds)..."
docker-compose up -d

echo
echo "Waiting for services to be ready..."
sleep 5

echo
echo "Initializing database..."
docker exec insider_threat_api python backend/init_db.py

echo
echo "========================================"
echo "   ✅ SENTINEL AI STARTED!"
echo "========================================"
echo
echo "Access Sentinel AI at:"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Dashboard: http://localhost:3000"
echo
echo "Demo credentials:"
echo "   Email:     admin@acmecorp.com"
echo "   Password:  password123"
echo
echo "To view logs:"
echo "   docker-compose logs -f backend"
echo
echo "To stop services:"
echo "   docker-compose down"
echo
