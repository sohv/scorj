#!/usr/bin/env python3

import asyncio
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup


class JobSearch:
    async def search_jobs(self, search_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Searches for jobs on LinkedIn based on a search profile.
        """
        print(f"Searching for jobs on LinkedIn with profile: {search_profile}")

        query = search_profile.get('query', '')
        location = search_profile.get('location', 'United States')

        # Construct the LinkedIn search URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs from LinkedIn: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        job_postings = []
        job_cards = soup.find_all('div', class_='base-card')

        for card in job_cards:
            try:
                title = card.find('h3', class_='base-search-card__title').text.strip()
                company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                location = card.find('span', class_='job-search-card__location').text.strip()
                # The full description is not available on the search results page.
                # We would need to make a separate request to the job details page for that.
                # For now, we'll use a placeholder.
                description = f"Job description for {title} at {company}. More details on the job page."

                job_postings.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                })
            except AttributeError:
                # Ignore cards that don't have the expected structure
                continue

        return job_postings
