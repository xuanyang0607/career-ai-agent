#!/usr/bin/env python3
"""
Career AI Agent - Simplified Flask API for Railway Deployment
"""

import json
import re
import os
import spacy
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
from datetime import datetime
from auth import init_auth, require_auth

# Import JobSpy if available
try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    print("⚠️  JobSpy not available")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize authentication
init_auth(app)

# Initialize Google AI client
try:
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    google_model = genai.GenerativeModel(Config.GOOGLE_MODEL)
    GOOGLE_AI_CONFIGURED = True
    print(f"✅ Google AI configured")
except Exception as e:
    GOOGLE_AI_CONFIGURED = False
    google_model = None
    print(f"❌ Google AI configuration failed: {e}")

# Initialize spaCy model
try:
    nlp = spacy.load(Config.SPACY_MODEL)
    print(f"✅ spaCy model loaded")
except Exception as e:
    print(f"⚠️  spaCy model not loaded: {e}")
    nlp = None

def extract_skills_from_text(text):
    """Extract skills from text."""
    if not nlp:
        return []
    
    try:
        skills = []
        text_lower = text.lower()
        
        # Technical skills
        technical_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'machine learning', 'ai', 'data science'
        ]
        
        for skill in technical_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        return list(set(skills))
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []

def generate_intelligence_report(user_profile):
    """Generate career intelligence report."""
    if not GOOGLE_AI_CONFIGURED or not google_model:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"Based on this profile: {user_profile}, provide market intelligence, key skills, and trends. Return as JSON with keys: market_intelligence, key_skills, macro_trends"
        response = google_model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {'error': f'Failed to generate report: {str(e)}'}

def search_jobs_api(search_term, location, limit=10):
    """Search for jobs."""
    if not JOBSPY_AVAILABLE:
        return {'error': 'JobSpy not available', 'jobs': []}
    
    try:
        jobs = scrape_jobs(search_term=search_term, location=location, results_wanted=limit)
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'salary': f"${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary not specified",
                'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                'url': job.url
            })
        return {'jobs': formatted_jobs, 'total_found': len(formatted_jobs)}
    except Exception as e:
        return {'error': f'Failed to search jobs: {str(e)}', 'jobs': []}

# Routes
@app.route('/')
@require_auth
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'spacy_loaded': nlp is not None,
        'google_ai_configured': GOOGLE_AI_CONFIGURED,
        'jobspy_available': JOBSPY_AVAILABLE
    })

@app.route('/parse_resume', methods=['POST'])
@require_auth
def parse_resume():
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
        
        skills = extract_skills_from_text(resume_text)
        
        return jsonify({
            'skills': skills,
            'experience': [],
            'education': [],
            'industries': [],
            'desired_roles': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_career_intelligence', methods=['POST'])
@require_auth
def get_career_intelligence():
    try:
        data = request.get_json()
        user_profile = data.get('user_profile', '')
        
        if not user_profile:
            return jsonify({'error': 'No user profile provided'}), 400
        
        report = generate_intelligence_report(user_profile)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_jobs', methods=['POST'])
@require_auth
def search_jobs():
    try:
        data = request.get_json()
        search_term = data.get('search_term', '')
        location = data.get('location', '')
        limit = data.get('limit', 10)
        
        if not search_term:
            return jsonify({'error': 'No search term provided'}), 400
        
        results = search_jobs_api(search_term, location, limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        Config.validate_config()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
    
    print("🚀 Starting Career AI Agent...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
