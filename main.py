#!/usr/bin/env python3
"""
Career AI Agent - Main Application
A Python application for career analysis and guidance using AI.
"""

import os
import spacy
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CareerAIAgent:
    """Main class for the Career AI Agent application."""
    
    def __init__(self):
        """Initialize the Career AI Agent."""
        self.openai_client = None
        self.nlp_model = None
        self.setup_openai()
        self.setup_spacy()
    
    def setup_openai(self):
        """Set up OpenAI client with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully.")
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    def setup_spacy(self):
        """Set up spaCy NLP model for text processing."""
        try:
            # Try to load English model, download if not available
            self.nlp_model = spacy.load("en_core_web_sm")
            print("spaCy model loaded successfully.")
        except OSError:
            print("spaCy English model not found. Please run: python -m spacy download en_core_web_sm")
    
    def analyze_resume(self, resume_text):
        """Analyze resume text using NLP."""
        if not self.nlp_model:
            print("spaCy model not available. Please install the English model.")
            return None
        
        doc = self.nlp_model(resume_text)
        
        # Extract key information
        analysis = {
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'skills': [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']],
            'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE']
        }
        
        return analysis
    
    def get_career_advice(self, query):
        """Get career advice using OpenAI API."""
        if not self.openai_client:
            print("OpenAI client not available. Please set OPENAI_API_KEY.")
            return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful career advisor with expertise in job searching, resume writing, and professional development."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting career advice: {e}")
            return None

def main():
    """Main function to run the Career AI Agent."""
    print("🚀 Initializing Career AI Agent...")
    
    # Initialize the agent
    agent = CareerAIAgent()
    
    # Example usage
    print("\n📋 Career AI Agent is ready!")
    print("Available features:")
    print("1. Resume analysis using spaCy")
    print("2. Career advice using OpenAI GPT")
    print("3. Web requests for job data")
    
    # Example resume analysis
    sample_resume = """
    John Doe
    Software Engineer
    Experience:
    - Senior Developer at Tech Corp (2020-2023)
    - Python, JavaScript, React
    - Led team of 5 developers
    """
    
    print(f"\n📄 Analyzing sample resume...")
    analysis = agent.analyze_resume(sample_resume)
    if analysis:
        print("Resume Analysis Results:")
        print(f"Organizations: {analysis['organizations']}")
        print(f"Skills: {analysis['skills'][:5]}...")  # Show first 5 skills
    
    # Example career advice
    print(f"\n💡 Getting career advice...")
    advice = agent.get_career_advice("How can I improve my software engineering resume?")
    if advice:
        print("Career Advice:")
        print(advice)

if __name__ == "__main__":
    main()
