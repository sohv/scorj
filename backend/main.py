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
from utils.scoring_engine_openai import ScoringEngine as OpenAIScoringEngine
from utils.scoring_engine_gemini import GeminiScoringEngine
from utils.scoring_engine_dual import DualScoringEngine

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

# Initialize parsers and scoring engines
resume_parser = ResumeParser()
job_parser = JobDescriptionParser()
openai_engine = OpenAIScoringEngine()
gemini_engine = GeminiScoringEngine()
dual_engine = DualScoringEngine()

# Default to dual engine for comprehensive analysis
scoring_engine = dual_engine

@app.post("/resume/score")
async def score_resume(
    resume: UploadFile = File(...),
    job_url: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    model: Optional[str] = Form("dual")  # dual, openai, gemini
):
    """Score a resume against a job description using specified model."""
    
    # Validate model choice
    valid_models = ["dual", "openai", "gemini"]
    if model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model choice. Must be one of: {valid_models}")
    
    # Select scoring engine based on model choice
    if model == "openai":
        selected_engine = openai_engine
    elif model == "gemini":
        selected_engine = gemini_engine
    else:  # dual
        selected_engine = dual_engine
    
    # Validate that either job_url or job_description is provided
    if not job_url and not job_description:
        raise HTTPException(status_code=400, detail="Either job URL or job description is required")
    
    if job_url and job_description:
        raise HTTPException(status_code=400, detail="Please provide either job URL or job description, not both")
    
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
        if job_url:
            job_data = job_parser.parse_linkedin_job(job_url.strip())
            
            # Validate job parsing
            if not job_data:
                raise HTTPException(status_code=400, detail="Could not parse job description from URL")
        else:
            # Handle pasted job description
            job_data = job_parser.parse_job_description_text(job_description.strip())
            
            # Validate job parsing
            if not job_data:
                raise HTTPException(status_code=400, detail="Could not parse job description text")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing job description: {str(e)}")
    
    # Calculate score
    try:
        result = selected_engine.calculate_score(resume_data, job_data)
        score = result.get('final_score', result.get('overall_score', 0))
        feedback = result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating score: {str(e)}")
    
    return {
        "score": score,
        "feedback": feedback,
        "job_title": job_data.get("title", "Unknown"),
        "company": job_data.get("company", "Unknown"),
        "model_used": model
    }

@app.post("/resume/compare")
async def compare_multiple_jobs(
    resume: UploadFile = File(...),
    job_urls: str = Form(...),
    model: Optional[str] = Form("dual")  # dual, openai, gemini
):
    """Compare a resume against multiple job descriptions using specified model."""
    
    # Validate model choice
    valid_models = ["dual", "openai", "gemini"]
    if model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model choice. Must be one of: {valid_models}")
    
    # Select scoring engine based on model choice
    if model == "openai":
        selected_engine = openai_engine
    elif model == "gemini":
        selected_engine = gemini_engine
    else:  # dual
        selected_engine = dual_engine
    
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
                
            result = selected_engine.calculate_score(resume_data, job_data)
            score = result.get('final_score', result.get('overall_score', 0))
            feedback = result
            results.append({
                "job_url": job_url,
                "job_title": job_data.get("title", "Unknown"),
                "company": job_data.get("company", "Unknown"),
                "score": score,
                "feedback": feedback,
                "model_used": model
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

# Model information endpoint
@app.get("/models")
async def get_available_models():
    """Get information about available scoring models."""
    return {
        "available_models": [
            {
                "name": "dual",
                "description": "Comprehensive analysis using both OpenAI and Gemini for best accuracy",
                "features": ["OpenAI GPT-4o-mini", "Google Gemini 1.5-pro", "Consensus scoring", "Transparency metrics"],
                "recommended": True
            },
            {
                "name": "openai",
                "description": "Fast and reliable analysis using OpenAI GPT-4o-mini",
                "features": ["OpenAI GPT-4o-mini", "Structured analysis", "Quick processing"],
                "recommended": False
            },
            {
                "name": "gemini",
                "description": "Advanced analysis using Google Gemini 1.5-pro",
                "features": ["Google Gemini 1.5-pro", "Detailed insights", "Creative feedback"],
                "recommended": False
            }
        ],
        "default_model": "dual"
    }

# Alternative endpoint for debugging
@app.get("/test")
async def test_endpoint():
    return {"message": "backend is working correctly"}