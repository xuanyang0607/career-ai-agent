#!/bin/bash

# 🚀 Career AI Agent Deployment Script
# This script helps you deploy to Railway

echo "🚀 Career AI Agent Deployment Script"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Career AI Agent"
fi

# Generate secure credentials
echo "🔐 Generating secure credentials..."
python3 generate_credentials.py

echo ""
echo "📋 Next Steps:"
echo "1. Update auth.py with the generated credentials"
echo "2. Push your code to GitHub:"
echo "   git remote add origin https://github.com/yourusername/career-ai-agent.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project' → 'Deploy from GitHub repo'"
echo "   - Select your repository"
echo "   - Add environment variables (GOOGLE_API_KEY, SECRET_KEY)"
echo ""
echo "4. Share the URL and credentials with your users"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
