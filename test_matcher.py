#!/usr/bin/env python3

import asyncio
from utils.job_matcher import JobMatcher

async def quick_test():
    matcher = JobMatcher()
    
    # Test just the job search part first
    search_profile = {'query': 'python developer', 'location': 'United States'}
    jobs = await matcher.job_search.search_jobs(search_profile)
    
    print(f"Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"- {job['title']} at {job['company']}")
    
    return jobs

if __name__ == "__main__":
    asyncio.run(quick_test())