#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting CTF Environment...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed.${NC}"
    exit 1
fi

# Stop any running containers first
echo -e "${GREEN}Stopping any existing containers...${NC}"
docker compose down

# Build and start containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker compose up --build -d

# Check if containers started successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Containers started successfully!${NC}"
    echo -e "${GREEN}You can access the following URLs:${NC}"
    echo -e "Portal: http://localhost:43721"
    echo -e "Challenges: http://localhost:43722"
    echo -e "Login Page: http://localhost:43722/login"
    echo -e "XSS Challenge: http://localhost:43722/xss"
    echo -e "File Upload Challenge: http://localhost:43722/file_upload"
    echo -e "Command Injection Challenge: http://localhost:43722/command_injection"
    echo -e "Scoreboard: http://localhost:43722/scoreboard"
else
    echo -e "${RED}Error: Failed to start containers.${NC}"
    exit 1
fi

# Show container status
echo -e "\n${GREEN}Container Status:${NC}"
docker compose ps 