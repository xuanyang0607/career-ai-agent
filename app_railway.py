"""
Career AI Agent - Flask API Application
A comprehensive career analysis and guidance API using AI technologies.
"""

import json
import re
import spacy
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
from datetime import datetime
from auth import init_auth, require_auth
try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    print("⚠️  JobSpy not available. Install with: pip install python-jobspy")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize authentication
init_auth(app)

# Initialize Google AI client
genai.configure(api_key=Config.GOOGLE_API_KEY)
google_model = genai.GenerativeModel(Config.GOOGLE_MODEL)

# Initialize spaCy model
try:
    nlp = spacy.load(Config.SPACY_MODEL)
    print(f"✅ spaCy model '{Config.SPACY_MODEL}' loaded successfully")
except OSError:
    print(f"❌ spaCy model '{Config.SPACY_MODEL}' not found. Please run: python -m spacy download {Config.SPACY_MODEL}")
    nlp = None

def extract_skills_from_text(text):
    """Extract skills from text using spaCy and pattern matching."""
    if not nlp:
        return []
    
    doc = nlp(text)
    skills = []
    
    # Extract technical skills using pattern matching
    skill_patterns = [
        r'\b(?:Python|JavaScript|Java|C\+\+|C#|Ruby|PHP|Go|Rust|Swift|Kotlin|TypeScript|React|Angular|Vue|Node\.js|Django|Flask|Spring|Laravel|Express|MongoDB|PostgreSQL|MySQL|Redis|Docker|Kubernetes|AWS|Azure|GCP|Git|Jenkins|Jira|Agile|Scrum|Machine Learning|AI|Data Science|SQL|NoSQL|REST|API|GraphQL|Microservices|DevOps|CI/CD|Linux|Unix|Windows|MacOS)\b',
        r'\b(?:Project Management|Leadership|Communication|Problem Solving|Critical Thinking|Team Management|Strategic Planning|Budget Management|Risk Management|Change Management|Stakeholder Management|Product Management|Business Analysis|Data Analysis|Marketing|Sales|Customer Service|Design|UX|UI|Content Creation|SEO|SEM|Social Media|Email Marketing|Brand Management|Event Planning|Public Relations|Human Resources|Finance|Accounting|Legal|Healthcare|Education|Research|Consulting|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\b'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    # Extract skills from spaCy entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
            # Filter out common non-skill entities
            if ent.text.lower() not in ['united states', 'new york', 'california', 'company', 'inc', 'corp', 'llc']:
                skills.append(ent.text)
    
    # Remove duplicates and clean up
    skills = list(set([skill.strip() for skill in skills if len(skill.strip()) > 2]))
    return skills[:20]  # Limit to top 20 skills

def extract_experience(text):
    """Extract work experience from resume text."""
    if not nlp:
        return []
    
    doc = nlp(text)
    experience = []
    
    # Look for experience patterns
    experience_patterns = [
        r'(?:(\d{4})\s*[-–—]\s*(\d{4}|\bpresent\b|\bcurrent\b))',
        r'(?:(\d{4})\s*to\s*(\d{4}|\bpresent\b|\bcurrent\b))',
        r'(?:(\d{4})\s*-\s*(\d{4}|\bpresent\b|\bcurrent\b))'
    ]
    
    lines = text.split('\n')
    current_experience = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for job titles
        title_patterns = [
            r'\b(?:Senior|Junior|Lead|Principal|Staff|Chief|VP|Director|Manager|Coordinator|Specialist|Analyst|Developer|Engineer|Designer|Architect|Consultant|Advisor|Strategist|Planner|Officer|Executive|Administrator|Assistant|Associate|Representative|Technician|Technologist|Scientist|Researcher|Instructor|Professor|Teacher|Trainer|Coach|Mentor|Facilitator|Moderator|Curator|Editor|Writer|Author|Journalist|Reporter|Producer|Director|Actor|Artist|Musician|Photographer|Videographer|Chef|Bartender|Server|Host|Receptionist|Secretary|Clerk|Cashier|Sales|Marketing|Business|Finance|Accounting|Legal|Medical|Nursing|Healthcare|Education|Research|Consulting|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\s+(?:Software|Web|Frontend|Backend|Full Stack|Mobile|iOS|Android|Data|Machine Learning|AI|DevOps|Cloud|Security|Network|Systems|Database|QA|Test|Product|Project|Program|Business|Marketing|Sales|Customer|Human Resources|Finance|Accounting|Legal|Medical|Nursing|Healthcare|Education|Research|Consulting|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\b',
            r'\b(?:Software|Web|Frontend|Backend|Full Stack|Mobile|iOS|Android|Data|Machine Learning|AI|DevOps|Cloud|Security|Network|Systems|Database|QA|Test|Product|Project|Program|Business|Marketing|Sales|Customer|Human Resources|Finance|Accounting|Legal|Medical|Nursing|Healthcare|Education|Research|Consulting|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\s+(?:Engineer|Developer|Architect|Analyst|Manager|Director|Coordinator|Specialist|Consultant|Advisor|Strategist|Planner|Officer|Executive|Administrator|Assistant|Associate|Representative|Technician|Technologist|Scientist|Researcher|Instructor|Professor|Teacher|Trainer|Coach|Mentor|Facilitator|Moderator|Curator|Editor|Writer|Author|Journalist|Reporter|Producer|Director|Actor|Artist|Musician|Photographer|Videographer|Chef|Bartender|Server|Host|Receptionist|Secretary|Clerk|Cashier|Sales|Marketing|Business|Finance|Accounting|Legal|Medical|Nursing|Healthcare|Education|Research|Consulting|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\b'
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, line, re.IGNORECASE)
            if title_match:
                current_experience['title'] = title_match.group(0)
                break
        
        # Look for company names
        for ent in doc.ents:
            if ent.label_ == 'ORG' and ent.text in line:
                current_experience['company'] = ent.text
                break
        
        # Look for dates
        for pattern in experience_patterns:
            date_match = re.search(pattern, line, re.IGNORECASE)
            if date_match:
                current_experience['years_start'] = date_match.group(1)
                current_experience['years_end'] = date_match.group(2)
                break
        
        # If we have enough info, add to experience list
        if len(current_experience) >= 2:
            current_experience['description_summary'] = line[:200] + "..." if len(line) > 200 else line
            experience.append(current_experience.copy())
            current_experience = {}
    
    return experience

def extract_education(text):
    """Extract education information from resume text."""
    education = []
    
    # Education patterns
    education_patterns = [
        r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)\s+(?:of|in)\s+(?:Science|Arts|Engineering|Business|Technology|Computer|Information|Data|Marketing|Finance|Accounting|Law|Medicine|Education|Psychology|Sociology|Economics|Mathematics|Physics|Chemistry|Biology|History|Literature|Philosophy|Political|International|Environmental|Health|Public|Social|Human|Organizational|Industrial|Mechanical|Electrical|Civil|Chemical|Biomedical|Software|Computer|Information|Data|Cybersecurity|Network|Systems|Database|Web|Mobile|Game|Robotics|AI|Machine Learning|Data Science|Business|Management|Leadership|Project|Program|Product|Marketing|Sales|Finance|Accounting|Human Resources|Operations|Supply Chain|Logistics|Manufacturing|Retail|E-commerce|Real Estate|Insurance|Banking|Investment|Trading|Cryptocurrency|Blockchain|Cybersecurity|Network Security|Information Security|Compliance|Audit|Quality Assurance|Testing|QA|SDLC|Waterfall|Kanban|Lean|Six Sigma|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\b',
        r'\b(?:BS|BA|MS|MA|PhD|MBA|MFA|JD|MD|DO|DDS|DVM|RN|LPN|CPA|CFA|PMP|PRINCE2|ITIL|COBIT|ISO|GDPR|HIPAA|SOX|PCI)\b'
    ]
    
    lines = text.split('\n')
    current_education = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for degree
        for pattern in education_patterns:
            degree_match = re.search(pattern, line, re.IGNORECASE)
            if degree_match:
                current_education['degree'] = degree_match.group(0)
                break
        
        # Look for graduation year
        year_match = re.search(r'\b(19|20)\d{2}\b', line)
        if year_match:
            current_education['graduation_year'] = year_match.group(0)
        
        # Look for institution names (simplified)
        if 'university' in line.lower() or 'college' in line.lower() or 'institute' in line.lower():
            current_education['institution'] = line
        
        # If we have enough info, add to education list
        if len(current_education) >= 2:
            education.append(current_education.copy())
            current_education = {}
    
    return education

def parse_resume_text(text):
    """
    Parse resume text and extract structured information.
    
    Args:
        text (str): Raw resume text
        
    Returns:
        dict: Structured resume information
    """
    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty")
    
    # Clean the text
    text = text.strip()
    
    # Extract information
    skills = extract_skills_from_text(text)
    experience = extract_experience(text)
    education = extract_education(text)
    
    # Infer industries from experience and skills
    industries = []
    industry_keywords = {
        'Technology': ['software', 'tech', 'programming', 'coding', 'development', 'engineering'],
        'Finance': ['finance', 'banking', 'investment', 'accounting', 'trading', 'financial'],
        'Healthcare': ['healthcare', 'medical', 'nursing', 'hospital', 'pharmaceutical', 'biotech'],
        'Education': ['education', 'teaching', 'academic', 'university', 'school', 'learning'],
        'Marketing': ['marketing', 'advertising', 'brand', 'digital marketing', 'social media'],
        'Consulting': ['consulting', 'advisory', 'strategy', 'management consulting'],
        'Retail': ['retail', 'e-commerce', 'sales', 'customer service', 'merchandising'],
        'Manufacturing': ['manufacturing', 'production', 'operations', 'supply chain', 'logistics']
    }
    
    text_lower = text.lower()
    for industry, keywords in industry_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            industries.append(industry)
    
    # Remove duplicates
    industries = list(set(industries))
    
    # Infer desired roles from skills and experience
    desired_roles = []
    if skills:
        # Use the most prominent skills to suggest roles
        top_skills = skills[:5]
        desired_roles = [f"{skill} Specialist" for skill in top_skills[:3]]
    
    return {
        'skills': skills,
        'experience': experience,
        'education': education,
        'industries': industries,
        'desired_roles': desired_roles,
        'parsed_at': datetime.now().isoformat()
    }

def generate_intelligence_report(user_profile):
    """
    Generate career intelligence report using OpenAI API.
    
    Args:
        user_profile (dict): Parsed resume information
        
    Returns:
        dict: Career intelligence report
    """
    try:
        # Construct the prompt for the LLM
        prompt = f"""
        You are a Senior Career Intelligence Analyst with expertise in market trends, industry analysis, and career development. 
        
        Analyze the following user profile and provide comprehensive career intelligence:
        
        User Profile:
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {len(user_profile.get('experience', []))} positions
        - Industries: {', '.join(user_profile.get('industries', []))}
        - Desired Roles: {', '.join(user_profile.get('desired_roles', []))}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "market_intelligence_summary": "Recent trends, funding news, and notable startups in the user's primary industry",
            "key_industry_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
            "macroeconomic_shifts": "Significant regulations, laws, or market forces impacting this industry/role",
            "salary_insights": "Current salary ranges and compensation trends",
            "growth_opportunities": "Emerging roles and career advancement paths"
        }}
        
        Focus on actionable insights and current market conditions. Be specific and data-driven in your recommendations.
        """
        
        response = google_model.generate_content(prompt)
        
        # Parse the response
        content = response.text
        try:
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: return structured response
                return {
                    "market_intelligence_summary": content,
                    "key_industry_skills": user_profile.get('skills', [])[:5],
                    "macroeconomic_shifts": "Analysis provided in summary",
                    "salary_insights": "Contact for detailed salary information",
                    "growth_opportunities": "See market intelligence summary"
                }
        except json.JSONDecodeError:
            # Fallback: return structured response
            return {
                "market_intelligence_summary": content,
                "key_industry_skills": user_profile.get('skills', [])[:5],
                "macroeconomic_shifts": "Analysis provided in summary",
                "salary_insights": "Contact for detailed salary information",
                "growth_opportunities": "See market intelligence summary"
            }
            
    except Exception as e:
        return {
            "error": f"Failed to generate intelligence report: {str(e)}",
            "market_intelligence_summary": "Unable to generate market intelligence at this time",
            "key_industry_skills": user_profile.get('skills', [])[:5],
            "macroeconomic_shifts": "Analysis temporarily unavailable",
            "salary_insights": "Contact for detailed salary information",
            "growth_opportunities": "See market intelligence summary"
        }

def generate_upskilling_plan(user_profile, in_demand_skills):
    """
    Generate personalized upskilling plan using OpenAI API.
    
    Args:
        user_profile (dict): Parsed resume information
        in_demand_skills (list): Skills in demand from career intelligence
        
    Returns:
        dict: Upskilling plan
    """
    try:
        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        demand_skills = set(skill.lower() for skill in in_demand_skills)
        
        # Identify skill gaps
        skill_gaps = list(demand_skills - user_skills)[:3]  # Top 3 gaps
        
        prompt = f"""
        You are an expert career development coach and learning strategist.
        
        User's current skills: {', '.join(user_profile.get('skills', []))}
        In-demand skills in their industry: {', '.join(in_demand_skills)}
        Identified skill gaps: {', '.join(skill_gaps)}
        
        For each skill gap, provide:
        1. A personalized AI-generated project idea that builds a portfolio
        2. 1-2 specific online resources/tutorials (Coursera, documentation, blogs)
        
        Return in this JSON format:
        {{
            "skill_gaps": [
                {{
                    "skill": "skill_name",
                    "project_idea": "Detailed project description",
                    "learning_resources": [
                        {{
                            "name": "Resource name",
                            "url": "Resource URL",
                            "type": "course|documentation|blog|video"
                        }}
                    ]
                }}
            ],
            "timeline": "Estimated timeline for completing the upskilling plan",
            "priority_order": "Recommended order to tackle these skills"
        }}
        """
        
        response = google_model.generate_content(prompt)
        
        content = response.text
        
        try:
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: return structured response
                return {
                    "skill_gaps": [
                        {
                            "skill": skill,
                            "project_idea": f"Build a portfolio project demonstrating {skill}",
                            "learning_resources": [
                                {
                                    "name": f"{skill} Tutorial",
                                    "url": f"https://example.com/{skill.lower().replace(' ', '-')}",
                                    "type": "course"
                                }
                            ]
                        } for skill in skill_gaps
                    ],
                    "timeline": "3-6 months",
                    "priority_order": "Start with the most in-demand skills first"
                }
        except json.JSONDecodeError:
            # Fallback: return structured response
            return {
                "skill_gaps": [
                    {
                        "skill": skill,
                        "project_idea": f"Build a portfolio project demonstrating {skill}",
                        "learning_resources": [
                            {
                                "name": f"{skill} Tutorial",
                                "url": f"https://example.com/{skill.lower().replace(' ', '-')}",
                                "type": "course"
                            }
                        ]
                    } for skill in skill_gaps
                ],
                "timeline": "3-6 months",
                "priority_order": "Start with the most in-demand skills first"
            }
            
    except Exception as e:
        return {
            "error": f"Failed to generate upskilling plan: {str(e)}",
            "skill_gaps": [],
            "timeline": "Unable to generate timeline",
            "priority_order": "Contact for personalized guidance"
        }

def search_jobs_api(title=None, location=None, industry=None, limit=10):
    """
    Search for jobs using JobSpy library.
    Supports LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter & more.
    """
    if not JOBSPY_AVAILABLE:
        # Fallback to simulated data if JobSpy is not available
        return search_jobs_fallback(title, location, industry, limit)
    
    try:
        # Prepare search parameters
        search_term = title or "software engineer"  # Default search term
        site_names = ["indeed", "linkedin", "zip_recruiter"]  # Main job boards
        
        # Build search parameters
        search_params = {
            "site_name": site_names,
            "search_term": search_term,
            "results_wanted": min(limit, 50),  # JobSpy limit
            "hours_old": 168,  # Jobs from last week
            "country_indeed": "USA"
        }
        
        # Add location if provided
        if location:
            search_params["location"] = location
        
        # Add job type filters based on industry
        if industry:
            if industry.lower() in ["technology", "software", "it"]:
                search_params["search_term"] = f"{search_term} (software OR technology OR IT)"
            elif industry.lower() in ["finance", "banking"]:
                search_params["search_term"] = f"{search_term} (finance OR banking)"
            elif industry.lower() in ["healthcare", "medical"]:
                search_params["search_term"] = f"{search_term} (healthcare OR medical)"
        
        print(f"🔍 Searching jobs with JobSpy: {search_params}")
        
        # Scrape jobs using JobSpy
        jobs_df = scrape_jobs(**search_params)
        
        if jobs_df.empty:
            print("⚠️  No jobs found with JobSpy")
            return search_jobs_fallback(title, location, industry, limit)
        
        # Convert DataFrame to list of dictionaries
        jobs_list = []
        for _, row in jobs_df.head(limit).iterrows():
            job = {
                "title": row.get("TITLE", "N/A"),
                "company": row.get("COMPANY", "N/A"),
                "location": f"{row.get('CITY', '')}, {row.get('STATE', '')}".strip(", "),
                "description": row.get("DESCRIPTION", "No description available")[:500] + "...",
                "salary": format_salary(row),
                "url": row.get("JOB_URL", "#"),
                "posted_date": str(row.get("DATE_POSTED", "N/A")),
                "job_type": row.get("JOB_TYPE", "N/A"),
                "is_remote": row.get("IS_REMOTE", False)
            }
            jobs_list.append(job)
        
        print(f"✅ Found {len(jobs_list)} jobs with JobSpy")
        return jobs_list
        
    except Exception as e:
        print(f"❌ Error with JobSpy: {e}")
        return search_jobs_fallback(title, location, industry, limit)

def search_jobs_fallback(title=None, location=None, industry=None, limit=10):
    """Fallback job search with simulated data."""
    sample_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "description": "We're looking for a Senior Software Engineer to join our team...",
            "salary": "$120,000 - $180,000",
            "url": "https://example.com/job1",
            "posted_date": "2024-01-15",
            "job_type": "fulltime",
            "is_remote": False
        },
        {
            "title": "Data Scientist",
            "company": "AI Startup",
            "location": "Remote",
            "description": "Join our AI team to build cutting-edge machine learning models...",
            "salary": "$100,000 - $150,000",
            "url": "https://example.com/job2",
            "posted_date": "2024-01-14",
            "job_type": "fulltime",
            "is_remote": True
        },
        {
            "title": "Frontend Developer",
            "company": "Web Solutions Inc",
            "location": "New York, NY",
            "description": "Build beautiful user interfaces with React and modern web technologies...",
            "salary": "$90,000 - $130,000",
            "url": "https://example.com/job3",
            "posted_date": "2024-01-13",
            "job_type": "fulltime",
            "is_remote": False
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Tech",
            "location": "Austin, TX",
            "description": "Manage our cloud infrastructure and CI/CD pipelines...",
            "salary": "$110,000 - $160,000",
            "url": "https://example.com/job4",
            "posted_date": "2024-01-12",
            "job_type": "fulltime",
            "is_remote": False
        },
        {
            "title": "Product Manager",
            "company": "Innovation Labs",
            "location": "Seattle, WA",
            "description": "Lead product strategy and development for our SaaS platform...",
            "salary": "$130,000 - $200,000",
            "url": "https://example.com/job5",
            "posted_date": "2024-01-11",
            "job_type": "fulltime",
            "is_remote": False
        }
    ]
    
    # Filter jobs based on search criteria
    filtered_jobs = sample_jobs
    
    if title:
        filtered_jobs = [job for job in filtered_jobs if title.lower() in job['title'].lower()]
    
    if location:
        filtered_jobs = [job for job in filtered_jobs if location.lower() in job['location'].lower()]
    
    if industry:
        # In a real implementation, you would filter by industry tags
        pass
    
    return filtered_jobs[:limit]

