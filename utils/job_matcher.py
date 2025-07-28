#!/usr/bin/env python3

import asyncio
from typing import Dict, Any, List
from collections import Counter

from .resume_parser import ResumeParser
from .job_parser import JobDescriptionParser
from .scoring_engine_openai import ScoringEngine
from .job_search import JobSearch


class JobMatcher:
    def __init__(self):
        self.resume_parser = ResumeParser()
        self.job_parser = JobDescriptionParser()
        self.scoring_engine = ScoringEngine()
        self.job_search = JobSearch()

    async def find_best_jobs(self, resume_path: str) -> List[Dict[str, Any]]:
        """
        Finds the top 5 best job matches for a given resume.
        """
        # 1. Parse the resume
        with open(resume_path, 'rb') as f:
            resume_data = self.resume_parser.parse_pdf(f)

        # 2. Create a search profile from the resume
        search_profile = self._create_search_profile(resume_data)

        # 3. Search for jobs based on the profile
        job_postings = await self.job_search.search_jobs(search_profile)

        # 4. Score and rank the jobs
        scored_jobs = []
        for job_posting in job_postings:
            job_data = self.job_parser.parse_job_description_text(job_posting['description'])
            score = self.scoring_engine.calculate_score(resume_data, job_data)
            scored_jobs.append({
                'job': job_posting,
                'score': score['final_score']
            })

        # 5. Sort by score and return the top 5
        scored_jobs.sort(key=lambda x: x['score'], reverse=True)
        return scored_jobs[:5]

    def _create_search_profile(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a more sophisticated search profile from the parsed resume data.
        """
        # Extract skills and count their frequency
        skills = resume_data.get('extracted_skills', [])
        skill_counts = Counter(skills)
        # Get the top 5 most frequent skills
        top_skills = [skill for skill, count in skill_counts.most_common(5)]

        # Get the most recent job title
        experience = resume_data.get('sections', {}).get('experience', [])
        latest_job_title = ''
        if experience:
            first_exp = experience[0]
            if isinstance(first_exp, dict):
                latest_job_title = first_exp.get('title', '')
            elif isinstance(first_exp, str):
                # Take the first line of the string as a proxy for the title
                latest_job_title = first_exp.split('\n')[0]

        # Get education details
        education = resume_data.get('sections', {}).get('education', [])
        degree = ''
        field_of_study = ''
        if education:
            first_edu = education[0]
            if isinstance(first_edu, dict):
                degree = first_edu.get('degree', '')
                field_of_study = first_edu.get('field', '')
            elif isinstance(first_edu, str):
                # Use the first line of the education string
                degree = first_edu.split('\n')[0]

        # Construct a more detailed search query
        query_parts = [latest_job_title, degree, field_of_study] + top_skills
        search_query = ' '.join(filter(None, query_parts))

        return {
            'query': search_query,
            'location': 'United States',  # Can be made dynamic
        }


async def main():
    matcher = JobMatcher()
    # This is a placeholder for a real resume path
    resume_path = 'sample.pdf'
    top_jobs = await matcher.find_best_jobs(resume_path)

    print("Top 5 Job Matches:")
    for job in top_jobs:
        print(f"  - {job['job']['title']} at {job['job']['company']} (Score: {job['score']})")


if __name__ == "__main__":
    asyncio.run(main())
