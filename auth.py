"""
Simple authentication system for Career AI Agent
Allows you to control access with username/password
"""

import os
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

# Simple user management
USERS = {
    "admin": generate_password_hash("your-secure-password-here"),
    "user1": generate_password_hash("user1-password"),
    "user2": generate_password_hash("user2-password")
}

def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_auth(app):
    """Initialize authentication with the Flask app."""
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username in USERS and check_password_hash(USERS[username], password):
                session['authenticated'] = True
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Career AI Agent - Login</title>
            <style>
                body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; }
                .login-container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 350px; }
                .login-container h1 { text-align: center; color: #667eea; margin-bottom: 30px; }
                .form-group { margin-bottom: 20px; }
                .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
                .form-group input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
                .form-group input:focus { outline: none; border-color: #667eea; }
                .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; }
                .btn:hover { transform: translateY(-2px); }
                .info { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔐 Career AI Agent</h1>
                <form method="POST">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
                <div class="info">
                    <p>Contact the administrator for access credentials</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
    
    @app.route('/health')
    def health_check():
        """Health check endpoint (no auth required)."""
        return jsonify({
            'status': 'healthy',
            'timestamp': session.get('timestamp'),
            'authenticated': session.get('authenticated', False)
        })
