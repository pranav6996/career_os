#!/usr/bin/env python
"""
Test script for job scraper
Run this to test the scraping functionality
"""

import sys
import os

# Ensure project root is on Python path
sys.path.insert(0, os.path.dirname(__file__))

from jobs.scraper import (
    JobScraperService,
    LinkedInScraper,
    InternshalaScaper,
    WeWorkRemotelyScraper,
    RemoteOKScraper,
    NaukriScraper,
    ResumeParser
)


def test_individual_scrapers():
    """Test each scraper individually"""
    print("=" * 80)
    print("TESTING INDIVIDUAL SCRAPERS")
    print("=" * 80)
    
    keywords = ['python', 'developer', 'intern']
    location = 'India'
    
    scrapers = {
        'LinkedIn': LinkedInScraper(),
        'Internshala': InternshalaScaper(),
        'WeWorkRemotely': WeWorkRemotelyScraper(),
        'RemoteOK': RemoteOKScraper(),
        'Naukri': NaukriScraper(),
    }
    
    all_results = []
    
    for name, scraper in scrapers.items():
        print(f"\n{name}:")
        print("-" * 40)
        try:
            jobs = scraper.scrape(keywords, location, limit=2)
            for i, job in enumerate(jobs, 1):
                print(f"\n  Job {i}:")
                print(f"    Title: {job['title']}")
                print(f"    Company: {job['company']}")
                print(f"    Link: {job['link']}")
                print(f"    Location: {job['location']}")
                all_results.append(job)
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    return all_results


def test_full_service():
    """Test the full scraping service"""
    print("\n" + "=" * 80)
    print("TESTING FULL SCRAPER SERVICE")
    print("=" * 80)
    
    # Create a dummy resume scenario
    print("\nSimulating resume with keywords: python, django, developer, intern")
    
    service = JobScraperService()
    
    # Since we don't have an actual resume file, we'll test with predefined keywords
    keywords = ['python', 'django', 'developer', 'intern']
    location = 'India'
    
    print(f"\nKeywords: {', '.join(keywords)}")
    print(f"Location: {location}")
    print(f"\nScraping 2 jobs from each platform...")
    
    all_jobs = []
    
    for platform_name, scraper in service.scrapers.items():
        print(f"\n{platform_name.upper()}:")
        print("-" * 40)
        try:
            jobs = scraper.scrape(keywords, location, 2)
            for i, job in enumerate(jobs, 1):
                print(f"\n  Job {i}:")
                print(f"Title: {job['title']}")
                print(f"Company: {job['company']}")
                print(f"Platform: {job['platform']}")
                print(f"Link: {job['link']}")
                all_jobs.append(job)
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    return all_jobs


def print_summary(jobs):
    """Print summary of scraped jobs"""
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal jobs scraped: {len(jobs)}")
    # Count by platform
    platforms = {}
    for job in jobs:
        platform = job['platform']
        platforms[platform] = platforms.get(platform, 0) + 1
    print("\nJobs by platform:")
    for platform, count in platforms.items():
        print(f"  {platform}: {count}")
    print("\n" + "=" * 80)
    print("ALL JOB LINKS")
    print("=" * 80)
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']} at {job['company']} ({job['platform']})")
        print(f"   Link: {job['link']}")

if __name__ == '__main__':
    print("scraping started......")
    try:
        # Test full service
        jobs = test_full_service()
        
        # Print summary
        print_summary(jobs)
        
        print("\n✅ Testing completed successfully!")
        print("\nNote: These are working job board search URLs.")
        print("The actual job listings may vary based on availability.")
        print("\nTo use with Django:")
        print("1. Set up your Django project")
        print("2. Run migrations: python manage.py migrate")
        print("3. Upload a resume through the web interface")
        print("4. The system will automatically scrape jobs based on your resume")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()