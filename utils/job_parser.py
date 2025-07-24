import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse
import os
import json
import time
import hashlib
from pathlib import Path
from openai import OpenAI

from config import config
from utils.error_handling import error_handler, ComponentMonitor, ErrorCategory, ErrorSeverity
from utils.enhanced_skills_matcher import skills_matcher

class JobDescriptionParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        
        parser_config = config.job_parser
        self.user_agents = parser_config.user_agents
        self.max_retries = parser_config.max_retries
        self.retry_delay = parser_config.retry_delay
        self.cache_enabled = parser_config.cache_enabled
        self.timeout = parser_config.timeout
        
        self.cache_dir = Path(config.cache.base_dir) / config.cache.job_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def parse_linkedin_job(self, url: str) -> Dict[str, str]:
        if not self._is_valid_linkedin_url(url):
            raise ValueError("Invalid LinkedIn job URL")

        with ComponentMonitor("job_parser", error_handler) as monitor:
            return self._parse_with_monitoring(url)

    def _parse_with_monitoring(self, url: str) -> Dict[str, str]:
        if self.cache_enabled:
            cached_data = self._get_cached_job_data(url)
            if cached_data:
                error_handler.logger.info("Using cached job data for URL")
                return cached_data

        for attempt in range(self.max_retries):
            headers = self._get_request_headers(attempt)
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            job_data = self._extract_job_data_with_fallbacks(soup, url)
            
            if self._validate_job_data_enhanced(job_data):
                if self.cache_enabled:
                    self._cache_job_data(url, job_data)
                return job_data
            else:
                if attempt == self.max_retries - 1:
                    raise Exception("Could not extract meaningful job data after all attempts")
                continue

    def _get_request_headers(self, attempt: int) -> Dict[str, str]:
        return {
            'User-Agent': self.user_agents[attempt % len(self.user_agents)],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _extract_job_data_with_fallbacks(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        title = self._extract_title(soup)
        company = self._extract_company(soup)
        location = self._extract_location(soup)
        description = self._extract_description(soup)
        
        if not description or description == "Job description not available":
            structured_data = soup.find('script', type='application/ld+json')
            if structured_data:
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
        
        return job_data

    def _validate_job_data_enhanced(self, job_data: Dict[str, str]) -> bool:
        description = job_data.get('description', '')
        title = job_data.get('title', '')
        skills = job_data.get('skills', [])
        
        if not description or len(description.strip()) < 50:
            error_handler.logger.warning(f"Description too short: {len(description.strip()) if description else 0} chars")
            return False
            
        if title == "Unknown Position":
            error_handler.logger.warning("Could not extract job title")
            return False
        
        if skills_matcher and isinstance(skills, list) and len(skills) == 0:
            extracted_skills = skills_matcher.extract_skills_from_text(description)
            if len(extracted_skills) == 0:
                error_handler.logger.warning("No technical skills detected in job description")
        
        return True

    def _is_valid_linkedin_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        linkedin_domains = ['www.linkedin.com', 'linkedin.com', 'linked.in']
        job_patterns = ['/jobs/view/', '/jobs/collections/', '/jobs/']
        
        return (
            parsed_url.netloc in linkedin_domains and
            any(pattern in url for pattern in job_patterns)
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
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
        
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title.get('content')
        
        return "Unknown Position"

    def _extract_company(self, soup: BeautifulSoup) -> str:
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
        
        meta_company = soup.find('meta', property='og:site_name')
        if meta_company and meta_company.get('content'):
            return meta_company.get('content')
        
        return "Unknown Company"

    def _extract_location(self, soup: BeautifulSoup) -> str:
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
        
        structured_data = soup.find('script', type='application/ld+json')
        if structured_data:
            data = json.loads(structured_data.string)
            if isinstance(data, dict) and 'description' in data:
                return data['description']
        
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')
        
        text_blocks = soup.find_all(['div', 'section', 'article'])
        for block in text_blocks:
            text = block.get_text(strip=True)
            if len(text) > 500 and any(keyword in text.lower() for keyword in ['responsibilities', 'requirements', 'qualifications', 'experience', 'skills']):
                return text
        
        return "Job description not available"

    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        requirements = []
        req_section = soup.find('div', string=re.compile(r'(?i)requirements|qualifications'))
        if req_section:
            req_items = req_section.find_all('li')
            requirements = [item.text.strip() for item in req_items]
        return requirements

    def _extract_benefits(self, soup: BeautifulSoup) -> List[str]:
        benefits = []
        benefits_section = soup.find('div', string=re.compile(r'(?i)benefits|perks'))
        if benefits_section:
            benefit_items = benefits_section.find_all('li')
            benefits = [item.text.strip() for item in benefit_items]
        return benefits

    def extract_skills(self, description: str) -> List[str]:
        if skills_matcher:
            taxonomy_skills = skills_matcher.extract_skills_from_text(description)
            ai_skills = self._extract_skills_openai(description)
            all_skills = list(taxonomy_skills.union(set(ai_skills)))
            error_handler.logger.info(f"Extracted {len(all_skills)} skills using enhanced matching")
            return all_skills
        else:
            return self._extract_skills_openai(description)

    def _extract_skills_openai(self, description: str) -> List[str]:
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

    def _extract_requirements_openai(self, description: str) -> List[str]:
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

    def extract_experience_level(self, description: str) -> str:
        return self._extract_experience_level_openai(description)

    def _extract_experience_level_openai(self, description: str) -> str:
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
        
        if level in ['entry', 'mid', 'senior', 'not specified']:
            return level
        else:
            return 'not specified'

    def _extract_experience_level_regex(self, description: str) -> str:
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
        title_match = re.search(r'^([^(]+?)(?:\s*\([^)]*\))?', text.strip())
        title = title_match.group(1).strip() if title_match else "Unknown Position"
        
        company_match = re.search(r'(?i)about\s+([^:]+):', text)
        company = company_match.group(1).strip() if company_match else "Unknown Company"
        
        location_match = re.search(r'(?i)location:\s*([^\n]+)', text)
        location = location_match.group(1).strip() if location_match else "Not specified"
        
        experience = self.extract_experience_level(text)
        skills = self.extract_skills(text)
        requirements = self._extract_requirements_openai(text)
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

    def _get_cache_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cached_job_data(self, url: str) -> Optional[Dict[str, str]]:
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < 86400:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None

    def _cache_job_data(self, url: str, job_data: Dict[str, str]) -> None:
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)

    def clear_cache(self) -> None:
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()