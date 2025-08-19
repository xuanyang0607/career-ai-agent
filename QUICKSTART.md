# 🚀 Quick Start Guide

Get your Career AI Agent up and running in 5 minutes!

## Prerequisites

- Python 3.7+ installed
- Google AI API key (get one at https://makersuite.google.com/app/apikey)

## Step 1: Install Dependencies

```bash
# Install Python packages
pip3 install -r requirements.txt

# Download spaCy model
python3 -m spacy download en_core_web_sm
```

## Step 2: Configure API Key

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your OpenAI API key
nano .env
```

Replace `your_google_api_key_here` with your actual Google AI API key.

## Step 3: Start the Web Interface

```bash
# Run with automatic checks
python3 run_web.py
```

## Step 4: Use the Application

1. **Open your browser** and go to `http://localhost:5000`
2. **Paste your resume** in the left form and click "Analyze Resume"
3. **Search for jobs** using the right form
4. **Explore results** in the organized tabs

## What You'll Get

### 📄 Resume Analysis
- **Skills extraction** - Technical and soft skills
- **Experience parsing** - Job titles, companies, dates
- **Education detection** - Degrees, institutions, years
- **Industry classification** - Automatic industry identification

### 🧠 Career Intelligence
- **Market trends** - Recent industry developments
- **Key skills** - In-demand skills for your field
- **Salary insights** - Current compensation trends
- **Growth opportunities** - Emerging roles and paths

### 📚 Upskilling Plan
- **Skill gaps** - Areas for improvement
- **Project ideas** - Portfolio-building suggestions
- **Learning resources** - Courses, tutorials, documentation
- **Timeline** - Estimated completion schedule

### 💼 Job Search
- **Real job listings** - From LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
- **Personalized recommendations** - AI-suggested roles
- **Apply links** - Direct application URLs
- **Salary information** - Compensation details
- **Multi-platform aggregation** - Jobs from all major job boards

## Troubleshooting

### "pip not found"
```bash
pip3 install -r requirements.txt
```

### "spaCy model not found"
```bash
python3 -m spacy download en_core_web_sm
```

### "Google API key error"
- Check your `.env` file has the correct API key
- Ensure you have credits in your Google AI account

### "Port 5000 in use"
- Change the port in `app.py` or `run_web.py`
- Or stop other applications using port 5000

## Next Steps

- **Customize the job search** - Add real job board APIs
- **Enhance the UI** - Add more styling and features
- **Add authentication** - User accounts and saved profiles
- **Integrate with LinkedIn** - Import profile data
- **Add interview prep** - Mock interviews and tips

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your OpenAI API key is correct
3. Ensure all dependencies are installed
4. Check that port 5000 is available

Happy career building! 🎉
