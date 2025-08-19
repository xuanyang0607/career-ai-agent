#!/usr/bin/env python3
"""
Simple script to run the Career AI Agent web interface
"""

import os
import sys
from app import app, Config

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import spacy
        import google.generativeai as genai
        import requests
        print("✅ All required packages are installed")
        
        # Check JobSpy availability
        try:
            from jobspy import scrape_jobs
            print("✅ JobSpy is available for real job scraping")
        except ImportError:
            print("⚠️  JobSpy not available. Install with: pip install python-jobspy")
            print("   Job search will use simulated data")
        
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_spacy_model():
    """Check if spaCy model is installed."""
    try:
        import spacy
        nlp = spacy.load(Config.SPACY_MODEL)
        print(f"✅ spaCy model '{Config.SPACY_MODEL}' is loaded")
        return True
    except OSError:
        print(f"❌ spaCy model '{Config.SPACY_MODEL}' not found")
        print(f"Please run: python -m spacy download {Config.SPACY_MODEL}")
        return False

def check_config():
    """Check if configuration is valid."""
    try:
        Config.validate_config()
        print("✅ Configuration is valid")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure GOOGLE_API_KEY is set")
        return False

def main():
    """Main function to run the web interface."""
    print("🚀 Career AI Agent Web Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check spaCy model
    if not check_spacy_model():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    print("\n🌐 Starting web interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
