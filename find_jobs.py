#!/usr/bin/env python3

import asyncio
import argparse

from utils.job_matcher import JobMatcher


async def main():
    parser = argparse.ArgumentParser(description='Find the best job matches for a resume.')
    parser.add_argument('resume_path', type=str, help='The path to the resume file (PDF).')
    args = parser.parse_args()

    matcher = JobMatcher()
    top_jobs = await matcher.find_best_jobs(args.resume_path)

    print("\nTop 5 Job Matches:")
    for i, job in enumerate(top_jobs, 1):
        print(f"{i}. {job['job']['title']} at {job['job']['company']}")
        print(f"   Location: {job['job']['location']}")
        print(f"   Score: {job['score']:.1f}/100")
        print(f"   Description: {job['job']['description'][:150]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main())
