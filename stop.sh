#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping CTF Environment...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker compose ps | grep -q "Up"; then
    echo -e "${YELLOW}No containers are currently running.${NC}"
    exit 0
fi

# Stop and remove containers
echo -e "${YELLOW}Stopping and removing containers...${NC}"
docker compose down

# Check if containers were stopped successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Containers stopped successfully!${NC}"
    
    # Ask if user wants to remove volumes
    read -p "Do you want to remove all volumes? This will delete all data (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing volumes...${NC}"
        docker compose down -v
        echo -e "${GREEN}Volumes removed successfully!${NC}"
    fi
else
    echo -e "${RED}Error: Failed to stop containers.${NC}"
    exit 1
fi

# Show final container status
echo -e "\n${GREEN}Container Status:${NC}"
docker compose ps 