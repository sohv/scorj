from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from datetime import datetime
import sys
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser
from utils.scoring_engine_openai import ScoringEngine

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
    job_url: str = Form(...)
):
    """Score a resume against a job description."""
    
    # Validate job URL
    if not job_url or not job_url.strip():
        raise HTTPException(status_code=400, detail="Job URL is required")
    
    # Validate file
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file format
    if not (resume.filename.endswith('.pdf') or resume.filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX files only.")
    
    try:
        # Read file content
        file_content = await resume.read()
        file_stream = io.BytesIO(file_content)
        
        # Parse resume based on file type
        if resume.filename.endswith('.pdf'):
            resume_data = resume_parser.parse_pdf(file_stream)
        elif resume.filename.endswith('.docx'):
            resume_data = resume_parser.parse_docx(file_stream)
        
        # Validate resume parsing
        if not resume_data:
            raise HTTPException(status_code=400, detail="Could not parse resume content")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")
    
    # Parse job description
    try:
        job_data = job_parser.parse_linkedin_job(job_url.strip())
        
        # Validate job parsing
        if not job_data:
            raise HTTPException(status_code=400, detail="Could not parse job description from URL")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing job URL: {str(e)}")
    
    # Calculate score
    try:
        score, feedback = scoring_engine.calculate_score(resume_data, job_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating score: {str(e)}")
    
    return {
        "score": score,
        "feedback": feedback,
        "job_title": job_data.get("title", "Unknown"),
        "company": job_data.get("company", "Unknown")
    }

@app.post("/resume/compare")
async def compare_multiple_jobs(
    resume: UploadFile = File(...),
    job_urls: str = Form(...)
):
    """Compare a resume against multiple job descriptions."""
    
    # Parse job URLs from form data (assuming they're newline-separated)
    if not job_urls or not job_urls.strip():
        raise HTTPException(status_code=400, detail="At least one job URL is required")
    
    # Split URLs and clean them
    urls_list = [url.strip() for url in job_urls.split('\n') if url.strip()]
    
    if not urls_list:
        raise HTTPException(status_code=400, detail="No valid job URLs provided")
    
    # Validate file
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file format
    if not (resume.filename.endswith('.pdf') or resume.filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX files only.")
    
    try:
        # Read file content
        file_content = await resume.read()
        file_stream = io.BytesIO(file_content)
        
        # Parse resume based on file type
        if resume.filename.endswith('.pdf'):
            resume_data = resume_parser.parse_pdf(file_stream)
        elif resume.filename.endswith('.docx'):
            resume_data = resume_parser.parse_docx(file_stream)
        
        # Validate resume parsing
        if not resume_data:
            raise HTTPException(status_code=400, detail="Could not parse resume content")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")
    
    # Parse and score each job
    results = []
    for job_url in urls_list:
        try:
            job_data = job_parser.parse_linkedin_job(job_url)
            
            if not job_data:
                results.append({
                    "job_url": job_url,
                    "error": "Could not parse job description from URL"
                })
                continue
                
            score, feedback = scoring_engine.calculate_score(resume_data, job_data)
            results.append({
                "job_url": job_url,
                "job_title": job_data.get("title", "Unknown"),
                "company": job_data.get("company", "Unknown"),
                "score": score,
                "feedback": feedback
            })
        except Exception as e:
            results.append({
                "job_url": job_url,
                "error": str(e)
            })
    
    return results

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "ResumeRoast API is running"}

# Alternative endpoint for debugging
@app.get("/test")
async def test_endpoint():
    return {"message": "Backend is working correctly"}