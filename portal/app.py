from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://ctf_user:ctf_password@db:5432/ctf_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=0)
    solved_challenges = db.relationship('SolvedChallenge', backref='user', lazy=True)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    solved_by = db.relationship('SolvedChallenge', backref='challenge', lazy=True)

class SolvedChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    solved_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_id', name='unique_solve'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Welcome back, ' + username + '!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    challenges = Challenge.query.all()
    solved_challenges = [sc.challenge_id for sc in current_user.solved_challenges]
    return render_template('dashboard.html', 
                         challenges=challenges, 
                         solved_challenges=solved_challenges)

@app.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    existing_solve = SolvedChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id
    ).first()
    
    if existing_solve:
        flash('You have already solved this challenge!', 'info')
        return redirect(url_for('dashboard'))
    
    if submitted_flag == challenge.flag:
        solved = SolvedChallenge(user_id=current_user.id, challenge_id=challenge_id)
        db.session.add(solved)
        
        current_user.score += challenge.points
        db.session.commit()
        
        flash(f'Congratulations! You solved the challenge and earned {challenge.points} points!', 'success')
    else:
        flash('Incorrect flag. Try again!', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/scoreboard')
def scoreboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('scoreboard.html', users=users)

def init_challenges():
    challenges = [
        {
            'name': 'SQL Injection - Login Bypass',
            'description': 'Try to bypass the login page using SQL injection. The flag is in the admin\'s secret note.',
            'flag': 'FLAG{sql_injection_master}',
            'points': 100
        },
        {
            'name': 'XSS Attacks',
            'description': 'Exploit the XSS vulnerability and capture the flag.',
            'flag': 'FLAG{xss_master}',
            'points': 150
        },
        {
            'name': 'File Upload Challenge',
            'description': 'Exploit the product search functionality to find hidden product keys.',
            'flag': 'FLAG{product_master}',
            'points': 200
        },
        {
            'name': 'Command Injection',
            'description': 'Exploit the ping command to execute arbitrary system commands and find the flag.',
            'flag': 'FLAG{command_injection_master}',
            'points': 250
        }
    ]
    
    for challenge_data in challenges:
        if not Challenge.query.filter_by(name=challenge_data['name']).first():
            challenge = Challenge(**challenge_data)
            db.session.add(challenge)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_challenges()
    app.run(host='0.0.0.0', port=8080) 