import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse
import os
import json
from openai import OpenAI

class JobDescriptionParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_linkedin_job(self, url: str) -> Dict[str, str]:
        """Extract and structure job description from LinkedIn URL."""
        if not self._is_valid_linkedin_url(url):
            raise ValueError("Invalid LinkedIn job URL")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job details
            title = self._extract_title(soup)
            company = self._extract_company(soup)
            location = self._extract_location(soup)
            description = self._extract_description(soup)
            
            # If we couldn't extract the description, try alternative methods
            if not description or description == "Job description not available":
                # Try to extract from structured data
                structured_data = soup.find('script', type='application/ld+json')
                if structured_data:
                    import json
                    data = json.loads(structured_data.string)
                    if isinstance(data, dict) and 'description' in data:
                        description = data['description']
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'requirements': self._extract_requirements_openai(description),
                'benefits': self._extract_benefits(soup),
                'skills': self._extract_skills_openai(description),
                'experience_level': self._extract_experience_level_openai(description)
            }
            
            # Validate that we got some meaningful data
            if not description or len(description.strip()) < 50:
                print(f"Debug: Extracted description length: {len(description.strip()) if description else 0}")
                print(f"Debug: Description preview: {description[:200] if description else 'None'}")
                raise Exception("Could not extract meaningful job description from LinkedIn page. The page might require authentication or have changed its structure.")
            
            return job_data
        except requests.RequestException as e:
            raise Exception(f"Error fetching job description: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing LinkedIn job page: {str(e)}")

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate if the URL is a LinkedIn job posting."""
        parsed_url = urlparse(url)
        linkedin_domains = ['www.linkedin.com', 'linkedin.com', 'linked.in']
        job_patterns = ['/jobs/view/', '/jobs/collections/', '/jobs/']
        
        return (
            parsed_url.netloc in linkedin_domains and
            any(pattern in url for pattern in job_patterns)
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from the page."""
        # Try multiple selectors for job title
        title_selectors = [
            'h1.job-details-jobs-unified-top-card__job-title',
            'h1[data-test-id="job-details-jobs-unified-top-card__job-title"]',
            'h1.jobs-unified-top-card__job-title',
            'h1[class*="job-title"]',
            'h1[class*="title"]',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.text.strip():
                return title_elem.text.strip()
        
        # Fallback: look for title in meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title.get('content')
        
        return "Unknown Position"

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name from the page."""
        # Try multiple selectors for company name
        company_selectors = [
            'a.job-details-jobs-unified-top-card__company-name',
            'a[data-test-id="job-details-jobs-unified-top-card__company-name"]',
            'a.jobs-unified-top-card__company-name',
            'a[class*="company-name"]',
            'a[class*="company"]',
            'span[class*="company"]'
        ]
        
        for selector in company_selectors:
            company_elem = soup.select_one(selector)
            if company_elem and company_elem.text.strip():
                return company_elem.text.strip()
        
        # Fallback: look for company in meta tags
        meta_company = soup.find('meta', property='og:site_name')
        if meta_company and meta_company.get('content'):
            return meta_company.get('content')
        
        return "Unknown Company"

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract job location from the page."""
        # Try multiple selectors for location
        location_selectors = [
            'span.job-details-jobs-unified-top-card__bullet',
            'span[data-test-id="job-details-jobs-unified-top-card__bullet"]',
            'span.jobs-unified-top-card__bullet',
            'span[class*="location"]',
            'span[class*="bullet"]',
            'div[class*="location"]'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem and location_elem.text.strip():
                return location_elem.text.strip()
        
        return "Location not specified"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from the page."""
        # Try multiple selectors for job description
        desc_selectors = [
            'div.job-details-jobs-unified-top-card__job-description',
            'div[data-test-id="job-details-jobs-unified-top-card__job-description"]',
            'div.jobs-unified-top-card__job-description',
            'div[class*="job-description"]',
            'div[class*="description"]',
            'section[class*="description"]',
            'div[data-job-description]',
            'div[class*="show-more-less-html"]',
            'div[class*="show-more-less-text"]',
            'div[class*="jobs-description"]',
            'div[class*="jobs-box__html-content"]',
            'div[class*="jobs-description-content"]'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem and desc_elem.text.strip():
                return desc_elem.text.strip()
        
        # Try to find description in structured data
        structured_data = soup.find('script', type='application/ld+json')
        if structured_data:
            data = json.loads(structured_data.string)
            if isinstance(data, dict) and 'description' in data:
                return data['description']
        
        # Fallback: look for description in meta tags
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')
        
        # Look for any div with substantial text content that might be the description
        text_blocks = soup.find_all(['div', 'section', 'article'])
        for block in text_blocks:
            text = block.get_text(strip=True)
            # Look for blocks with substantial content that might be job descriptions
            if len(text) > 500 and any(keyword in text.lower() for keyword in ['responsibilities', 'requirements', 'qualifications', 'experience', 'skills']):
                return text
        
        return "Job description not available"

    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """Extract job requirements from the page (fallback method)."""
        requirements = []
        req_section = soup.find('div', string=re.compile(r'(?i)requirements|qualifications'))
        if req_section:
            req_items = req_section.find_all('li')
            requirements = [item.text.strip() for item in req_items]
        return requirements

    def _extract_benefits(self, soup: BeautifulSoup) -> List[str]:
        """Extract job benefits from the page."""
        benefits = []
        benefits_section = soup.find('div', string=re.compile(r'(?i)benefits|perks'))
        if benefits_section:
            benefit_items = benefits_section.find_all('li')
            benefits = [item.text.strip() for item in benefit_items]
        return benefits

    def extract_skills(self, description: str) -> List[str]:
        """Extract required skills from job description using OpenAI."""
        return self._extract_skills_openai(description)

    def _extract_skills_openai(self, description: str) -> List[str]:
        """Extract skills using OpenAI."""
        try:
            prompt = f"""
            Extract all required and preferred skills from this job description. Include:
            - Programming languages
            - Frameworks and libraries
            - Tools and software
            - Technical skills
            - Methodologies
            - Certifications
            - Soft skills
            - Industry-specific skills
            
            Return a JSON object with a "skills" array containing all relevant skills as strings.
            
            Job description:
            {description}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting skills and requirements from job descriptions. Return structured JSON data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('skills', [])
            
        except Exception as e:
            print(f"OpenAI skill extraction failed: {e}")
            return []

    def _extract_requirements_openai(self, description: str) -> List[str]:
        """Extract job requirements using OpenAI."""
        try:
            prompt = f"""
            Extract the key requirements from this job description. Focus on:
            - Must-have qualifications
            - Required experience
            - Essential skills
            - Educational requirements
            - Certifications needed
            
            Return a JSON object with a "requirements" array containing concise requirement statements.
            
            Job description:
            {description}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting job requirements. Return structured JSON data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('requirements', [])
            
        except Exception as e:
            print(f"OpenAI requirements extraction failed: {e}")
            return []

    def extract_experience_level(self, description: str) -> str:
        """Extract required experience level from job description using OpenAI."""
        return self._extract_experience_level_openai(description)

    def _extract_experience_level_openai(self, description: str) -> str:
        """Extract experience level using OpenAI."""
        try:
            prompt = f"""
            Analyze this job description and determine the required experience level. 
            Return one of these exact values: "entry", "mid", "senior", or "not specified"
            
            Guidelines:
            - "entry": 0-2 years, junior positions, entry-level, new grad
            - "mid": 3-6 years, intermediate, mid-level
            - "senior": 7+ years, senior, lead, principal positions
            - "not specified": if experience level is unclear or not mentioned
            
            Return a JSON object with "experience_level" key.
            
            Job description:
            {description}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing job requirements. Return structured JSON data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            level = result.get('experience_level', 'not specified')
            
            # Validate the response
            if level in ['entry', 'mid', 'senior', 'not specified']:
                return level
            else:
                return 'not specified'
                
        except Exception as e:
            print(f"OpenAI experience level extraction failed, falling back to regex: {e}")
            return self._extract_experience_level_regex(description)

    def _extract_experience_level_regex(self, description: str) -> str:
        """Fallback regex-based experience level extraction."""
        experience_patterns = {
            'entry': r'(?i)(entry|junior|0-2|1-2|1-3)',
            'mid': r'(?i)(mid|intermediate|3-5|4-6)',
            'senior': r'(?i)(senior|lead|5\+|6\+|7\+)'
        }

        for level, pattern in experience_patterns.items():
            if re.search(pattern, description):
                return level
        return 'not specified'

    def parse_job_description_text(self, text: str) -> Dict[str, str]:
        """Parse job description from pasted text."""
        try:
            # Extract job title (usually at the beginning)
            title_match = re.search(r'^([^(]+?)(?:\s*\([^)]*\))?', text.strip())
            title = title_match.group(1).strip() if title_match else "Unknown Position"
            
            # Extract company name (look for patterns like "About CompanyName:")
            company_match = re.search(r'(?i)about\s+([^:]+):', text)
            company = company_match.group(1).strip() if company_match else "Unknown Company"
            
            # Extract location
            location_match = re.search(r'(?i)location:\s*([^\n]+)', text)
            location = location_match.group(1).strip() if location_match else "Not specified"
            
            # Extract experience level
            experience = self.extract_experience_level(text)
            
            # Extract skills
            skills = self.extract_skills(text)
            
            # Extract requirements
            requirements = self._extract_requirements_openai(text)
            
            # The full description is the entire text
            description = text.strip()
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'requirements': requirements,
                'benefits': [],
                'skills': skills,
                'experience_level': experience
            }
        except Exception as e:
            raise Exception(f"Error parsing job description text: {str(e)}")