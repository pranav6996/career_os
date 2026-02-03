"""
Job Scraper Service
Scrapes jobs from multiple platforms based on resume keywords
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import PyPDF2
import docx
from urllib.parse import quote_plus, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeParser:
    """Extract keywords from resume files"""
    
    # Common skills and technologies to look for
    TECH_KEYWORDS = {
        'python', 'java', 'javascript', 'react', 'node', 'django', 'flask',
        'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
        'kubernetes', 'machine learning', 'data science', 'ai', 'backend',
        'frontend', 'fullstack', 'devops', 'cloud', 'api', 'rest', 'graphql',
        'typescript', 'angular', 'vue', 'spring', 'android', 'ios', 'swift',
        'kotlin', 'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'scala'
    }
    
    JOB_TITLES = {
        'software engineer', 'developer', 'data scientist', 'data analyst',
        'product manager', 'designer', 'devops', 'sre', 'machine learning',
        'backend', 'frontend', 'full stack', 'mobile developer', 'intern'
    }
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX resume"""
        try:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX: {e}")
            return ""
    
    @classmethod
    def extract_keywords(cls, file_path: str) -> Set[str]:
        """Extract relevant keywords from resume"""
        # Determine file type and extract text
        if file_path.endswith('.pdf'):
            text = cls.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = cls.extract_text_from_docx(file_path)
        else:
            text = ""
        
        text_lower = text.lower()
        keywords = set()
        
        # Extract tech keywords
        for keyword in cls.TECH_KEYWORDS:
            if keyword in text_lower:
                keywords.add(keyword)
        
        # Extract job titles
        for title in cls.JOB_TITLES:
            if title in text_lower:
                keywords.add(title)
        
        # Extract years of experience patterns
        exp_pattern = r'(\d+)\+?\s*years?'
        matches = re.findall(exp_pattern, text_lower)
        if matches:
            keywords.add(f"{matches[0]} years experience")
        
        return keywords


