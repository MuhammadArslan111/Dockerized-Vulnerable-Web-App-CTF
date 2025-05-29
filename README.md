# Web CTF Platform

A web-based Capture The Flag (CTF) platform with vulnerable challenges and a scoring system.

## Features

- Multiple web-based security challenges
- Flag submission system
- Real-time scoreboard
- Dockerized environment for easy deployment
- User authentication and registration

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone this repository
2. Run the start script:
```bash
./start.sh
```

3. Access the CTF platform at http://localhost:43721
4. Access the challenges at http://localhost:43722

## Stopping the Platform

To stop all services and clean up containers, run:
```bash
./stop.sh
```

## Project Structure

- `challenges/` - Contains vulnerable web applications
- `portal/` - CTF portal for flag submission and scoreboard
- `docker/` - Docker configuration files
- `start.sh` - Script to start the entire platform
- `stop.sh` - Script to stop and clean up all services

## Security Notice

This platform contains intentionally vulnerable applications for educational purposes. Do not deploy in production environments. 