def format_salary(row):
    """Format salary information from JobSpy data."""
    min_amount = row.get("MIN_AMOUNT")
    max_amount = row.get("MAX_AMOUNT")
    interval = row.get("INTERVAL", "yearly")
    
    if min_amount and max_amount:
        if interval == "yearly":
            return f"${min_amount:,} - ${max_amount:,}"
        elif interval == "hourly":
            return f"${min_amount}/hr - ${max_amount}/hr"
        else:
            return f"${min_amount:,} - ${max_amount:,} ({interval})"
    elif min_amount:
        if interval == "yearly":
            return f"${min_amount:,}+"
        elif interval == "hourly":
            return f"${min_amount}/hr+"
        else:
            return f"${min_amount:,}+ ({interval})"
    else:
        return "Salary not specified"

def get_job_recommendations(user_profile, limit=5):
    """
    Get personalized job recommendations based on user profile.
    """
    try:
        # Use OpenAI to generate job recommendations
        prompt = f"""
        Based on this user profile, suggest 5 job titles that would be a good fit:
        
        User Profile:
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {len(user_profile.get('experience', []))} positions
        - Industries: {', '.join(user_profile.get('industries', []))}
        - Desired Roles: {', '.join(user_profile.get('desired_roles', []))}
        
        Return only the job titles as a JSON array, like: ["Job Title 1", "Job Title 2", ...]
        """
        
        response = google_model.generate_content(prompt)
        
        content = response.text
        try:
            # Try to extract JSON from the response
            import json
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                recommended_titles = json.loads(json_str)
                return recommended_titles
        except:
            pass
        
        # Fallback to default recommendations
        return ["Software Engineer", "Data Analyst", "Product Manager", "DevOps Engineer", "UX Designer"]
        
    except Exception as e:
        # Fallback to default recommendations
        return ["Software Engineer", "Data Analyst", "Product Manager", "DevOps Engineer", "UX Designer"]

