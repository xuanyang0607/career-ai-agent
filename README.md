# Career AI Agent

A powerful Flask-based API for career analysis and guidance using AI technologies. This application provides comprehensive resume parsing, career intelligence, and personalized upskilling recommendations.

## Features

- **Resume Parsing**: Extract skills, experience, education, and industry information using spaCy NLP
- **Career Intelligence**: Get market insights, industry trends, and salary information using Google Gemini
- **Upskilling Plans**: Receive personalized learning recommendations and project ideas
- **RESTful API**: Clean, well-documented endpoints for easy frontend integration
- **Error Handling**: Comprehensive error handling and validation

## Features

### 🌐 Web Interface
- **Beautiful, responsive UI** - Modern design with tabs and interactive forms
- **Resume Analysis** - Paste your resume and get instant analysis
- **Job Search** - Search for jobs by title, location, and industry using JobSpy
- **Real-time Results** - See results in organized tabs with detailed information
- **Multi-Platform Job Scraping** - LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter

### 🔌 API Endpoints

#### 1. Health Check
- **GET** `/health` - Check API status and configuration

#### 2. Resume Parsing
- **POST** `/parse_resume` - Parse resume text and extract structured information

#### 3. Career Intelligence
- **POST** `/get_career_intelligence` - Generate market intelligence and industry insights

#### 4. Upskilling Plans
- **POST** `/get_upskilling_plan` - Get personalized learning recommendations

#### 5. Job Search
- **POST** `/search_jobs` - Search for jobs based on criteria
- **POST** `/get_job_recommendations` - Get personalized job recommendations

## Setup Instructions

### 1. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Set up spaCy English Model

```bash
# Download the English language model for spaCy
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Copy `env.example` to `.env` and add your configuration:

```bash
# .env file
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-pro
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
```

### 4. Run the Web Interface

```bash
# Option 1: Run with checks (recommended)
python run_web.py

# Option 2: Run directly
python app.py
```

The web interface will be available at `http://localhost:5000`

## Usage

### 🌐 Web Interface Usage

1. **Start the web interface:**
   ```bash
   python run_web.py
   ```

2. **Open your browser** and go to `http://localhost:5000`

3. **Analyze your resume:**
   - Paste your resume text in the left form
   - Click "Analyze Resume"
   - View results in organized tabs

4. **Search for jobs:**
   - Use the right form to search by title, location, or industry
   - Click "Search Jobs"
   - Browse job listings with apply links

5. **Explore results:**
   - **Resume Analysis**: Skills, experience, education, industries
   - **Career Intelligence**: Market insights, key skills, salary info
   - **Upskilling Plan**: Skill gaps, project ideas, learning resources
   - **Job Listings**: Matching job opportunities

### 🔌 API Usage Examples

#### Parse Resume

```bash
curl -X POST http://localhost:5000/parse_resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "John Doe\nSoftware Engineer\nExperience:\n- Senior Developer at Tech Corp (2020-2023)\n- Python, JavaScript, React\n- Led team of 5 developers"
  }'
```

### Get Career Intelligence

```bash
curl -X POST http://localhost:5000/get_career_intelligence \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "skills": ["Python", "JavaScript", "React"],
      "experience": [{"title": "Software Engineer", "company": "Tech Corp"}],
      "industries": ["Technology"],
      "desired_roles": ["Senior Developer"]
    }
  }'
```

### Get Upskilling Plan

```bash
curl -X POST http://localhost:5000/get_upskilling_plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "skills": ["Python", "JavaScript"],
      "experience": [{"title": "Developer"}],
      "industries": ["Technology"]
    },
    "in_demand_skills": ["Machine Learning", "DevOps", "Cloud Computing"]
  }'
```

#### Search Jobs

```bash
curl -X POST http://localhost:5000/search_jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "location": "San Francisco",
    "industry": "Technology"
  }'
```

#### Get Job Recommendations

```bash
curl -X POST http://localhost:5000/get_job_recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "skills": ["Python", "Machine Learning"],
      "experience": [{"title": "Data Scientist"}],
      "industries": ["Technology"]
    }
  }'
```

