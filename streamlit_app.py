#!/usr/bin/env python3
"""
Career AI Agent - Streamlit Version
"""

import streamlit as st
import json
import os
import google.generativeai as genai
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Career AI Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    
    .skill-tag {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .tab-content {
        padding: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Enhanced Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 65px;
        padding: 0 28px;
        background-color: white;
        border-radius: 8px;
        border: 2px solid transparent;
        font-size: 18px;
        font-weight: 700;
        color: #495057;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8f9fa;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(45deg, #5a6fd8, #6a4190);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab content spacing */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'google_ai_configured' not in st.session_state:
    st.session_state.google_ai_configured = False

# Initialize chat session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

if 'user_profile_complete' not in st.session_state:
    st.session_state.user_profile_complete = False

if 'career_insights' not in st.session_state:
    st.session_state.career_insights = {}

if 'market_intelligence' not in st.session_state:
    st.session_state.market_intelligence = {}

if 'career_tracker' not in st.session_state:
    st.session_state.career_tracker = {
        'skills_progress': {},
        'job_applications': [],
        'learning_goals': [],
        'achievements': []
    }

# Helper functions for UI components
def display_progress_status():
    """Display progress status in sidebar"""
    completed_steps = 0
    total_steps = 5
    
    if st.session_state.get('resume_data'):
        completed_steps += 1
    if st.session_state.get('career_analysis'):
        completed_steps += 1
    if st.session_state.get('job_recommendations'):
        completed_steps += 1
    if st.session_state.get('training_recommendations'):
        completed_steps += 1
    if st.session_state.get('resume_data') and st.session_state.get('job_recommendations'):
        completed_steps += 1
    
    progress = completed_steps / total_steps
    st.progress(progress)
    st.caption(f"Progress: {completed_steps}/{total_steps} steps completed")

def display_skill_tags(skills):
    """Display skills as styled tags"""
    if skills:
        skill_html = ""
        for skill in skills:
            skill_html += f'<span class="skill-tag">{skill}</span>'
        st.markdown(skill_html, unsafe_allow_html=True)
    else:
        st.write("No skills found")

def create_metric_card(title, value, delta=None):
    """Create a styled metric card"""
    if delta:
        st.metric(title, value, delta)
    else:
        st.metric(title, value)

def display_success_message(message):
    """Display a styled success message"""
    st.markdown(f'<div class="success-card">✅ {message}</div>', unsafe_allow_html=True)

def display_info_message(message):
    """Display a styled info message"""
    st.markdown(f'<div class="info-card">ℹ️ {message}</div>', unsafe_allow_html=True)

def display_warning_message(message):
    """Display a styled warning message"""
    st.markdown(f'<div class="warning-card">⚠️ {message}</div>', unsafe_allow_html=True)

def create_skills_chart(skills_data):
    """Create a skills visualization chart"""
    if not skills_data:
        return None
    
    # Categorize skills
    technical_skills = []
    soft_skills = []
    
    technical_keywords = ['python', 'javascript', 'java', 'react', 'sql', 'aws', 'docker', 'git']
    
    for skill in skills_data:
        if any(keyword in skill.lower() for keyword in technical_keywords):
            technical_skills.append(skill)
        else:
            soft_skills.append(skill)
    
    # Create pie chart
    labels = ['Technical Skills', 'Soft Skills']
    values = [len(technical_skills), len(soft_skills)]
    colors = ['#667eea', '#764ba2']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_traces(marker=dict(colors=colors))
    fig.update_layout(
        title="Skills Distribution",
        showlegend=True,
        height=300
    )
    
    return fig

# Conversational Career Discovery Functions
def get_career_discovery_questions():
    """Get personalized career discovery questions"""
    # Check if resume data is available
    has_resume = st.session_state.get('resume_data', {})
    resume_skills = has_resume.get('skills', [])
    resume_experience = has_resume.get('years_experience', 0)
    
    if has_resume and resume_skills:
        # More contextual questions when resume is available
        questions = [
            {
                "step": 1,
                "question": f"Hi! I can see you have {resume_experience} years of experience with skills in {', '.join(resume_skills[:3])}{'...' if len(resume_skills) > 3 else ''}. How are you feeling about your career right now?",
                "type": "text",
                "options": ["Excited and motivated", "Bored and looking for change", "Stressed and uncertain", "Lost and need direction", "Confident but want growth"]
            },
            {
                "step": 2,
                "question": "Based on your background, what's your biggest career concern or challenge right now?",
                "type": "text",
                "options": ["Not sure what I'm good at", "Don't know my market value", "Worried about AI replacing my job", "Want to switch industries", "Need to upskill but don't know where to start", "Want to advance in my current field"]
            },
            {
                "step": 3,
                "question": "When you think about your ideal work environment, what matters most to you?",
                "type": "multiselect",
                "options": ["Work-life balance", "Making a positive impact", "High salary and benefits", "Creative freedom", "Job security", "Learning and growth", "Remote work flexibility", "Team collaboration"]
            },
            {
                "step": 4,
                "question": "What type of work energizes you most?",
                "type": "text",
                "options": ["Solving complex problems", "Helping others", "Creating something new", "Leading teams", "Analyzing data", "Building relationships", "Learning new things", "Making strategic decisions"]
            },
            {
                "step": 5,
                "question": "If you could wave a magic wand and have any career, what would it look like?",
                "type": "text",
                "placeholder": "Describe your dream career in 2-3 sentences..."
            }
        ]
    else:
        # Default questions when no resume is available
        questions = [
            {
                "step": 1,
                "question": "Hi! I'm your Career AI Assistant. I'm here to help you discover your true potential and find the perfect career path. Let's start with understanding your current situation. How are you feeling about your career right now?",
                "type": "text",
                "options": ["Excited and motivated", "Bored and looking for change", "Stressed and uncertain", "Lost and need direction", "Confident but want growth"]
            },
            {
                "step": 2,
                "question": "What's your biggest career concern or challenge right now?",
                "type": "text",
                "options": ["Not sure what I'm good at", "Don't know my market value", "Worried about AI replacing my job", "Want to switch industries", "Need to upskill but don't know where to start"]
            },
            {
                "step": 3,
                "question": "When you think about your ideal work environment, what matters most to you?",
                "type": "multiselect",
                "options": ["Work-life balance", "Making a positive impact", "High salary and benefits", "Creative freedom", "Job security", "Learning and growth", "Remote work flexibility", "Team collaboration"]
            },
            {
                "step": 4,
                "question": "What type of work energizes you most?",
                "type": "text",
                "options": ["Solving complex problems", "Helping others", "Creating something new", "Leading teams", "Analyzing data", "Building relationships", "Learning new things", "Making strategic decisions"]
            },
            {
                "step": 5,
                "question": "If you could wave a magic wand and have any career, what would it look like?",
                "type": "text",
                "placeholder": "Describe your dream career in 2-3 sentences..."
            }
        ]
    
    return questions

def generate_career_surprise_insights(user_responses, resume_data):
    """Generate surprising career insights based on user responses"""
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        # Format user responses for better AI understanding
        formatted_responses = []
        for response in user_responses:
            formatted_responses.append(f"Q: {response['question']}\nA: {response['response']}")
        
        responses_text = "\n\n".join(formatted_responses)
        
        # Extract key resume details for accurate analysis
        years_exp = resume_data.get('years_experience', 0)
        skills = resume_data.get('skills', [])
        job_titles = resume_data.get('job_titles', [])
        education = resume_data.get('education_level', 'Unknown')
        industries = resume_data.get('industries', [])
        
        prompt = f"""
        As a career AI expert, analyze this person's responses and resume to provide surprising, insightful career revelations.
        
        USER RESPONSES:
        {responses_text}
        
        RESUME DATA:
        Skills: {skills}
        Professional Experience: {years_exp} years (EXACTLY - do not calculate differently)
        Job Titles: {job_titles}
        Education: {education}
        Industries: {industries}
        
        CRITICAL: Use the EXACT years of professional experience provided: {years_exp} years. This is calculated from work experience only, excluding education years. Do NOT recalculate or estimate differently.
        
        IMPORTANT: You must respond with ONLY valid JSON. No additional text, explanations, or formatting outside the JSON structure.
        
        Provide surprising insights in this exact JSON format:
        {{
            "surprising_strengths": [
                {{
                    "strength": "Specific strength",
                    "evidence": "Why this is surprising based on their profile",
                    "market_value": "How this strength is valued in the market"
                }}
            ],
            "hidden_talents": [
                {{
                    "talent": "Hidden talent",
                    "description": "Why this is a hidden gem",
                    "career_applications": "How this can be leveraged"
                }}
            ],
            "market_revelations": [
                {{
                    "insight": "Surprising market insight",
                    "impact": "How this affects their career",
                    "action": "What they should do about it"
                }}
            ],
            "career_surprises": [
                {{
                    "surprise": "Unexpected career possibility",
                    "reason": "Why this is surprising for them",
                    "feasibility": "How achievable this is"
                }}
            ],
            "value_proposition": {{
                "unique_value": "What makes them uniquely valuable with {years_exp} years of professional experience",
                "employer_perception": "How employers likely see them based on their {years_exp} years of experience",
                "salary_potential": "Their earning potential considering {years_exp} years of professional experience"
            }},
            "next_surprises": "What other surprising insights await them"
        }}
        
        Focus on insights that will genuinely surprise and excite them about their potential. Make sure to return ONLY the JSON object.
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            # If JSON parsing fails, return a fallback response
            st.error(f"JSON parsing error: {json_error}")
            st.error(f"Raw response: {response_text}")
            
            # Return a structured fallback
            return {
                "surprising_strengths": [
                    {
                        "strength": "Adaptability and Growth Mindset",
                        "evidence": "Your responses show openness to change and learning",
                        "market_value": "Highly valued in today's rapidly changing job market"
                    }
                ],
                "hidden_talents": [
                    {
                        "talent": "Problem-Solving Ability",
                        "description": "Your career concerns show analytical thinking",
                        "career_applications": "Can be leveraged in consulting, product management, or operations roles"
                    }
                ],
                "market_revelations": [
                    {
                        "insight": "Career transitions are more common than ever",
                        "impact": "Your career pivot is actually a strategic advantage",
                        "action": "Focus on transferable skills and industry knowledge"
                    }
                ],
                "career_surprises": [
                    {
                        "surprise": "Your background may be perfect for emerging AI roles",
                        "reason": "Many AI roles value diverse backgrounds and fresh perspectives",
                        "feasibility": "Highly achievable with targeted upskilling"
                    }
                ],
                "value_proposition": {
                    "unique_value": "Fresh perspective with growth potential",
                    "employer_perception": "Motivated candidate ready for new challenges",
                    "salary_potential": "Strong growth potential with right role alignment"
                },
                "next_surprises": "Your career journey is just beginning - many exciting opportunities await!"
            }
        
    except Exception as e:
        st.error(f"Error in generate_career_surprise_insights: {str(e)}")
        return {'error': f'Failed to generate insights: {str(e)}'}

def generate_market_intelligence(industry, role):
    """Generate comprehensive market intelligence"""
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"""
        As a market intelligence expert, provide comprehensive market data for {industry} industry and {role} roles.
        
        Return JSON with:
        {{
            "startup_landscape": {{
                "funding_trends": "Recent funding activity and trends",
                "hot_startups": ["List of notable startups"],
                "investment_focus": "What investors are focusing on"
            }},
            "job_market": {{
                "hiring_trends": "Current hiring patterns",
                "layoff_impact": "Recent layoffs and their impact",
                "demand_forecast": "Future demand predictions",
                "competition_level": "How competitive the market is"
            }},
            "macroeconomic_factors": {{
                "regulations": "New laws and regulations affecting the industry",
                "market_forces": "Economic forces shaping the industry",
                "ai_impact": "How AI is changing the landscape",
                "global_trends": "International market trends"
            }},
            "compensation_insights": {{
                "salary_trends": "Current salary trends and changes",
                "benefits_evolution": "How benefits are changing",
                "equity_trends": "Stock options and equity trends",
                "remote_work_impact": "How remote work affects compensation"
            }},
            "culture_alignment": {{
                "company_cultures": "Types of company cultures in this space",
                "work_life_balance": "WLB trends and expectations",
                "value_alignment": "How to find culture fit",
                "diversity_initiatives": "DEI trends and initiatives"
            }},
            "newsletter_content": {{
                "key_headlines": ["Important industry news"],
                "trending_topics": ["What's trending in the industry"],
                "expert_insights": "Insights from industry experts"
            }}
        }}
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            st.error(f"JSON parsing error in market intelligence: {json_error}")
            st.error(f"Raw response: {response_text}")
            return {'error': f'Failed to parse market intelligence response: {str(json_error)}'}
        
    except Exception as e:
        return {'error': f'Failed to generate market intelligence: {str(e)}'}

def generate_career_pathway_simulation(user_profile, target_role):
    """Generate career pathway simulation with real profiles"""
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"""
        Create a career pathway simulation showing what this person's career could look like.
        
        USER PROFILE: {user_profile}
        TARGET ROLE: {target_role}
        
        Return JSON with:
        {{
            "career_trajectory": {{
                "year_1": {{"title": "Role", "salary": "$X", "skills": ["skill1", "skill2"]}},
                "year_3": {{"title": "Role", "salary": "$X", "skills": ["skill1", "skill2"]}},
                "year_5": {{"title": "Role", "salary": "$X", "skills": ["skill1", "skill2"]}},
                "year_10": {{"title": "Role", "salary": "$X", "skills": ["skill1", "skill2"]}}
            }},
            "similar_profiles": [
                {{
                    "name": "Anonymous Profile",
                    "background": "Similar background description",
                    "current_role": "Current role",
                    "journey": "How they got there",
                    "key_insights": "What made them successful"
                }}
            ],
            "milestones": [
                {{
                    "milestone": "Specific achievement",
                    "timeline": "When to achieve it",
                    "importance": "Why it matters",
                    "preparation": "How to prepare"
                }}
            ],
            "risk_factors": [
                {{
                    "risk": "Potential career risk",
                    "mitigation": "How to avoid or handle it",
                    "probability": "How likely this is"
                }}
            ]
        }}
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            st.error(f"JSON parsing error in career pathway: {json_error}")
            st.error(f"Raw response: {response_text}")
            return {'error': f'Failed to parse career pathway response: {str(json_error)}'}
        
    except Exception as e:
        return {'error': f'Failed to generate career pathway: {str(e)}'}

# Initialize Google AI
def init_google_ai():
    try:
        # Try to get API key from Streamlit secrets first, then environment
        api_key = st.secrets.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found. Please add it to Streamlit secrets or environment variables.")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.google_model = model
        st.session_state.google_ai_configured = True
        st.success("✅ Google AI configured")
        return True
    except Exception as e:
        st.error(f"❌ Failed to configure Google AI: {e}")
        return False

# Extract comprehensive resume data
def extract_resume_data(text):
    if not text:
        return {}
    
    # Enhanced skill extraction
    skills = []
    text_lower = text.lower()
    
    technical_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
        'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'machine learning', 'ai', 'data science', 'tensorflow',
        'pytorch', 'scikit-learn', 'pandas', 'numpy', 'git', 'jenkins', 'terraform'
    ]
    
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
        'strategic thinking', 'analytical', 'creative', 'adaptable', 'collaborative',
        'time management', 'organization', 'presentation', 'negotiation', 'mentoring'
    ]
    
    for skill in technical_skills + soft_skills:
        if skill in text_lower:
            skills.append(skill.title())
    
    # Extract job titles (simple pattern matching)
    job_titles = []
    title_patterns = [
        'manager', 'director', 'engineer', 'developer', 'analyst', 'consultant',
        'coordinator', 'specialist', 'lead', 'senior', 'junior', 'principal',
        'architect', 'designer', 'researcher', 'scientist', 'administrator'
    ]
    
    for pattern in title_patterns:
        if pattern in text_lower:
            job_titles.append(pattern.title())
    
    # Extract years of experience (improved pattern matching)
    import re
    years_experience = 0
    
    # Multiple patterns to catch different formats
    patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|of)',
        r'experience[:\s]*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:professional|work|industry)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:total|combined)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:proven|demonstrated)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            years_experience = int(match.group(1))
            break
    
    # If no explicit years found, try to calculate from job dates
    if years_experience == 0:
        # Look for date patterns like "03/2023 - Present", "2020-2023", "Jan 2020 - Dec 2023", etc.
        # But ONLY in professional experience sections, not education
        date_patterns = [
            r'(\d{1,2}/\d{4})\s*[-–—]\s*(\d{1,2}/\d{4})',  # 03/2023 - 02/2023
            r'(\d{1,2}/\d{4})\s*[-–—]\s*(present|current|now|ongoing)',  # 03/2023 - present
            r'(\d{4})\s*[-–—]\s*(\d{4})',  # 2020-2023
            r'(\d{4})\s*[-–—]\s*(present|current|now|ongoing)',  # 2020-present
            r'(\d{4})\s*to\s*(present|current|now|ongoing)',    # 2020 to present
        ]
        
        current_year = datetime.now().year
        all_start_years = []
        all_end_years = []
        
        # Split text into sections and only look in professional experience sections
        text_sections = re.split(r'\n\s*(?:EDUCATION|education|Education)\s*\n', text)
        professional_text = text_sections[0]  # Everything before education section
        professional_text_lower = professional_text.lower()
        
        for pattern in date_patterns:
            matches = re.findall(pattern, professional_text_lower)
            for match in matches:
                if len(match) == 2:
                    start_part, end_part = match
                    
                    # Handle start year - check for MM/YYYY format first
                    if '/' in start_part:
                        try:
                            month, year = start_part.split('/')
                            start_year = int(year)
                        except:
                            continue
                    else:
                        try:
                            start_year = int(start_part)
                        except ValueError:
                            continue
                    
                    # Handle end year - check for MM/YYYY format first
                    if '/' in end_part:
                        try:
                            month, year = end_part.split('/')
                            end_year = int(year)
                        except:
                            continue
                    elif end_part.lower() in ['present', 'current', 'now', 'ongoing']:
                        end_year = current_year
                    else:
                        try:
                            end_year = int(end_part)
                        except ValueError:
                            continue
                    
                    if start_year <= end_year <= current_year and start_year >= 1950:  # Reasonable year range
                        all_start_years.append(start_year)
                        all_end_years.append(end_year)
        
        # Also look for single years (start dates without end dates) - only in professional sections
        single_year_patterns = [
            r'(\d{4})\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # 2020 Jan
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*(\d{4})',  # Jan 2020
            r'(\d{4})\s*(?:january|february|march|april|may|june|july|august|september|october|november|december)',  # 2020 January
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s*(\d{4})',  # January 2020
        ]
        
        for pattern in single_year_patterns:
            matches = re.findall(pattern, professional_text_lower)
            for match in matches:
                try:
                    year = int(match)
                    if 1950 <= year <= current_year:
                        all_start_years.append(year)
                        # Assume it's ongoing if no end date
                        all_end_years.append(current_year)
                except ValueError:
                    continue
        
        # Calculate total career span
        if all_start_years and all_end_years:
            earliest_start = min(all_start_years)
            latest_end = max(all_end_years)
            years_experience = latest_end - earliest_start
            
            # If the span seems too long (more than 50 years), try a different approach
            if years_experience > 50:
                # Look for the most recent job and calculate from there
                recent_jobs = []
                for i, start_year in enumerate(all_start_years):
                    if i < len(all_end_years):
                        recent_jobs.append((start_year, all_end_years[i]))
                
                if recent_jobs:
                    # Sort by start year and take the most recent
                    recent_jobs.sort(key=lambda x: x[0], reverse=True)
                    most_recent_start = recent_jobs[0][0]
                    most_recent_end = recent_jobs[0][1]
                    years_experience = most_recent_end - most_recent_start
    
    # Extract education level
    education_level = "Unknown"
    if any(term in text_lower for term in ['phd', 'doctorate', 'doctoral']):
        education_level = "PhD"
    elif any(term in text_lower for term in ['master', 'mba', 'ms', 'ma']):
        education_level = "Masters"
    elif any(term in text_lower for term in ['bachelor', 'bs', 'ba', 'bsc']):
        education_level = "Bachelors"
    elif any(term in text_lower for term in ['associate', 'diploma', 'certificate']):
        education_level = "Associate/Certificate"
    
    # Extract industry (simple pattern)
    industries = []
    industry_keywords = [
        'technology', 'healthcare', 'finance', 'education', 'retail', 'manufacturing',
        'consulting', 'non-profit', 'government', 'media', 'entertainment', 'real estate'
    ]
    
    for industry in industry_keywords:
        if industry in text_lower:
            industries.append(industry.title())
    
    return {
        'skills': list(set(skills)),
        'job_titles': list(set(job_titles)),
        'years_experience': years_experience,
        'education_level': education_level,
        'industries': list(set(industries)),
        'raw_text': text
    }

# Generate comprehensive career analysis
def generate_career_analysis(resume_data, manual_preferences):
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"""
        As a career AI expert, analyze this professional profile and provide comprehensive career guidance.
        
        RESUME DATA:
        - Skills: {resume_data.get('skills', [])}
        - Job Titles: {resume_data.get('job_titles', [])}
        - Years Experience: {resume_data.get('years_experience', 0)}
        - Education: {resume_data.get('education_level', 'Unknown')}
        - Industries: {resume_data.get('industries', [])}
        - Raw Text: {resume_data.get('raw_text', '')[:1000]}...
        
        USER PREFERENCES:
        - Location: {manual_preferences.get('location', 'Not specified')}
        - Salary Min: ${manual_preferences.get('salary_min', 0):,}
        - Job Type: {manual_preferences.get('job_type', 'Not specified')}
        - Sponsorship: {manual_preferences.get('sponsorship', False)}
        - Values: {manual_preferences.get('value_alignment', [])}
        - Company Size: {manual_preferences.get('company_size', 'Not specified')}
        
        Please provide a comprehensive analysis in JSON format with these sections:
        1. "self_assessment": {{
            "strengths": ["list of key strengths"],
            "market_value": "assessment of market value",
            "perceived_value": "how employers likely perceive this candidate"
        }}
        2. "industry_alignment": {{
            "primary_industries": ["industries that align with skills"],
            "adjacent_industries": ["industries where skills could transfer"],
            "growth_opportunities": ["emerging areas of opportunity"]
        }}
        3. "role_recommendations": {{
            "immediate_roles": ["roles to apply for now"],
            "growth_roles": ["roles for career advancement"],
            "transition_roles": ["roles for career pivots"]
        }}
        4. "market_intelligence": {{
            "salary_insights": "current salary ranges and trends",
            "demand_forecast": "job market outlook",
            "ai_impact": "how AI affects this career path",
            "key_trends": ["important industry trends"]
        }}
        5. "action_plan": {{
            "immediate_actions": ["steps to take now"],
            "skill_gaps": ["areas to develop"],
            "networking_strategy": "how to build relevant connections",
            "timeline": "realistic timeline for career goals"
        }}
        6. "resume_improvements": {{
            "strengths_to_highlight": ["what to emphasize"],
            "weaknesses_to_address": ["what to improve"],
            "formatting_suggestions": ["resume structure advice"],
            "keyword_optimization": ["important keywords to include"]
        }}
        
        Focus on actionable, specific advice that addresses career transition concerns and AI impact.
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            st.error(f"JSON parsing error in career analysis: {json_error}")
            st.error(f"Raw response: {response_text}")
            return {'error': f'Failed to parse career analysis response: {str(json_error)}'}
        
    except Exception as e:
        return {'error': f'Failed to generate analysis: {str(e)}'}

# Generate job recommendations
def generate_job_recommendations(resume_data, manual_preferences):
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        prompt = f"""
        Based on this profile, recommend specific jobs this person should apply to RIGHT NOW.
        
        PROFILE: {resume_data}
        PREFERENCES: {manual_preferences}
        
        Return JSON with:
        {{
            "recommended_jobs": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "location": "Location",
                    "salary_range": "Salary Range",
                    "match_score": "Why this is a good fit",
                    "application_tips": "How to stand out",
                    "company_culture": "What to know about culture",
                    "growth_potential": "Career growth opportunities",
                    "ai_relevance": "How AI affects this role",
                    "job_description": "Key responsibilities and requirements",
                    "required_skills": ["skill1", "skill2", "skill3"],
                    "preferred_skills": ["skill1", "skill2", "skill3"]
                }}
            ],
            "application_strategy": "Overall approach to applications",
            "timeline": "When to apply and follow up"
        }}
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            st.error(f"JSON parsing error in job recommendations: {json_error}")
            st.error(f"Raw response: {response_text}")
            return {'error': f'Failed to parse job recommendations response: {str(json_error)}'}
        
    except Exception as e:
        return {'error': f'Failed to generate job recommendations: {str(e)}'}

# Generate training materials and projects
def generate_training_recommendations(resume_data, job_recommendations):
    if not st.session_state.google_ai_configured:
        return {'error': 'Google AI not configured'}
    
    try:
        # Extract skills from recommended jobs
        all_required_skills = []
        all_preferred_skills = []
        job_titles = []
        
        if 'recommended_jobs' in job_recommendations:
            for job in job_recommendations['recommended_jobs']:
                all_required_skills.extend(job.get('required_skills', []))
                all_preferred_skills.extend(job.get('preferred_skills', []))
                job_titles.append(job.get('title', ''))
        
        current_skills = resume_data.get('skills', [])
        years_experience = resume_data.get('years_experience', 0)
        
        prompt = f"""
        As a career development expert, create a comprehensive learning and project plan for this candidate.
        
        CANDIDATE PROFILE:
        - Current Skills: {current_skills}
        - Years Experience: {years_experience}
        - Education: {resume_data.get('education_level', 'Unknown')}
        - Target Job Titles: {job_titles}
        
        TARGET JOB REQUIREMENTS:
        - Required Skills: {list(set(all_required_skills))}
        - Preferred Skills: {list(set(all_preferred_skills))}
        
        Create a personalized learning plan in JSON format:
        {{
            "skill_gaps": [
                {{
                    "skill": "Skill Name",
                    "current_level": "Beginner/Intermediate/Advanced",
                    "target_level": "Intermediate/Advanced/Expert",
                    "priority": "High/Medium/Low",
                    "time_to_learn": "2-4 weeks",
                    "learning_resources": [
                        {{
                            "type": "Course/Book/Video/Tutorial",
                            "title": "Resource Title",
                            "provider": "Coursera/YouTube/Book/etc",
                            "url": "https://example.com",
                            "duration": "10 hours",
                            "cost": "Free/$99/etc",
                            "description": "What you'll learn"
                        }}
                    ]
                }}
            ],
            "simulated_projects": [
                {{
                    "project_name": "Project Title",
                    "description": "What this project demonstrates",
                    "skills_demonstrated": ["skill1", "skill2"],
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "time_required": "2-4 weeks",
                    "deliverables": ["deliverable1", "deliverable2"],
                    "github_template": "https://github.com/example/template",
                    "portfolio_impact": "How this improves your resume",
                    "step_by_step_guide": [
                        "Step 1: Setup and planning",
                        "Step 2: Implementation",
                        "Step 3: Testing and deployment"
                    ]
                }}
            ],
            "learning_timeline": {{
                "week_1_2": ["Focus on high-priority skills"],
                "week_3_4": ["Start first project"],
                "week_5_6": ["Complete project, start second"],
                "week_7_8": ["Portfolio building and refinement"]
            }},
            "portfolio_enhancement": {{
                "resume_additions": ["What to add to resume"],
                "linkedin_updates": ["How to update LinkedIn"],
                "github_showcase": ["How to present projects"],
                "case_studies": ["What case studies to create"]
            }},
            "certification_recommendations": [
                {{
                    "certification": "Certification Name",
                    "provider": "AWS/Google/Microsoft/etc",
                    "relevance": "Why this matters for target roles",
                    "cost": "$99",
                    "duration": "3 months",
                    "exam_info": "What the exam covers"
                }}
            ]
        }}
        
        Focus on practical, actionable learning that directly improves job prospects.
        Prioritize skills that appear in multiple job requirements.
        """
        
        response = st.session_state.google_model.generate_content(prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as json_error:
            st.error(f"JSON parsing error in training recommendations: {json_error}")
            st.error(f"Raw response: {response_text}")
            return {'error': f'Failed to parse training recommendations response: {str(json_error)}'}
        
    except Exception as e:
        return {'error': f'Failed to generate training recommendations: {str(e)}'}

# Main app
def main():
    # Main header with gradient styling
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Career AI Agent</h1>
        <p style="font-size: 1.2rem; margin: 0;">Your comprehensive AI-powered career analysis and job search assistant</p>
        <p style="font-size: 1rem; margin: 0.5rem 0 0 0; opacity: 0.9;">Navigate career shifts with AI insights, find your perfect role, and get actionable career guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Setup & Status")
        
        # AI Configuration Status
        if st.session_state.google_ai_configured:
            display_success_message("Google AI Configured")
        else:
            display_warning_message("Google AI Not Configured")
            if st.button("🔑 Initialize Google AI", type="primary"):
                init_google_ai()
        
        st.markdown("---")
        
        # Progress Status
        st.markdown("### 📊 Your Progress")
        display_progress_status()
        
        st.markdown("---")
        
        # Quick Start Guide
        st.markdown("### 📋 Quick Start Guide")
        steps = [
            "📄 Upload your resume",
            "🎯 Set your preferences", 
            "🧠 Get career analysis",
            "💼 Find job recommendations",
            "📚 Get training materials"
        ]
        
        for i, step in enumerate(steps, 1):
            if i == 1 and st.session_state.get('resume_data'):
                st.markdown(f"✅ {step}")
            elif i == 2 and st.session_state.get('manual_preferences'):
                st.markdown(f"✅ {step}")
            elif i == 3 and st.session_state.get('career_analysis'):
                st.markdown(f"✅ {step}")
            elif i == 4 and st.session_state.get('job_recommendations'):
                st.markdown(f"✅ {step}")
            elif i == 5 and st.session_state.get('training_recommendations'):
                st.markdown(f"✅ {step}")
            else:
                st.markdown(f"⏳ {step}")
        
        st.markdown("---")
        
        # Quick Stats
        if st.session_state.get('resume_data'):
            st.markdown("### 📈 Quick Stats")
            resume_data = st.session_state.resume_data
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Skills", len(resume_data.get('skills', [])))
            with col2:
                st.metric("Experience", f"{resume_data.get('years_experience', 0)} years")
    
    # Main content with enhanced tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🤖 Career Discovery Chat", 
        "🎯 Career Insights", 
        "💼 Job Recommendations", 
        "📈 Market Intelligence",
        "🛠️ Resume Improvement",
        "📚 Training & Projects",
        "🏆 Career Tracker"
    ])
    
    # Tab 1: Career Discovery Chat
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.header("🤖 Career Discovery Chat")
        st.write("Let's have a conversation to discover your true potential and surprise you with insights about your career!")
        
        # Resume upload and analysis section
        st.subheader("📄 Upload & Analyze Your Resume")
        st.write("Upload your resume for comprehensive analysis and personalized career insights!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            resume_text_chat = st.text_area(
                "Paste your resume text here", 
                height=300,
                placeholder="Paste your complete resume text including work experience, education, skills, and achievements...",
                key="resume_chat_input"
            )
        
        with col2:
            uploaded_file_chat = st.file_uploader(
                "Or upload a file", 
                type=['txt', 'pdf', 'docx'],
                help="Upload your resume file for easier processing",
                key="resume_chat_file"
            )
            
            if uploaded_file_chat:
                st.info(f"📁 File uploaded: {uploaded_file_chat.name}")
        
        # Process resume if provided
        if resume_text_chat:
            if st.button("🔍 Analyze Resume", key="analyze_resume_chat", type="primary"):
                with st.spinner("🤖 AI is analyzing your resume and generating insights..."):
                    resume_data = extract_resume_data(resume_text_chat)
                    st.session_state.resume_data = resume_data
                    display_success_message("Resume analysis complete! Your profile has been processed.")
                    st.rerun()  # Refresh to show updated questions
        
        # Show comprehensive resume analysis if available
        if st.session_state.get('resume_data'):
            resume_data = st.session_state.resume_data
            
            # Enhanced metrics display
            st.subheader("📊 Your Profile Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card("Skills Found", len(resume_data.get('skills', [])))
            with col2:
                create_metric_card("Years Experience", resume_data.get('years_experience', 0))
            with col3:
                create_metric_card("Education Level", resume_data.get('education_level', 'Unknown'))
            with col4:
                create_metric_card("Industries", len(resume_data.get('industries', [])))
            
            # Skills visualization
            if resume_data.get('skills'):
                st.subheader("🎯 Skills Analysis")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Your Skills:**")
                    display_skill_tags(resume_data.get('skills', []))
                
                with col2:
                    # Skills distribution chart
                    skills_chart = create_skills_chart(resume_data.get('skills', []))
                    if skills_chart:
                        st.plotly_chart(skills_chart, use_container_width=True)
            
            # Detailed information in expandable sections
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("💼 Job Titles & Experience", expanded=True):
                    if resume_data.get('job_titles'):
                        for title in resume_data.get('job_titles', []):
                            st.write(f"• {title}")
                    else:
                        st.write("No specific job titles detected")
                    
                    if resume_data.get('years_experience', 0) > 0:
                        st.write(f"**Total Experience:** {resume_data.get('years_experience', 0)} years")
            
            with col2:
                with st.expander("🏭 Industries & Education", expanded=True):
                    if resume_data.get('industries'):
                        st.write("**Industries:**")
                        for industry in resume_data.get('industries', []):
                            st.write(f"• {industry}")
                    
                    if resume_data.get('education_level') != 'Unknown':
                        st.write(f"**Education:** {resume_data.get('education_level', 'Unknown')}")
            
            # Career preferences section
            st.subheader("🎯 Your Career Preferences")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📍 Location & Compensation**")
                location = st.text_input(
                    "Preferred Location", 
                    value="California", 
                    help="Where do you want to work?",
                    placeholder="e.g., San Francisco, Remote, New York",
                    key="pref_location"
                )
                salary_min = st.number_input(
                    "Minimum Salary ($)", 
                    value=200000, 
                    step=10000, 
                    min_value=0,
                    help="Your minimum acceptable salary",
                    key="pref_salary"
                )
            
            with col2:
                st.markdown("**💼 Job Details**")
                job_type = st.selectbox(
                    "Job Type",
                    ["Full time", "Part time", "Contract", "Intern", "Remote", "Hybrid"],
                    help="What type of employment are you looking for?",
                    key="pref_job_type"
                )
                
                sponsorship = st.checkbox("Need Visa Sponsorship", value=False, help="Do you require visa sponsorship?", key="pref_sponsorship")
            
            # Company values
            st.markdown("**🏢 Company Culture**")
            value_options = [
                "Work-life balance", "Transparency", "Impact", "Innovation", 
                "Diversity", "Growth", "Stability", "Social responsibility"
            ]
            value_alignment = st.multiselect(
                "What matters most to you?",
                value_options,
                default=["Work-life balance", "Transparency", "Impact"],
                help="Select the values that are most important to you",
                key="pref_values"
            )
            
            company_size = st.selectbox(
                "Preferred Company Size",
                ["Startup (1-50)", "Small (10-500)", "Medium (500-5000)", "Large (5000+)", "Any"],
                help="What size company do you prefer?",
                key="pref_company_size"
            )
            
            # Store preferences in session state
            st.session_state.manual_preferences = {
                "location": location,
                "salary_min": salary_min,
                "job_type": job_type,
                "sponsorship": sponsorship,
                "value_alignment": value_alignment,
                "company_size": company_size
            }
        
        st.markdown("---")
        
        # Chat interface
        if not st.session_state.user_profile_complete:
            # Check if Google AI is configured before starting chat
            if not st.session_state.google_ai_configured:
                st.markdown("""
                <div class="warning-card">
                    <strong>⚠️ Setup Required</strong><br>
                    Please configure Google AI in the sidebar before starting the career discovery chat.
                </div>
                """, unsafe_allow_html=True)
                
                st.info("🔧 **Next Step:** Click 'Initialize Google AI' in the sidebar, then come back to start your career discovery journey!")
                
                # Show what the chat will do
                st.subheader("🎯 What This Chat Will Do")
                st.markdown("""
                The Career Discovery Chat will:
                1. **Ask you 5 personalized questions** about your career goals and challenges
                2. **Analyze your responses** using AI to find surprising insights
                3. **Reveal hidden talents** and strengths you didn't know you had
                4. **Show market opportunities** tailored to your profile
                5. **Provide actionable next steps** for your career journey
                """)
                
                st.markdown("---")
                st.subheader("🚀 Ready to Get Started?")
                st.write("Once you've configured Google AI in the sidebar, you can begin your personalized career discovery journey!")
            else:
                questions = get_career_discovery_questions()
                current_question = questions[st.session_state.current_step]
                
                st.markdown(f"""
                <div class="info-card">
                    <strong>Question {st.session_state.current_step + 1} of {len(questions)}</strong><br>
                    {current_question['question']}
                </div>
                """, unsafe_allow_html=True)
            
                # Question response interface
                if current_question['type'] == 'text':
                    if current_question.get('options'):
                        response = st.radio("Your answer:", current_question['options'], key=f"q{st.session_state.current_step}")
                    else:
                        response = st.text_area(
                            "Your answer:", 
                            placeholder=current_question.get('placeholder', ''),
                            key=f"q{st.session_state.current_step}"
                        )
                elif current_question['type'] == 'multiselect':
                    response = st.multiselect(
                        "Select all that apply:", 
                        current_question['options'],
                        key=f"q{st.session_state.current_step}"
                    )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("Next Question", type="primary", use_container_width=True):
                        if response:
                            # Store response
                            if 'user_responses' not in st.session_state:
                                st.session_state.user_responses = []
                            st.session_state.user_responses.append({
                                'question': current_question['question'],
                                'response': response
                            })
                            
                            # Move to next question
                            if st.session_state.current_step < len(questions) - 1:
                                st.session_state.current_step += 1
                                st.rerun()
                            else:
                                # All questions answered, generate insights
                                st.session_state.user_profile_complete = True
                                st.rerun()
                        else:
                            st.warning("Please provide an answer before continuing.")
                
                # Show progress
                progress = (st.session_state.current_step + 1) / len(questions)
                st.progress(progress)
                st.caption(f"Progress: {st.session_state.current_step + 1}/{len(questions)} questions completed")
        
        else:
            # Check if Google AI is configured before generating insights
            if not st.session_state.google_ai_configured:
                st.markdown("""
                <div class="warning-card">
                    <strong>⚠️ Google AI Not Configured</strong><br>
                    Please configure Google AI in the sidebar to generate career insights.
                </div>
                """, unsafe_allow_html=True)
                
                st.info("🔧 **Setup Required:** Click 'Initialize Google AI' in the sidebar to get started!")
                
                # Show a preview of what insights would look like
                st.subheader("🎯 Preview: What You'll Discover")
                st.markdown("""
                Once Google AI is configured, you'll get insights like:
                - 💪 **Surprising Strengths** you didn't know you had
                - 🎯 **Hidden Talents** that can advance your career
                - 📊 **Market Revelations** about your field
                - 🚀 **Career Surprises** - unexpected opportunities
                - 💰 **Your Value Proposition** in the job market
                """)
                
                if st.button("🔄 Start Over", type="secondary"):
                    st.session_state.user_profile_complete = False
                    st.session_state.current_step = 0
                    st.session_state.user_responses = []
                    st.session_state.career_surprise_insights = {}
                    st.rerun()
            else:
                # Generate and display career insights
                if 'career_surprise_insights' not in st.session_state:
                    with st.spinner("🤖 Analyzing your responses and generating surprising insights..."):
                        insights = generate_career_surprise_insights(
                            st.session_state.user_responses,
                            st.session_state.get('resume_data', {})
                        )
                        st.session_state.career_surprise_insights = insights
            
            insights = st.session_state.career_surprise_insights
            
            if 'error' not in insights:
                st.markdown("""
                <div class="success-card">
                    <h3>🎉 Your Career Discovery Results!</h3>
                    <p>Here are some surprising insights about your career potential:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Surprising Strengths
                if 'surprising_strengths' in insights:
                    st.subheader("💪 Your Surprising Strengths")
                    for strength in insights['surprising_strengths']:
                        with st.expander(f"✨ {strength.get('strength', 'Strength')}"):
                            st.write(f"**Evidence:** {strength.get('evidence', 'No evidence provided')}")
                            st.write(f"**Market Value:** {strength.get('market_value', 'No market value info')}")
                
                # Hidden Talents
                if 'hidden_talents' in insights:
                    st.subheader("🎯 Hidden Talents")
                    for talent in insights['hidden_talents']:
                        with st.expander(f"💎 {talent.get('talent', 'Talent')}"):
                            st.write(f"**Description:** {talent.get('description', 'No description')}")
                            st.write(f"**Career Applications:** {talent.get('career_applications', 'No applications info')}")
                
                # Market Revelations
                if 'market_revelations' in insights:
                    st.subheader("📊 Market Revelations")
                    for revelation in insights['market_revelations']:
                        with st.expander(f"🔍 {revelation.get('insight', 'Insight')}"):
                            st.write(f"**Impact:** {revelation.get('impact', 'No impact info')}")
                            st.write(f"**Action:** {revelation.get('action', 'No action info')}")
                
                # Career Surprises
                if 'career_surprises' in insights:
                    st.subheader("🚀 Career Surprises")
                    for surprise in insights['career_surprises']:
                        with st.expander(f"🎪 {surprise.get('surprise', 'Surprise')}"):
                            st.write(f"**Why Surprising:** {surprise.get('reason', 'No reason provided')}")
                            st.write(f"**Feasibility:** {surprise.get('feasibility', 'No feasibility info')}")
                
                # Value Proposition
                if 'value_proposition' in insights:
                    st.subheader("💰 Your Value Proposition")
                    vp = insights['value_proposition']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Unique Value", vp.get('unique_value', 'Not specified'))
                    with col2:
                        st.metric("Employer Perception", vp.get('employer_perception', 'Not specified'))
                    with col3:
                        st.metric("Salary Potential", vp.get('salary_potential', 'Not specified'))
                
                # Next Steps
                st.markdown("---")
                st.subheader("🎯 Ready for More Surprises?")
                st.markdown("""
                <div class="info-card">
                    <strong>Your journey has just begun!</strong><br>
                    Now that you've discovered your surprising potential, explore:
                    <ul>
                        <li>📄 Detailed resume analysis</li>
                        <li>💼 Personalized job recommendations</li>
                        <li>📈 Market intelligence for your field</li>
                        <li>📚 Custom training and projects</li>
                        <li>🏆 Track your career progress</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Reset button
                if st.button("🔄 Start Over", type="secondary"):
                    st.session_state.user_profile_complete = False
                    st.session_state.current_step = 0
                    st.session_state.user_responses = []
                    st.session_state.career_surprise_insights = {}
                    st.rerun()
            else:
                st.error(f"Error generating insights: {insights['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Career Insights
    with tab2:
        st.header("🧠 Comprehensive Career Analysis")
        
        if 'resume_data' in st.session_state and 'manual_preferences' in st.session_state:
            if st.button("🚀 Generate Career Analysis", type="primary"):
                with st.spinner("Generating comprehensive career analysis..."):
                    analysis = generate_career_analysis(
                        st.session_state.resume_data, 
                        st.session_state.manual_preferences
                    )
                    
                    if 'error' in analysis:
                        st.error(analysis['error'])
                    else:
                        st.session_state.career_analysis = analysis
                        st.success("✅ Career analysis complete!")
            
            if 'career_analysis' in st.session_state:
                analysis = st.session_state.career_analysis
                
                # Self Assessment
                if 'self_assessment' in analysis:
                    st.subheader("🔍 Self Assessment")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Your Strengths:**")
                        for strength in analysis['self_assessment'].get('strengths', []):
                            st.write(f"• {strength}")
                    with col2:
                        st.write("**Market Value:**")
                        st.write(analysis['self_assessment'].get('market_value', 'Not available'))
                
                # Industry Alignment
                if 'industry_alignment' in analysis:
                    st.subheader("🏭 Industry Alignment")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Primary Industries:**")
                        for industry in analysis['industry_alignment'].get('primary_industries', []):
                            st.write(f"• {industry}")
                    with col2:
                        st.write("**Adjacent Industries:**")
                        for industry in analysis['industry_alignment'].get('adjacent_industries', []):
                            st.write(f"• {industry}")
                    with col3:
                        st.write("**Growth Opportunities:**")
                        for opp in analysis['industry_alignment'].get('growth_opportunities', []):
                            st.write(f"• {opp}")
                
                # Role Recommendations
                if 'role_recommendations' in analysis:
                    st.subheader("🎯 Role Recommendations")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Apply Now:**")
                        for role in analysis['role_recommendations'].get('immediate_roles', []):
                            st.write(f"• {role}")
                    with col2:
                        st.write("**Growth Roles:**")
                        for role in analysis['role_recommendations'].get('growth_roles', []):
                            st.write(f"• {role}")
                    with col3:
                        st.write("**Transition Roles:**")
                        for role in analysis['role_recommendations'].get('transition_roles', []):
                            st.write(f"• {role}")
            else:
                st.info("👆 Please complete the Resume Analysis first to get career insights")
    
    # Tab 3: Job Recommendations
    with tab3:
        st.header("💼 Personalized Job Recommendations")
        
        if 'resume_data' in st.session_state and 'manual_preferences' in st.session_state:
            if st.button("🎯 Find Jobs for Me", type="primary"):
                with st.spinner("Finding personalized job recommendations..."):
                    jobs = generate_job_recommendations(
                        st.session_state.resume_data,
                        st.session_state.manual_preferences
                    )
                    
                    if 'error' in jobs:
                        st.error(jobs['error'])
                    else:
                        st.session_state.job_recommendations = jobs
                        st.success("✅ Job recommendations ready!")
            
            if 'job_recommendations' in st.session_state:
                jobs = st.session_state.job_recommendations
                
                if 'recommended_jobs' in jobs:
                    st.subheader("🎯 Recommended Jobs")
                    for i, job in enumerate(jobs['recommended_jobs']):
                        with st.expander(f"💼 {job.get('title', 'Job Title')} at {job.get('company', 'Company')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                                st.write(f"**Salary:** {job.get('salary_range', 'Not specified')}")
                                st.write(f"**Match Score:** {job.get('match_score', 'Not specified')}")
                            with col2:
                                st.write(f"**Company Culture:** {job.get('company_culture', 'Not specified')}")
                                st.write(f"**Growth Potential:** {job.get('growth_potential', 'Not specified')}")
                                st.write(f"**AI Relevance:** {job.get('ai_relevance', 'Not specified')}")
                            
                            st.write(f"**Application Tips:** {job.get('application_tips', 'Not specified')}")
                
                if 'application_strategy' in jobs:
                    st.subheader("📋 Application Strategy")
                    st.write(jobs['application_strategy'])
        else:
            st.info("👆 Please complete the Resume Analysis first to get job recommendations")
    
    # Tab 4: Market Intelligence
    with tab4:
        st.header("📈 Market Intelligence & AI Impact")
        
        if 'career_analysis' in st.session_state:
            analysis = st.session_state.career_analysis
            
            if 'market_intelligence' in analysis:
                market = analysis['market_intelligence']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("💰 Salary Insights")
                    st.write(market.get('salary_insights', 'Not available'))
                    
                    st.subheader("🔮 Demand Forecast")
                    st.write(market.get('demand_forecast', 'Not available'))
                
                with col2:
                    st.subheader("🤖 AI Impact")
                    st.write(market.get('ai_impact', 'Not available'))
                    
                    st.subheader("📊 Key Trends")
                    for trend in market.get('key_trends', []):
                        st.write(f"• {trend}")
            
            if 'action_plan' in analysis:
                st.subheader("🎯 Action Plan")
                plan = analysis['action_plan']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Immediate Actions:**")
                    for action in plan.get('immediate_actions', []):
                        st.write(f"• {action}")
                    
                    st.write("**Skill Gaps to Address:**")
                    for gap in plan.get('skill_gaps', []):
                        st.write(f"• {gap}")
                
                with col2:
                    st.write("**Networking Strategy:**")
                    st.write(plan.get('networking_strategy', 'Not available'))
                    
                    st.write("**Timeline:**")
                    st.write(plan.get('timeline', 'Not available'))
        else:
            st.info("👆 Please complete the Resume Analysis first to get market intelligence")
    
    # Tab 5: Resume Improvement
    with tab5:
        st.header("🛠️ Resume Improvement & Optimization")
        
        if 'career_analysis' in st.session_state:
            analysis = st.session_state.career_analysis
            
            if 'resume_improvements' in analysis:
                improvements = analysis['resume_improvements']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✨ Strengths to Highlight")
                    for strength in improvements.get('strengths_to_highlight', []):
                        st.write(f"• {strength}")
                    
                    st.subheader("🔧 Areas to Improve")
                    for weakness in improvements.get('weaknesses_to_address', []):
                        st.write(f"• {weakness}")
                
                with col2:
                    st.subheader("📝 Formatting Suggestions")
                    for suggestion in improvements.get('formatting_suggestions', []):
                        st.write(f"• {suggestion}")
                    
                    st.subheader("🔑 Keywords to Include")
                    for keyword in improvements.get('keyword_optimization', []):
                        st.write(f"• {keyword}")
                
                st.info("💡 **Note:** This resume was improved with AI assistance. Make sure to mention 'Resume enhanced with AI assistance' in your applications to maintain transparency.")
        else:
            st.info("👆 Please complete the Resume Analysis first to get resume improvement suggestions")
    
    # Tab 6: Training & Projects
    with tab6:
        st.header("📚 Personalized Training & Project Recommendations")
        st.write("Get customized learning materials and simulated projects to bridge skill gaps and enhance your portfolio.")
        
        if 'resume_data' in st.session_state and 'job_recommendations' in st.session_state:
            if st.button("🎓 Generate Learning Plan", type="primary"):
                with st.spinner("Creating personalized training and project recommendations..."):
                    training = generate_training_recommendations(
                        st.session_state.resume_data,
                        st.session_state.job_recommendations
                    )
                    
                    if 'error' in training:
                        st.error(training['error'])
                    else:
                        st.session_state.training_recommendations = training
                        st.success("✅ Learning plan ready!")
            
            if 'training_recommendations' in st.session_state:
                training = st.session_state.training_recommendations
                
                # Skill Gaps Section
                if 'skill_gaps' in training:
                    st.subheader("🎯 Skill Gaps to Address")
                    for i, gap in enumerate(training['skill_gaps']):
                        with st.expander(f"📖 {gap.get('skill', 'Skill')} - Priority: {gap.get('priority', 'Medium')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Current Level:** {gap.get('current_level', 'Unknown')}")
                                st.write(f"**Target Level:** {gap.get('target_level', 'Unknown')}")
                                st.write(f"**Time to Learn:** {gap.get('time_to_learn', 'Unknown')}")
                            with col2:
                                st.write(f"**Priority:** {gap.get('priority', 'Medium')}")
                            
                            st.subheader("📚 Learning Resources")
                            for resource in gap.get('learning_resources', []):
                                st.write(f"**{resource.get('type', 'Resource')}:** {resource.get('title', 'Title')}")
                                st.write(f"  - Provider: {resource.get('provider', 'Unknown')}")
                                st.write(f"  - Duration: {resource.get('duration', 'Unknown')}")
                                st.write(f"  - Cost: {resource.get('cost', 'Unknown')}")
                                st.write(f"  - Description: {resource.get('description', 'No description')}")
                                if resource.get('url'):
                                    st.write(f"  - [Link]({resource.get('url')})")
                                st.write("---")
                
                # Simulated Projects Section
                if 'simulated_projects' in training:
                    st.subheader("🚀 Simulated Projects for Portfolio")
                    for i, project in enumerate(training['simulated_projects']):
                        with st.expander(f"💻 {project.get('project_name', 'Project')} - {project.get('difficulty', 'Intermediate')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Description:** {project.get('description', 'No description')}")
                                st.write(f"**Time Required:** {project.get('time_required', 'Unknown')}")
                                st.write(f"**Skills Demonstrated:**")
                                for skill in project.get('skills_demonstrated', []):
                                    st.write(f"  • {skill}")
                            with col2:
                                st.write(f"**Portfolio Impact:** {project.get('portfolio_impact', 'No info')}")
                                if project.get('github_template'):
                                    st.write(f"**Template:** [GitHub]({project.get('github_template')})")
                            
                            st.subheader("📋 Step-by-Step Guide")
                            for step in project.get('step_by_step_guide', []):
                                st.write(f"• {step}")
                            
                            st.subheader("📦 Deliverables")
                            for deliverable in project.get('deliverables', []):
                                st.write(f"• {deliverable}")
                
                # Learning Timeline
                if 'learning_timeline' in training:
                    st.subheader("📅 Learning Timeline")
                    timeline = training['learning_timeline']
                    for week, activities in timeline.items():
                        st.write(f"**{week.replace('_', ' ').title()}:**")
                        for activity in activities:
                            st.write(f"  • {activity}")
                
                # Portfolio Enhancement
                if 'portfolio_enhancement' in training:
                    st.subheader("💼 Portfolio Enhancement Strategy")
                    enhancement = training['portfolio_enhancement']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Resume Additions:**")
                        for addition in enhancement.get('resume_additions', []):
                            st.write(f"• {addition}")
                        
                        st.write("**LinkedIn Updates:**")
                        for update in enhancement.get('linkedin_updates', []):
                            st.write(f"• {update}")
                    
                    with col2:
                        st.write("**GitHub Showcase:**")
                        for showcase in enhancement.get('github_showcase', []):
                            st.write(f"• {showcase}")
                        
                        st.write("**Case Studies:**")
                        for case in enhancement.get('case_studies', []):
                            st.write(f"• {case}")
                
                # Certifications
                if 'certification_recommendations' in training:
                    st.subheader("🏆 Recommended Certifications")
                    for cert in training['certification_recommendations']:
                        with st.expander(f"🎖️ {cert.get('certification', 'Certification')} - {cert.get('provider', 'Provider')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Provider:** {cert.get('provider', 'Unknown')}")
                                st.write(f"**Cost:** {cert.get('cost', 'Unknown')}")
                                st.write(f"**Duration:** {cert.get('duration', 'Unknown')}")
                            with col2:
                                st.write(f"**Relevance:** {cert.get('relevance', 'No info')}")
                                st.write(f"**Exam Info:** {cert.get('exam_info', 'No info')}")
        else:
            st.info("👆 Please complete the Resume Analysis and Job Recommendations first to get personalized training materials")
            
            if 'resume_data' not in st.session_state:
                st.warning("⚠️ Complete Resume Analysis first")
            if 'job_recommendations' not in st.session_state:
                st.warning("⚠️ Generate Job Recommendations first")
    
    # Tab 7: Career Tracker
    with tab7:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.header("🏆 Career Progress Tracker")
        st.write("Track your career journey, monitor your progress, and celebrate your achievements!")
        
        # Career Tracker Dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Skills Learned", len(st.session_state.career_tracker.get('skills_progress', {})))
        with col2:
            st.metric("Jobs Applied", len(st.session_state.career_tracker.get('job_applications', [])))
        with col3:
            st.metric("Learning Goals", len(st.session_state.career_tracker.get('learning_goals', [])))
        with col4:
            st.metric("Achievements", len(st.session_state.career_tracker.get('achievements', [])))
        
        # Skills Progress
        st.subheader("📈 Skills Progress")
        if st.session_state.career_tracker.get('skills_progress'):
            for skill, progress in st.session_state.career_tracker['skills_progress'].items():
                st.write(f"**{skill}:** {progress}%")
                st.progress(progress / 100)
        else:
            st.info("Complete some training to track your skills progress!")
        
        # Job Applications Tracker
        st.subheader("💼 Job Applications")
        if st.button("➕ Add Job Application", type="primary"):
            with st.form("add_job_application"):
                company = st.text_input("Company")
                position = st.text_input("Position")
                status = st.selectbox("Status", ["Applied", "Interview", "Rejected", "Offer"])
                date = st.date_input("Date")
                
                if st.form_submit_button("Add Application"):
                    if company and position:
                        st.session_state.career_tracker['job_applications'].append({
                            'company': company,
                            'position': position,
                            'status': status,
                            'date': str(date)
                        })
                        st.success("Job application added!")
                        st.rerun()
        
        # Display job applications
        if st.session_state.career_tracker.get('job_applications'):
            for i, app in enumerate(st.session_state.career_tracker['job_applications']):
                with st.expander(f"{app['company']} - {app['position']} ({app['status']})"):
                    st.write(f"**Date:** {app['date']}")
                    st.write(f"**Status:** {app['status']}")
        
        # Learning Goals
        st.subheader("🎯 Learning Goals")
        if st.button("➕ Add Learning Goal", type="secondary"):
            with st.form("add_learning_goal"):
                goal = st.text_input("Learning Goal")
                deadline = st.date_input("Deadline")
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                
                if st.form_submit_button("Add Goal"):
                    if goal:
                        st.session_state.career_tracker['learning_goals'].append({
                            'goal': goal,
                            'deadline': str(deadline),
                            'priority': priority,
                            'completed': False
                        })
                        st.success("Learning goal added!")
                        st.rerun()
        
        # Display learning goals
        if st.session_state.career_tracker.get('learning_goals'):
            for i, goal in enumerate(st.session_state.career_tracker['learning_goals']):
                with st.expander(f"{goal['goal']} - {goal['priority']} Priority"):
                    st.write(f"**Deadline:** {goal['deadline']}")
                    st.write(f"**Priority:** {goal['priority']}")
                    if st.button(f"Mark Complete", key=f"complete_{i}"):
                        st.session_state.career_tracker['learning_goals'][i]['completed'] = True
                        st.success("Goal completed! 🎉")
                        st.rerun()
        
        # Achievements
        st.subheader("🏅 Achievements")
        if st.button("➕ Add Achievement", type="secondary"):
            with st.form("add_achievement"):
                achievement = st.text_input("Achievement")
                date = st.date_input("Date Achieved")
                category = st.selectbox("Category", ["Skill", "Job", "Project", "Certification", "Other"])
                
                if st.form_submit_button("Add Achievement"):
                    if achievement:
                        st.session_state.career_tracker['achievements'].append({
                            'achievement': achievement,
                            'date': str(date),
                            'category': category
                        })
                        st.success("Achievement added!")
                        st.rerun()
        
        # Display achievements
        if st.session_state.career_tracker.get('achievements'):
            for achievement in st.session_state.career_tracker['achievements']:
                st.write(f"🏆 **{achievement['achievement']}** ({achievement['category']}) - {achievement['date']}")
        
        # Career Pathway Simulation
        if st.session_state.get('resume_data') and st.session_state.get('career_analysis'):
            st.subheader("🗺️ Career Pathway Simulation")
            
            if st.button("🎯 Generate Career Pathway", type="primary"):
                with st.spinner("Generating your career pathway simulation..."):
                    # Get primary industry and role from analysis
                    industry = "Technology"  # Default, could be extracted from analysis
                    role = "Software Engineer"  # Default, could be extracted from analysis
                    
                    pathway = generate_career_pathway_simulation(
                        st.session_state.resume_data,
                        role
                    )
                    
                    if 'error' not in pathway:
                        st.session_state.career_pathway = pathway
                        st.success("Career pathway generated!")
                    else:
                        st.error(f"Error: {pathway['error']}")
            
            if 'career_pathway' in st.session_state:
                pathway = st.session_state.career_pathway
                
                # Career Trajectory
                if 'career_trajectory' in pathway:
                    st.subheader("📈 Your Career Trajectory")
                    trajectory = pathway['career_trajectory']
                    
                    for year, data in trajectory.items():
                        with st.expander(f"{year.replace('_', ' ').title()}: {data.get('title', 'Role')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Salary:** {data.get('salary', 'Not specified')}")
                            with col2:
                                st.write(f"**Skills:** {', '.join(data.get('skills', []))}")
                
                # Similar Profiles
                if 'similar_profiles' in pathway:
                    st.subheader("👥 Similar Career Paths")
                    for profile in pathway['similar_profiles']:
                        with st.expander(f"Profile: {profile.get('name', 'Anonymous')}"):
                            st.write(f"**Background:** {profile.get('background', 'No background')}")
                            st.write(f"**Current Role:** {profile.get('current_role', 'No current role')}")
                            st.write(f"**Journey:** {profile.get('journey', 'No journey info')}")
                            st.write(f"**Key Insights:** {profile.get('key_insights', 'No insights')}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