# Web Interface
@app.route('/')
@require_auth
def index():
    """Serve the main web interface."""
    return render_template('index.html')

# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'spacy_loaded': nlp is not None,
        'google_ai_configured': bool(Config.GOOGLE_API_KEY),
        'jobspy_available': JOBSPY_AVAILABLE
    })

@app.route('/parse_resume', methods=['POST'])
@require_auth
def parse_resume():
    """
    Parse resume text and extract structured information.
    
    Expected JSON payload:
    {
        "resume_text": "Raw resume text content"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({
                'error': 'Missing resume_text in request body'
            }), 400
        
        resume_text = data['resume_text']
        
        if not resume_text or not resume_text.strip():
            return jsonify({
                'error': 'Resume text cannot be empty'
            }), 400
        
        # Parse the resume
        parsed_data = parse_resume_text(resume_text)
        
        return jsonify({
            'success': True,
            'data': parsed_data
        })
        
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/get_career_intelligence', methods=['POST'])
@require_auth
def get_career_intelligence():
    """
    Generate career intelligence report based on user profile.
    
    Expected JSON payload:
    {
        "user_profile": {
            "skills": [...],
            "experience": [...],
            "education": [...],
            "industries": [...],
            "desired_roles": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_profile' not in data:
            return jsonify({
                'error': 'Missing user_profile in request body'
            }), 400
        
        user_profile = data['user_profile']
        
        # Generate intelligence report
        intelligence_report = generate_intelligence_report(user_profile)
        
        return jsonify({
            'success': True,
            'data': intelligence_report
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/get_upskilling_plan', methods=['POST'])
@require_auth
def get_upskilling_plan():
    """
    Generate personalized upskilling plan.
    
    Expected JSON payload:
    {
        "user_profile": {
            "skills": [...],
            "experience": [...],
            "education": [...],
            "industries": [...],
            "desired_roles": [...]
        },
        "in_demand_skills": ["skill1", "skill2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_profile' not in data:
            return jsonify({
                'error': 'Missing user_profile in request body'
            }), 400
        
        user_profile = data['user_profile']
        in_demand_skills = data.get('in_demand_skills', [])
        
        # Generate upskilling plan
        upskilling_plan = generate_upskilling_plan(user_profile, in_demand_skills)
        
        return jsonify({
            'success': True,
            'data': upskilling_plan
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/search_jobs', methods=['POST'])
@require_auth
def search_jobs():
    """
    Search for jobs based on criteria.
    
    Expected JSON payload:
    {
        "title": "Job title (optional)",
        "location": "Location (optional)",
        "industry": "Industry (optional)"
    }
    """
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip() if data else ''
        location = data.get('location', '').strip() if data else ''
        industry = data.get('industry', '').strip() if data else ''
        
        # Search for jobs
        jobs = search_jobs_api(title=title, location=location, industry=industry)
        
        return jsonify({
            'success': True,
            'data': jobs
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/get_job_recommendations', methods=['POST'])
@require_auth
def get_job_recommendations_endpoint():
    """
    Get personalized job recommendations based on user profile.
    
    Expected JSON payload:
    {
        "user_profile": {
            "skills": [...],
            "experience": [...],
            "education": [...],
            "industries": [...],
            "desired_roles": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_profile' not in data:
            return jsonify({
                'error': 'Missing user_profile in request body'
            }), 400
        
        user_profile = data['user_profile']
        
        # Get job recommendations
        recommended_titles = get_job_recommendations(user_profile)
        
        # Search for jobs with recommended titles
        recommended_jobs = []
        for title in recommended_titles[:3]:  # Top 3 recommendations
            jobs = search_jobs_api(title=title, limit=2)
            recommended_jobs.extend(jobs)
        
        return jsonify({
            'success': True,
            'data': {
                'recommended_titles': recommended_titles,
                'recommended_jobs': recommended_jobs
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
    
    print("🚀 Starting Career AI Agent API...")
    print(f"📊 spaCy model: {Config.SPACY_MODEL}")
    print(f"🤖 Google AI model: {Config.GOOGLE_MODEL}")
    print(f"💼 JobSpy integration: {'✅ Available' if JOBSPY_AVAILABLE else '❌ Not available'}")
    print(f"🌐 API will be available at: http://localhost:5000")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
