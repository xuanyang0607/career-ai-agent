#!/usr/bin/env python3
"""
Generate secure credentials for production deployment
"""

import secrets
from werkzeug.security import generate_password_hash

def generate_secure_credentials():
    """Generate secure credentials for production."""
    
    print("🔐 Generating Secure Credentials for Production")
    print("=" * 50)
    
    # Generate secure secret key
    secret_key = secrets.token_hex(32)
    print(f"🔑 Secret Key: {secret_key}")
    print("   Use this as your SECRET_KEY environment variable")
    print()
    
    # Generate secure passwords
    admin_password = secrets.token_urlsafe(12)
    user1_password = secrets.token_urlsafe(12)
    user2_password = secrets.token_urlsafe(12)
    
    print("👤 User Credentials:")
    print(f"   Admin: admin / {admin_password}")
    print(f"   User1: user1 / {user1_password}")
    print(f"   User2: user2 / {user2_password}")
    print()
    
    # Generate hashed passwords for auth.py
    print("📝 Update your auth.py file with these hashed passwords:")
    print()
    print("USERS = {")
    print(f'    "admin": generate_password_hash("{admin_password}"),')
    print(f'    "user1": generate_password_hash("{user1_password}"),')
    print(f'    "user2": generate_password_hash("{user2_password}")')
    print("}")
    print()
    
    print("🌐 Environment Variables for Railway/Render:")
    print(f"GOOGLE_API_KEY=your_google_api_key_here")
    print(f"SECRET_KEY={secret_key}")
    print()
    
    print("📋 Share these credentials with your users:")
    print(f"   URL: https://your-app-name.railway.app")
    print(f"   User1: user1 / {user1_password}")
    print(f"   User2: user2 / {user2_password}")
    print()
    
    print("⚠️  IMPORTANT:")
    print("   - Save these credentials securely")
    print("   - Don't commit them to version control")
    print("   - Update auth.py before deploying")
    print("   - Set environment variables in your deployment platform")

if __name__ == "__main__":
    generate_secure_credentials()