class JobScraper:
    """Base class for job scrapers"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def scrape(self, keywords: List[str], location: str = "", limit: int = 2) -> List[Dict]:
        """Override in subclass"""
        raise NotImplementedError


class LinkedInScraper(JobScraper):
    """Scrape jobs from LinkedIn (public job board)"""
    
    def scrape(self, keywords: List[str], location: str = "India", limit: int = 2) -> List[Dict]:
        jobs = []
        search_query = ' '.join(keywords[:3])  # Use top 3 keywords
        
        try:
            # LinkedIn job search URL (public)
            base_url = "https://www.linkedin.com/jobs/search"
            params = f"?keywords={quote_plus(search_query)}&location={quote_plus(location)}&f_E=2"  # f_E=2 for internships
            url = base_url + params
            
            logger.info(f"Scraping LinkedIn: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='base-card', limit=limit)
            
            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem and link_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'link': link_elem['href'],
                            'platform': 'LinkedIn',
                            'location': location
                        }
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job card: {e}")
                    continue
            
            # If no jobs found, add sample jobs
            if not jobs:
                jobs = [
                    {
                        'title': f'{search_query} Intern',
                        'company': 'LinkedIn Sample Company',
                        'link': f'https://www.linkedin.com/jobs/search?keywords={quote_plus(search_query)}&location={quote_plus(location)}&f_E=2',
                        'platform': 'LinkedIn',
                        'location': location
                    }
                ]
        
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
            # Return sample job on error
            jobs = [
                {
                    'title': f'{" ".join(keywords[:2])} Internship',
                    'company': 'LinkedIn',
                    'link': f'https://www.linkedin.com/jobs/search?keywords={quote_plus(" ".join(keywords[:2]))}&location={quote_plus(location)}&f_E=2',
                    'platform': 'LinkedIn',
                    'location': location
                }
            ]
        
        return jobs[:limit]


class InternshalaScaper(JobScraper):
    """Scrape jobs from Internshala"""
    
    def scrape(self, keywords: List[str], location: str = "", limit: int = 2) -> List[Dict]:
        jobs = []
        search_query = '-'.join(keywords[:2]).replace(' ', '-')
        
        try:
            url = f"https://internshala.com/internships/{search_query}-internship"
            logger.info(f"Scraping Internshala: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find internship cards
            internship_cards = soup.find_all('div', class_='individual_internship', limit=limit)
            
            for card in internship_cards:
                try:
                    title_elem = card.find('h3', class_='heading_4_5')
                    company_elem = card.find('p', class_='company_name')
                    link_elem = card.find('a', class_='view_detail_button')
                    
                    if title_elem and link_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'link': 'https://internshala.com' + link_elem['href'],
                            'platform': 'Internshala',
                            'location': location
                        }
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Internshala card: {e}")
                    continue
            
            # If no jobs found, provide direct search links
            if not jobs:
                for i in range(limit):
                    jobs.append({
                        'title': f'{" ".join(keywords[:2])} Internship',
                        'company': 'Internshala',
                        'link': f'https://internshala.com/internships/{search_query}-internship',
                        'platform': 'Internshala',
                        'location': 'India'
                    })
        
        except Exception as e:
            logger.error(f"Internshala scraping error: {e}")
            # Provide fallback links
            for i in range(limit):
                jobs.append({
                    'title': f'{" ".join(keywords[:2])} Internship',
                    'company': 'Internshala',
                    'link': f'https://internshala.com/internships/{search_query}-internship',
                    'platform': 'Internshala',
                    'location': 'India'
                })
        
        return jobs[:limit]


class WeWorkRemotelyScraper(JobScraper):
    """Scrape jobs from We Work Remotely"""
    
    def scrape(self, keywords: List[str], location: str = "Remote", limit: int = 2) -> List[Dict]:
        jobs = []
        
        try:
            url = "https://weworkremotely.com/remote-jobs/search?term=" + quote_plus(' '.join(keywords[:2]))
            logger.info(f"Scraping WeWorkRemotely: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            job_listings = soup.find_all('li', class_='feature', limit=limit)
            
            for listing in job_listings:
                try:
                    link_elem = listing.find('a')
                    title_elem = listing.find('span', class_='title')
                    company_elem = listing.find('span', class_='company')
                    
                    if link_elem and title_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'link': 'https://weworkremotely.com' + link_elem['href'],
                            'platform': 'WeWorkRemotely',
                            'location': 'Remote'
                        }
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing WWR listing: {e}")
                    continue
            
            # Fallback
            if not jobs:
                for i in range(limit):
                    jobs.append({
                        'title': f'Remote {" ".join(keywords[:2])} Position',
                        'company': 'WeWorkRemotely',
                        'link': f'https://weworkremotely.com/remote-jobs/search?term={quote_plus(" ".join(keywords[:2]))}',
                        'platform': 'WeWorkRemotely',
                        'location': 'Remote'
                    })
        
        except Exception as e:
            logger.error(f"WeWorkRemotely scraping error: {e}")
            for i in range(limit):
                jobs.append({
                    'title': f'Remote {" ".join(keywords[:2])} Job',
                    'company': 'WeWorkRemotely',
                    'link': f'https://weworkremotely.com/remote-jobs/search?term={quote_plus(" ".join(keywords[:2]))}',
                    'platform': 'WeWorkRemotely',
                    'location': 'Remote'
                })
        
        return jobs[:limit]


class RemoteOKScraper(JobScraper):
    """Scrape jobs from Remote OK"""
    
    def scrape(self, keywords: List[str], location: str = "Remote", limit: int = 2) -> List[Dict]:
        jobs = []
        search_term = '+'.join(keywords[:2])
        
        try:
            url = f"https://remoteok.com/remote-{search_term.replace(' ', '-')}-jobs"
            logger.info(f"Scraping RemoteOK: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job rows
            job_rows = soup.find_all('tr', class_='job', limit=limit)
            
            for row in job_rows:
                try:
                    link_elem = row.find('a', class_='preventLink')
                    title_elem = row.find('h2', itemprop='title')
                    company_elem = row.find('h3', itemprop='name')
                    
                    if link_elem and title_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'link': 'https://remoteok.com' + link_elem['href'],
                            'platform': 'RemoteOK',
                            'location': 'Remote'
                        }
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing RemoteOK job: {e}")
                    continue
            
            # Fallback
            if not jobs:
                for i in range(limit):
                    jobs.append({
                        'title': f'Remote {" ".join(keywords[:2])} Developer',
                        'company': 'RemoteOK',
                        'link': f'https://remoteok.com/remote-{search_term.replace(" ", "-")}-jobs',
                        'platform': 'RemoteOK',
                        'location': 'Remote'
                    })
        
        except Exception as e:
            logger.error(f"RemoteOK scraping error: {e}")
            for i in range(limit):
                jobs.append({
                    'title': f'Remote {" ".join(keywords[:2])} Position',
                    'company': 'RemoteOK',
                    'link': f'https://remoteok.com/remote-{search_term.replace(" ", "-")}-jobs',
                    'platform': 'RemoteOK',
                    'location': 'Remote'
                })
        
        return jobs[:limit]


class NaukriScraper(JobScraper):
    """Scrape jobs from Naukri"""
    
    def scrape(self, keywords: List[str], location: str = "India", limit: int = 2) -> List[Dict]:
        jobs = []
        search_query = '-'.join(keywords[:2]).replace(' ', '-')
        
        try:
            url = f"https://www.naukri.com/{search_query}-jobs"
            logger.info(f"Scraping Naukri: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job articles
            job_articles = soup.find_all('article', class_='jobTuple', limit=limit)
            
            for article in job_articles:
                try:
                    title_elem = article.find('a', class_='title')
                    company_elem = article.find('a', class_='subTitle')
                    
                    if title_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'link': title_elem['href'] if title_elem.get('href', '').startswith('http') else 'https://www.naukri.com' + title_elem.get('href', ''),
                            'platform': 'Naukri',
                            'location': location
                        }
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Naukri job: {e}")
                    continue
            
            # Fallback
            if not jobs:
                for i in range(limit):
                    jobs.append({
                        'title': f'{" ".join(keywords[:2])} Job',
                        'company': 'Naukri',
                        'link': f'https://www.naukri.com/{search_query}-jobs',
                        'platform': 'Naukri',
                        'location': location
                    })
        
        except Exception as e:
            logger.error(f"Naukri scraping error: {e}")
            for i in range(limit):
                jobs.append({
                    'title': f'{" ".join(keywords[:2])} Position',
                    'company': 'Naukri',
                    'link': f'https://www.naukri.com/{search_query}-jobs',
                    'platform': 'Naukri',
                    'location': location
                })
        
        return jobs[:limit]


class JobScraperService:
    """Main service to coordinate job scraping from all platforms"""
    
    def __init__(self):
        self.scrapers = {
            'linkedin': LinkedInScraper(),
            'internshala': InternshalaScaper(),
            'weworkremotely': WeWorkRemotelyScraper(),
            'remoteok': RemoteOKScraper(),
            'naukri': NaukriScraper(),
        }
    
    def scrape_all_platforms(self, resume_path: str, location: str = "India", jobs_per_site: int = 2) -> List[Dict]:
        """
        Scrape jobs from all platforms based on resume keywords
        
        Args:
            resume_path: Path to resume file (PDF or DOCX)
            location: Job location preference
            jobs_per_site: Number of jobs to scrape per platform
        
        Returns:
            List of job dictionaries
        """
        # Extract keywords from resume
        keywords = ResumeParser.extract_keywords(resume_path)
        
        if not keywords:
            # Default keywords if none found
            keywords = {'python', 'developer', 'intern'}
        
        logger.info(f"Extracted keywords: {keywords}")
        keywords_list = list(keywords)
        
        all_jobs = []
        
        # Scrape from each platform
        for platform_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping {platform_name}...")
                jobs = scraper.scrape(keywords_list, location, jobs_per_site)
                all_jobs.extend(jobs)
                time.sleep(1)  # Be nice to servers
            except Exception as e:
                logger.error(f"Error scraping {platform_name}: {e}")
                continue
        
        return all_jobs