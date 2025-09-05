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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'google_ai_configured' not in st.session_state:
    st.session_state.google_ai_configured = False

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
    
    # Extract years of experience (simple pattern)
    import re
    years_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience', text_lower)
    years_experience = int(years_match.group(1)) if years_match else 0
    
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
        return json.loads(response.text)
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
        return json.loads(response.text)
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
        return json.loads(response.text)
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Resume Analysis", 
        "🎯 Career Insights", 
        "💼 Job Recommendations", 
        "📈 Market Intelligence",
        "🛠️ Resume Improvement",
        "📚 Training & Projects"
    ])
    
    # Tab 1: Enhanced Resume Analysis
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        # Header with description
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("📄 Resume Analysis & Preferences")
            st.write("Upload your resume and set your career preferences to get started with personalized insights.")
        with col2:
            if st.session_state.get('resume_data'):
                display_success_message("Resume Analyzed!")
            else:
                display_info_message("Ready to analyze")
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Upload Your Resume")
            st.markdown("**Paste your complete resume text below:**")
            resume_text = st.text_area(
                "Resume Content", 
                height=400,
                placeholder="Paste your complete resume text including:\n• Work experience with dates and descriptions\n• Education and degrees\n• Skills and certifications\n• Achievements and projects\n• Contact information",
                help="The more detailed your resume, the better our analysis will be!"
            )
            
            # File upload option
            uploaded_file = st.file_uploader(
                "Or upload a file", 
                type=['txt', 'pdf', 'docx'],
                help="Upload your resume file for easier processing"
            )
            
            if uploaded_file:
                st.info(f"📁 File uploaded: {uploaded_file.name}")
        
        with col2:
            st.subheader("🎯 Your Career Preferences")
            
            # Manual preferences form with better styling
            st.markdown("**📍 Location & Compensation**")
            location = st.text_input(
                "Preferred Location", 
                value="California", 
                help="Where do you want to work?",
                placeholder="e.g., San Francisco, Remote, New York"
            )
            salary_min = st.number_input(
                "Minimum Salary ($)", 
                value=200000, 
                step=10000, 
                min_value=0,
                help="Your minimum acceptable salary"
            )
            
            st.markdown("**💼 Job Details**")
            job_type = st.selectbox(
                "Job Type",
                ["Full time", "Part time", "Contract", "Intern", "Remote", "Hybrid"],
                help="What type of employment are you looking for?"
            )
            
            sponsorship = st.checkbox("Need Visa Sponsorship", value=False, help="Do you require visa sponsorship?")
            
            st.markdown("**🏢 Company Culture**")
            value_options = [
                "Work-life balance", "Transparency", "Impact", "Innovation", 
                "Diversity", "Growth", "Stability", "Social responsibility"
            ]
            value_alignment = st.multiselect(
                "What matters most to you?",
                value_options,
                default=["Work-life balance", "Transparency", "Impact"],
                help="Select the values that are most important to you"
            )
            
            company_size = st.selectbox(
                "Preferred Company Size",
                ["Startup (1-50)", "Small (10-500)", "Medium (500-5000)", "Large (5000+)", "Any"],
                help="What size company do you prefer?"
            )
        
        # Analyze button with better styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_clicked = st.button("🔍 Analyze Resume & Generate Insights", type="primary", use_container_width=True)
        
        if analyze_clicked:
            if resume_text:
                with st.spinner("🤖 AI is analyzing your resume and generating insights..."):
                    # Extract resume data
                    resume_data = extract_resume_data(resume_text)
                    
                    # Create manual preferences dict
                    manual_preferences = {
                        "location": location,
                        "salary_min": salary_min,
                        "job_type": job_type,
                        "sponsorship": sponsorship,
                        "value_alignment": value_alignment,
                        "company_size": company_size
                    }
                    
                    # Store in session state for other tabs
                    st.session_state.resume_data = resume_data
                    st.session_state.manual_preferences = manual_preferences
                
                # Display success message
                display_success_message("Resume analysis complete! Your profile has been processed.")
                
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
                
                # Next steps
                st.markdown("---")
                st.subheader("🚀 Next Steps")
                st.markdown("""
                <div class="info-card">
                    <strong>Ready for the next phase!</strong><br>
                    Your resume has been analyzed. Now you can:
                    <ul>
                        <li>🎯 Get comprehensive career insights</li>
                        <li>💼 Find personalized job recommendations</li>
                        <li>📈 Explore market intelligence</li>
                        <li>📚 Get training materials and projects</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                display_warning_message("Please paste your resume text to get started")
        
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

if __name__ == "__main__":
    main()
