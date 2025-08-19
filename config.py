"""
Configuration file for Career AI Agent
Store API keys and configuration settings securely
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Career AI Agent application."""
    
    # Google AI Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-pro')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # spaCy Configuration
    SPACY_MODEL = os.getenv('SPACY_MODEL', 'en_core_web_sm')
    
    # API Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    @staticmethod
    def validate_config():
        """Validate that required configuration is present."""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        
        return True
