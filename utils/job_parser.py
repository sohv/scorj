import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse

class JobDescriptionParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_linkedin_job(self, url: str) -> Dict[str, str]:
        """Extract and structure job description from LinkedIn URL."""
        if not self._is_valid_linkedin_url(url):
            raise ValueError("Invalid LinkedIn job URL")

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job details
            job_data = {
                'title': self._extract_title(soup),
                'company': self._extract_company(soup),
                'location': self._extract_location(soup),
                'description': self._extract_description(soup),
                'requirements': self._extract_requirements(soup),
                'benefits': self._extract_benefits(soup)
            }
            
            return job_data
        except requests.RequestException as e:
            raise Exception(f"Error fetching job description: {str(e)}")

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate if the URL is a LinkedIn job posting."""
        parsed_url = urlparse(url)
        return (
            (parsed_url.netloc == 'www.linkedin.com' or parsed_url.netloc == 'linkedin.com') and
            ('/jobs/view/' in url or '/jobs/collections/' in url)
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from the page."""
        title_elem = soup.find('h1', class_='job-details-jobs-unified-top-card__job-title')
        return title_elem.text.strip() if title_elem else ""

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name from the page."""
        company_elem = soup.find('a', class_='job-details-jobs-unified-top-card__company-name')
        return company_elem.text.strip() if company_elem else ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract job location from the page."""
        location_elem = soup.find('span', class_='job-details-jobs-unified-top-card__bullet')
        return location_elem.text.strip() if location_elem else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from the page."""
        desc_elem = soup.find('div', class_='job-details-jobs-unified-top-card__job-description')
        return desc_elem.text.strip() if desc_elem else ""

    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """Extract job requirements from the page."""
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
        """Extract required skills from job description."""
        # Common skill patterns
        skill_patterns = [
            r'(?i)(python|java|javascript|typescript|react|angular|vue|node\.js|express|django|flask|fastapi)',
            r'(?i)(aws|azure|gcp|cloud|docker|kubernetes|terraform)',
            r'(?i)(sql|mysql|postgresql|mongodb|redis|elasticsearch)',
            r'(?i)(machine learning|deep learning|ai|nlp|computer vision)',
            r'(?i)(agile|scrum|kanban|ci/cd|devops)'
        ]

        skills = set()
        for pattern in skill_patterns:
            matches = re.finditer(pattern, description)
            for match in matches:
                skills.add(match.group().lower())

        return list(skills)

    def extract_experience_level(self, description: str) -> str:
        """Extract required experience level from job description."""
        experience_patterns = {
            'entry': r'(?i)(entry|junior|0-2|1-2|1-3)',
            'mid': r'(?i)(mid|intermediate|3-5|4-6)',
            'senior': r'(?i)(senior|lead|5\+|6\+|7\+)'
        }

        for level, pattern in experience_patterns.items():
            if re.search(pattern, description):
                return level
        return 'not specified'