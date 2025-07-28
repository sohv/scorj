#!/usr/bin/env python3

import asyncio
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse


class JobSearch:
    def __init__(self):
        self.session = requests.Session()
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]

    async def search_jobs(self, search_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Searches for jobs on LinkedIn with improved scraping methods.
        Falls back to mock data if scraping fails.
        """
        query = search_profile.get('query', '')
        location = search_profile.get('location', 'United States')
        
        print(f"Searching LinkedIn for: {query} in {location}")
        
        # Try LinkedIn first
        linkedin_jobs = await self._search_linkedin(query, location)
        if linkedin_jobs:
            return linkedin_jobs
        
        # Try Indeed as backup
        indeed_jobs = await self._search_indeed(query, location)
        if indeed_jobs:
            return indeed_jobs
            
        # Fall back to mock data if all fail
        print("Real job search failed, using mock data")
        return self._get_mock_jobs(query)

    async def _search_linkedin(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Try to scrape LinkedIn jobs"""
        try:
            # Encode the search parameters
            encoded_query = urllib.parse.quote_plus(query)
            encoded_location = urllib.parse.quote_plus(location)
            
            # LinkedIn public jobs URL (no login required)
            url = f"https://www.linkedin.com/jobs/search?keywords={encoded_query}&location={encoded_location}&f_TPR=r86400"  # Past 24 hours
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Add random delay to avoid rate limiting
            await asyncio.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"LinkedIn response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"LinkedIn returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # LinkedIn job cards - try multiple selectors
            job_selectors = [
                'div[data-view-name="job-search-card"]',
                '.job-search-card',
                '.jobs-search__results-list li',
                'div.base-card'
            ]
            
            job_cards = []
            for selector in job_selectors:
                job_cards = soup.select(selector)
                if job_cards:
                    print(f"Found {len(job_cards)} jobs using selector: {selector}")
                    break
            
            if not job_cards:
                print("No job cards found with any selector")
                return []
                
            for card in job_cards[:10]:  # Limit to 10 jobs
                try:
                    # Try different selectors for job data
                    title_elem = (card.select_one('.base-search-card__title') or 
                                card.select_one('h3 a') or 
                                card.select_one('.job-title'))
                    
                    company_elem = (card.select_one('.base-search-card__subtitle') or
                                  card.select_one('.job-search-card__subtitle-primary-grouping') or
                                  card.select_one('h4'))
                    
                    location_elem = (card.select_one('.job-search-card__location') or
                                   card.select_one('.base-search-card__metadata'))
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Create a basic job description from available info
                        description = f"Job opening for {title} at {company}. Location: {location_text}. This is a real job posting from LinkedIn. For full details, please visit the LinkedIn job page."
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location_text,
                            'description': description,
                            'source': 'LinkedIn'
                        })
                        
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            
            print(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
            return jobs
            
        except Exception as e:
            print(f"LinkedIn scraping failed: {e}")
            return []

    async def _search_indeed(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Try Indeed as backup"""
        try:
            encoded_query = urllib.parse.quote_plus(query)
            encoded_location = urllib.parse.quote_plus(location)
            
            url = f"https://www.indeed.com/jobs?q={encoded_query}&l={encoded_location}&sort=date"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            await asyncio.sleep(random.uniform(1, 2))
            
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"Indeed response status: {response.status_code}")
            
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Indeed job cards
            job_cards = soup.select('[data-jk]')  # Indeed uses data-jk attribute
            
            for card in job_cards[:8]:  # Limit to 8 jobs
                try:
                    title_elem = card.select_one('h2 a span[title]')
                    company_elem = card.select_one('[data-testid="company-name"]')
                    location_elem = card.select_one('[data-testid="job-location"]')
                    
                    if title_elem and company_elem:
                        title = title_elem.get('title', '').strip()
                        company = company_elem.get_text(strip=True)
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        
                        description = f"Job opening for {title} at {company}. Location: {location_text}. This is a real job posting from Indeed. For full details, please visit the Indeed job page."
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location_text,
                            'description': description,
                            'source': 'Indeed'
                        })
                        
                except Exception as e:
                    continue
            
            print(f"Successfully scraped {len(jobs)} jobs from Indeed")
            return jobs
            
        except Exception as e:
            print(f"Indeed scraping failed: {e}")
            return []

    def _get_mock_jobs(self, query: str) -> List[Dict[str, Any]]:
        """Fallback mock jobs with query filtering"""
        mock_jobs = [
            {
                'title': 'Software Engineer',
                'company': 'TechCorp',
                'location': 'San Francisco, CA',
                'description': '''We are looking for a Software Engineer to join our team. 
                Requirements: Python, JavaScript, React, Node.js, SQL, Git.
                Experience with AWS, Docker, and microservices preferred.
                Bachelor's degree in Computer Science or related field.
                2-4 years of experience in software development.''',
                'source': 'Mock Data'
            },
            {
                'title': 'Data Scientist',
                'company': 'DataCorp',
                'location': 'New York, NY',
                'description': '''Seeking a Data Scientist to analyze complex datasets.
                Requirements: Python, R, SQL, Machine Learning, Statistics.
                Experience with TensorFlow, PyTorch, Pandas, NumPy.
                Advanced degree in Data Science, Statistics, or related field.
                3-5 years of experience in data analysis and modeling.''',
                'source': 'Mock Data'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'WebSolutions',
                'location': 'Austin, TX',
                'description': '''Full Stack Developer needed for web applications.
                Requirements: JavaScript, TypeScript, React, Node.js, MongoDB.
                Experience with Next.js, Express.js, and RESTful APIs.
                Bachelor's degree in Computer Science.
                2-5 years of full stack development experience.''',
                'source': 'Mock Data'
            }
        ]
        
        # Filter by query if provided
        if query:
            query_lower = query.lower()
            filtered = [job for job in mock_jobs 
                       if query_lower in job['title'].lower() or 
                          query_lower in job['description'].lower()]
            return filtered if filtered else mock_jobs
        
        return mock_jobs