## Project Structure

```
career_ai_agent/
├── app.py              # Main Flask application with API endpoints
├── config.py           # Configuration and API key management
├── main.py             # Legacy CLI application (for reference)
├── run_web.py          # Web interface launcher with checks
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── env.example        # Example environment variables
├── .env              # Environment variables (create this)
└── templates/
    └── index.html     # Web interface HTML template
```

## Response Formats

### Resume Parsing Response

```json
{
  "success": true,
  "data": {
    "skills": ["Python", "JavaScript", "React"],
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "years_start": "2020",
        "years_end": "2023",
        "description_summary": "Led team of 5 developers..."
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science",
        "institution": "University Name",
        "graduation_year": "2019"
      }
    ],
    "industries": ["Technology"],
    "desired_roles": ["Python Specialist", "JavaScript Specialist"],
    "parsed_at": "2024-01-15T10:30:00"
  }
}
```

### Career Intelligence Response

```json
{
  "success": true,
  "data": {
    "market_intelligence_summary": "Recent trends in software development...",
    "key_industry_skills": ["Machine Learning", "DevOps", "Cloud Computing"],
    "macroeconomic_shifts": "AI regulations and market changes...",
    "salary_insights": "Current salary ranges for software engineers...",
    "growth_opportunities": "Emerging roles in AI and cloud computing..."
  }
}
```

### Upskilling Plan Response

```json
{
  "success": true,
  "data": {
    "skill_gaps": [
      {
        "skill": "Machine Learning",
        "project_idea": "Build a recommendation system using Python and scikit-learn",
        "learning_resources": [
          {
            "name": "Machine Learning Course on Coursera",
            "url": "https://coursera.org/ml-course",
            "type": "course"
          }
        ]
      }
    ],
    "timeline": "3-6 months",
    "priority_order": "Start with Machine Learning, then DevOps"
  }
}
```

## Dependencies

- `flask>=2.3.0` - Web framework for API
- `flask-cors>=4.0.0` - Cross-origin resource sharing
- `spacy>=3.7.0` - Natural language processing
- `requests>=2.31.0` - HTTP library
- `google-generativeai>=0.3.0` - Google Gemini API client
- `python-jobspy>=1.1.79` - Job scraping from multiple platforms
- `python-dotenv>=1.0.0` - Environment variable management

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data or missing required fields
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server-side errors

All error responses include descriptive messages to help with debugging.

## Development

### Running in Development Mode

```bash
export DEBUG=True
python app.py
```

### Testing the API

You can test the API using curl, Postman, or any HTTP client. The health check endpoint is a good starting point:

```bash
curl http://localhost:5000/health
```

## Security Notes

- Store API keys securely in environment variables
- Change the default SECRET_KEY in production
- Consider implementing rate limiting for production use
- Add authentication if needed for production deployment

## JobSpy Integration

The Career AI Agent now uses [JobSpy](https://github.com/speedyapply/JobSpy) for real job scraping from multiple platforms:

### **Supported Job Boards:**
- **LinkedIn** - Professional networking and job postings
- **Indeed** - Comprehensive job search platform
- **Glassdoor** - Jobs with company reviews and salary data
- **Google Jobs** - Google's job search integration
- **ZipRecruiter** - Job matching platform

### **Features:**
- **Real-time job scraping** from multiple sources
- **Automatic salary parsing** and formatting
- **Location-based filtering** with distance options
- **Job type filtering** (full-time, part-time, contract, internship)
- **Remote work detection**
- **Fallback to simulated data** if JobSpy is unavailable

### **Installation:**
```bash
pip install python-jobspy
```

### **Usage:**
The job search automatically uses JobSpy when available. If JobSpy is not installed, the system falls back to simulated job data.

## Next Steps

This API is designed to power a user-friendly frontend interface. The structured JSON responses make it easy to integrate with:

- React/Vue.js frontends
- Mobile applications
- Chatbots
- Other AI applications

The modular design allows for easy extension with additional features like job board integration, interview preparation, or advanced analytics.
