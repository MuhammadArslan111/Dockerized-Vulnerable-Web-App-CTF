# Dockerized Vulnerable Web App CTF Platform

A comprehensive web-based Capture The Flag (CTF) platform designed for security training and practice. This platform features intentionally vulnerable web applications and a scoring system to track progress.

## 🚀 Features

- **Multiple Security Challenges**
  - SQL Injection Challenge
  - Cross-Site Scripting (XSS) Challenge
  - File Upload Vulnerability
  - Command Injection Challenge
- **User Management**
  - Secure user authentication
  - Registration system
  - Profile management
- **Scoring System**
  - Real-time scoreboard
  - Points tracking
  - Challenge completion tracking
- **Dockerized Environment**
  - Easy deployment
  - Isolated containers
  - Consistent development environment

## 🛠️ Prerequisites

- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Git
- Basic understanding of web security concepts

## 🏗️ Project Structure

```
.
├── challenges/           # Vulnerable web applications
│   ├── sql_injection/   # SQL Injection challenge
│   ├── xss/            # XSS challenge
│   ├── file_upload/    # File Upload challenge
│   └── command_inj/    # Command Injection challenge
├── portal/             # CTF portal application
│   ├── app.py         # Main Flask application
│   ├── templates/     # HTML templates
│   └── static/        # Static assets
├── docker/            # Docker configuration files
├── start.sh          # Platform startup script
└── stop.sh           # Platform shutdown script
```

## 🚀 Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/dockerized-vulnerable-web-app-ctf.git
   cd dockerized-vulnerable-web-app-ctf
   ```

2. **Start the Platform**
   ```bash
   ./start.sh
   ```

3. **Access the Applications**
   - CTF Portal: http://localhost:43721
   - Vulnerable Web App: http://localhost:43722

4. **Create an Account**
   - Visit http://localhost:43721/register
   - Create your account
   - Log in to access challenges

## 🌐 Available URLs

### CTF Portal (http://localhost:43721)
- **Home:** [http://localhost:43721](http://localhost:43721)
- **Login:** [http://localhost:43721/login](http://localhost:43721/login)
- **Register:** [http://localhost:43721/register](http://localhost:43721/register)
- **Dashboard:** [http://localhost:43721/dashboard](http://localhost:43721/dashboard)
- **Scoreboard:** [http://localhost:43721/scoreboard](http://localhost:43721/scoreboard)

### Vulnerable Web App (http://localhost:43722)
- **Home:** [http://localhost:43722](http://localhost:43722)
- **Login:** [http://localhost:43722/login](http://localhost:43722/login)
- **XSS Challenge:** [http://localhost:43722/xss](http://localhost:43722/xss)
- **File Upload:** [http://localhost:43722/file_upload](http://localhost:43722/file_upload)
- **Command Injection:** [http://localhost:43722/command_injection](http://localhost:43722/command_injection)

## 🎯 Challenges

### 1. SQL Injection Challenge
- **Difficulty:** Medium
- **Points:** 100
- **Description:** Exploit the login form to bypass authentication and access the admin's secret note.

### 2. XSS Challenge
- **Difficulty:** Medium
- **Points:** 150
- **Description:** Exploit the XSS vulnerability to capture the flag.

### 3. File Upload Challenge
- **Difficulty:** Hard
- **Points:** 200
- **Description:** Exploit the product search functionality to find hidden product keys.

### 4. Command Injection Challenge
- **Difficulty:** Hard
- **Points:** 250
- **Description:** Exploit the ping command to execute arbitrary system commands and find the flag.

## 🛑 Stopping the Platform

To stop all services and clean up containers:
```bash
./stop.sh
```

## ⚠️ Security Notice

This platform contains intentionally vulnerable applications for educational purposes only. Do not deploy in production environments or expose to the public internet. The vulnerabilities are designed to help users learn about web security concepts in a controlled environment.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework
- Docker
- PostgreSQL
- All contributors and users of this platform 