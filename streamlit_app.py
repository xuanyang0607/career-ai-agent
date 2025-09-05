#!/usr/bin/env python3
"""
Career AI Agent - Streamlit Version
"""

import streamlit as st
import json
import os
import google.generativeai as genai
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Career AI Agent",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'google_ai_configured' not in st.session_state:
    st.session_state.google_ai_configured = False

# Initialize Google AI
def init_google_ai():
    try:
        # Try to get API key from Streamlit secrets first, then environment
        api_key = st.secrets.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found. Please add it to Streamlit secrets or environment variables.")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        st.session_state.google_model = model
        st.session_state.google_ai_configured = True
        st.success("✅ Google AI configured")
        return True
    except Exception as e:
        st.error(f"❌ Failed to configure Google AI: {e}")
        return False

# Extract skills from text
def extract_skills_from_text(text):
    if not text:
        return []
    
    skills = []
    text_lower = text.lower()
    
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

# Generate career intelligence
def generate_intelligence_report(user_profile):
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"Based on this profile: {user_profile}, provide market intelligence, key skills, and trends. Return as JSON with keys: market_intelligence, key_skills, macro_trends"
        response = st.session_state.google_model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {'error': f'Failed to generate report: {str(e)}'}

# Main app
def main():
    st.title("🚀 Career AI Agent")
    st.write("Your AI-powered career analysis assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Setup")
        if st.button("Initialize Google AI"):
            init_google_ai()
        
        st.write(f"🤖 Google AI: {'✅ Configured' if st.session_state.google_ai_configured else '❌ Not configured'}")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📄 Resume Analysis", "🧠 Career Intelligence", "💼 Job Search"])
    
    # Tab 1: Resume Analysis
    with tab1:
        st.header("📄 Resume Analysis")
        resume_text = st.text_area("Resume Text", height=300)
        
        if st.button("Analyze Resume"):
            if resume_text:
                skills = extract_skills_from_text(resume_text)
                st.subheader("🎯 Extracted Skills")
                for skill in skills:
                    st.write(f"• {skill}")
                st.metric("Skills Found", len(skills))
            else:
                st.error("Please enter resume text")
    
    # Tab 2: Career Intelligence
    with tab2:
        st.header("🧠 Career Intelligence")
        user_profile = st.text_area("Your Career Profile", height=200)
        
        if st.button("Generate Report"):
            if user_profile:
                report = generate_intelligence_report(user_profile)
                if 'error' in report:
                    st.error(report['error'])
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📈 Market Intelligence")
                        st.write(report.get('market_intelligence', 'No data'))
                    with col2:
                        st.subheader("🔑 Key Skills")
                        for skill in report.get('key_skills', []):
                            st.write(f"• {skill}")
            else:
                st.error("Please enter your profile")
    
    # Tab 3: Job Search
    with tab3:
        st.header("💼 Job Search")
        search_term = st.text_input("Job Title")
        location = st.text_input("Location")
        
        if st.button("Search Jobs"):
            if search_term:
                st.subheader(f"Found jobs for: {search_term}")
                st.write("• Mock job result 1")
                st.write("• Mock job result 2")
            else:
                st.error("Please enter a search term")

if __name__ == "__main__":
    main()
