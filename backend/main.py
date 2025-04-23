from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser
from utils.scoring_engine import ScoringEngine

# Initialize FastAPI app
app = FastAPI(title="ResumeRoast API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers and scoring engine
resume_parser = ResumeParser()
job_parser = JobDescriptionParser()
scoring_engine = ScoringEngine()

@app.post("/resume/score")
async def score_resume(
    resume: UploadFile = File(...),
    job_url: str = None
):
    """Score a resume against a job description."""
    # Parse resume
    if resume.filename.endswith('.pdf'):
        resume_data = resume_parser.parse_pdf(resume.file)
    elif resume.filename.endswith('.docx'):
        resume_data = resume_parser.parse_docx(resume.file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Parse job description
    if not job_url:
        raise HTTPException(status_code=400, detail="Job URL is required")
    
    try:
        job_data = job_parser.parse_linkedin_job(job_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calculate score
    score, feedback = scoring_engine.calculate_score(resume_data, job_data)

    return {
        "score": score,
        "feedback": feedback,
        "job_title": job_data["title"],
        "company": job_data["company"]
    }

@app.post("/resume/compare")
async def compare_multiple_jobs(
    resume: UploadFile = File(...),
    job_urls: List[str] = None
):
    """Compare a resume against multiple job descriptions."""
    if not job_urls:
        raise HTTPException(status_code=400, detail="At least one job URL is required")

    # Parse resume
    if resume.filename.endswith('.pdf'):
        resume_data = resume_parser.parse_pdf(resume.file)
    elif resume.filename.endswith('.docx'):
        resume_data = resume_parser.parse_docx(resume.file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Parse and score each job
    results = []
    for job_url in job_urls:
        try:
            job_data = job_parser.parse_linkedin_job(job_url)
            score, feedback = scoring_engine.calculate_score(resume_data, job_data)
            results.append({
                "job_url": job_url,
                "job_title": job_data["title"],
                "company": job_data["company"],
                "score": score,
                "feedback": feedback
            })
        except Exception as e:
            results.append({
                "job_url": job_url,
                "error": str(e)
            })

    return results