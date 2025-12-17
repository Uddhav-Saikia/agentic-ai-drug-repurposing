#!/bin/bash

# Production deployment script
set -e

echo "🚀 Starting deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed.${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is required but not installed.${NC}" >&2; exit 1; }

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure your settings"
    exit 1
fi

# Check for Gemini API key
if ! grep -q "GEMINI_API_KEY=" .env; then
    echo -e "${RED}Error: GEMINI_API_KEY not configured in .env${NC}"
    exit 1
fi

# Pull latest code (if in git repo)
if [ -d .git ]; then
    echo -e "${YELLOW}Pulling latest code...${NC}"
    git pull origin main || echo "Skipping git pull"
fi

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for database
echo -e "${YELLOW}Waiting for database...${NC}"
sleep 10

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python init_database.py

# Check health
echo -e "${YELLOW}Checking service health...${NC}"
sleep 5

# Check backend
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
fi

# Show running services
echo -e "\n${GREEN}Deployment complete!${NC}\n"
echo "Services:"
docker-compose -f docker-compose.prod.yml ps

echo -e "\n${GREEN}Access URLs:${NC}"
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000/api/v1/docs"
echo "Flower:    http://localhost:5555"

echo -e "\n${YELLOW}View logs:${NC}"
echo "docker-compose -f docker-compose.prod.yml logs -f"

echo -e "\n${YELLOW}Stop services:${NC}"
echo "docker-compose -f docker-compose.prod.yml down"
