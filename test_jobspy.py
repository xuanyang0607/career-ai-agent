#!/usr/bin/env python3
"""
Test script for JobSpy integration
Verifies that job scraping works correctly
"""

import sys
import json
from datetime import datetime

def test_jobspy_import():
    """Test if JobSpy can be imported."""
    try:
        from jobspy import scrape_jobs
        print("✅ JobSpy imported successfully")
        return True
    except ImportError as e:
        print(f"❌ JobSpy import failed: {e}")
        print("Install with: pip install python-jobspy")
        return False

def test_jobspy_search():
    """Test a simple job search with JobSpy."""
    try:
        from jobspy import scrape_jobs
        
        print("\n🔍 Testing JobSpy search...")
        
        # Simple search for software engineer jobs
        jobs_df = scrape_jobs(
            site_name=["indeed"],  # Start with just Indeed for testing
            search_term="software engineer",
            location="San Francisco, CA",
            results_wanted=5,
            hours_old=168,  # Last week
            country_indeed="USA"
        )
        
        if jobs_df.empty:
            print("⚠️  No jobs found (this might be normal)")
            return False
        
        print(f"✅ Found {len(jobs_df)} jobs")
        print("\n📋 Sample jobs:")
        
        for i, (_, row) in enumerate(jobs_df.head(3).iterrows()):
            print(f"\nJob {i+1}:")
            print(f"  Title: {row.get('TITLE', 'N/A')}")
            print(f"  Company: {row.get('COMPANY', 'N/A')}")
            print(f"  Location: {row.get('CITY', 'N/A')}, {row.get('STATE', 'N/A')}")
            print(f"  Salary: {row.get('MIN_AMOUNT', 'N/A')} - {row.get('MAX_AMOUNT', 'N/A')}")
            print(f"  URL: {row.get('JOB_URL', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ JobSpy search failed: {e}")
        return False

def test_app_integration():
    """Test the app's job search function."""
    try:
        from app import search_jobs_api
        
        print("\n🔍 Testing app integration...")
        
        # Test job search through the app
        jobs = search_jobs_api(
            title="software engineer",
            location="San Francisco",
            limit=3
        )
        
        if not jobs:
            print("⚠️  No jobs returned from app function")
            return False
        
        print(f"✅ App returned {len(jobs)} jobs")
        print("\n📋 Sample jobs from app:")
        
        for i, job in enumerate(jobs[:2]):
            print(f"\nJob {i+1}:")
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Company: {job.get('company', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Salary: {job.get('salary', 'N/A')}")
            print(f"  URL: {job.get('url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all JobSpy tests."""
    print("🧪 JobSpy Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Import
    if not test_jobspy_import():
        print("\n❌ JobSpy is not available. Install with: pip install python-jobspy")
        print("The app will use simulated job data instead.")
        return
    
    # Test 2: Basic search
    if not test_jobspy_search():
        print("\n⚠️  JobSpy search failed. This might be due to:")
        print("   - Network connectivity issues")
        print("   - Rate limiting from job boards")
        print("   - JobSpy version compatibility")
        print("The app will use simulated job data instead.")
        return
    
    # Test 3: App integration
    if not test_app_integration():
        print("\n❌ App integration failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All JobSpy tests passed!")
    print("✅ Real job scraping is working correctly")

if __name__ == "__main__":
    main()
