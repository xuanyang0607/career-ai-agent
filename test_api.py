#!/usr/bin/env python3
"""
Test script for Career AI Agent API
Demonstrates how to use all the API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   spaCy loaded: {data['spacy_loaded']}")
            print(f"   Google AI configured: {data['google_ai_configured']}")
            print(f"   JobSpy available: {data['jobspy_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False

def test_parse_resume():
    """Test the resume parsing endpoint."""
    print("\n📄 Testing resume parsing...")
    
    sample_resume = """
    John Doe
    Software Engineer
    
    EXPERIENCE
    Senior Software Engineer
    Tech Solutions Inc. | 2020 - 2023
    - Led development of microservices architecture using Python and Docker
    - Managed team of 5 developers and implemented Agile methodologies
    - Improved system performance by 40% through optimization
    
    Junior Developer
    StartupXYZ | 2018 - 2020
    - Developed web applications using React and Node.js
    - Collaborated with cross-functional teams using Git and Jira
    - Implemented REST APIs and database solutions
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2018
    
    SKILLS
    Programming: Python, JavaScript, React, Node.js, SQL
    Tools: Docker, Kubernetes, AWS, Git, Jenkins
    Methodologies: Agile, Scrum, DevOps, CI/CD
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/parse_resume",
            json={"resume_text": sample_resume},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resume parsing successful!")
            print(f"   Skills found: {len(data['data']['skills'])}")
            print(f"   Experience entries: {len(data['data']['experience'])}")
            print(f"   Education entries: {len(data['data']['education'])}")
            print(f"   Industries: {data['data']['industries']}")
            return data['data']
        else:
            print(f"❌ Resume parsing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing resume parsing: {e}")
        return None

def test_career_intelligence(user_profile):
    """Test the career intelligence endpoint."""
    print("\n🧠 Testing career intelligence...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/get_career_intelligence",
            json={"user_profile": user_profile},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Career intelligence generated!")
            print(f"   Market summary: {data['data']['market_intelligence_summary'][:100]}...")
            print(f"   Key skills: {data['data']['key_industry_skills']}")
            return data['data']
        else:
            print(f"❌ Career intelligence failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing career intelligence: {e}")
        return None

def test_upskilling_plan(user_profile, in_demand_skills):
    """Test the upskilling plan endpoint."""
    print("\n📚 Testing upskilling plan...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/get_upskilling_plan",
            json={
                "user_profile": user_profile,
                "in_demand_skills": in_demand_skills
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upskilling plan generated!")
            print(f"   Skill gaps identified: {len(data['data']['skill_gaps'])}")
            print(f"   Timeline: {data['data']['timeline']}")
            return data['data']
        else:
            print(f"❌ Upskilling plan failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing upskilling plan: {e}")
        return None

def main():
    """Run all API tests."""
    print("🚀 Career AI Agent API Test Suite")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ API is not available. Please start the server with: python app.py")
        return
    
    # Test resume parsing
    user_profile = test_parse_resume()
    if not user_profile:
        print("\n❌ Resume parsing failed. Stopping tests.")
        return
    
    # Test career intelligence
    intelligence_data = test_career_intelligence(user_profile)
    if not intelligence_data:
        print("\n⚠️  Career intelligence failed. This might be due to missing Google API key.")
        # Use fallback data for upskilling test
        in_demand_skills = ["Machine Learning", "DevOps", "Cloud Computing"]
    else:
        in_demand_skills = intelligence_data.get('key_industry_skills', [])
    
    # Test upskilling plan
    upskilling_data = test_upskilling_plan(user_profile, in_demand_skills)
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    
    if user_profile and intelligence_data and upskilling_data:
        print("✅ All endpoints working correctly!")
    elif user_profile:
        print("⚠️  Basic functionality working. Check OpenAI API key for full features.")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
