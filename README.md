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

## Project URLs

## Main Portal URLs

- **Portal Home:** [http://localhost:43721](http://localhost:43721)  
- **Login Page:** [http://localhost:43721/login](http://localhost:43721/login)  
- **Register Page:** [http://localhost:43721/register](http://localhost:43721/register)  
- **Dashboard:** [http://localhost:43721/dashboard](http://localhost:43721/dashboard)  
- **Scoreboard:** [http://localhost:43721/scoreboard](http://localhost:43721/scoreboard)  

---

## Challenge URLs (Vulnerable Web Application)

- **Main Challenge Page:** [http://localhost:43722](http://localhost:43722)  
- **Login Page:** [http://localhost:43722/login](http://localhost:43722/login)  
- **XSS Challenge:** [http://localhost:43722/xss](http://localhost:43722/xss)  
- **File Upload Challenge:** [http://localhost:43722/file_upload](http://localhost:43722/file_upload)  
- **Command Injection Challenge:** [http://localhost:43722/command_injection](http://localhost:43722/command_injection)  
- **Scoreboard:** [http://localhost:43722/scoreboard](http://localhost:43722/scoreboard)


## Security Notice

This platform contains intentionally vulnerable applications for educational purposes. Do not deploy in production environments. 