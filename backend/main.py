from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from datetime import datetime
import sys
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser
from utils.scoring_engine_openai import ScoringEngine as OpenAIScoringEngine

# Initialize FastAPI app
app = FastAPI(title="Scorj API")

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
scoring_engine = OpenAIScoringEngine()

# Preload embedding model at startup to avoid loading delays
from utils.embedding_matcher import EmbeddingSkillsMatcher
EmbeddingSkillsMatcher.preload_model()

@app.post("/resume/score")
async def score_resume(
    resume: UploadFile = File(...),
    job_url: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    user_comments: Optional[str] = Form(None)  # User comments for context
):
    
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
    
    file_content = await resume.read()
    file_stream = io.BytesIO(file_content)
    
    if resume.filename.endswith('.pdf'):
        resume_data = resume_parser.parse_pdf(file_stream)
    elif resume.filename.endswith('.docx'):
        resume_data = resume_parser.parse_docx(file_stream)
    
    if not resume_data:
        raise HTTPException(status_code=400, detail="Could not parse resume content")
    
    if user_comments and user_comments.strip():
        resume_data['user_comments'] = user_comments.strip()
        resume_data['full_text'] = resume_data.get('full_text', '') + f"\n\nAdditional Context from User:\n{user_comments.strip()}"
    
    # Parse job description
    if job_url:
        job_data = job_parser.parse_linkedin_job(job_url.strip())
        
        if not job_data:
            raise HTTPException(status_code=400, detail="Could not parse job description from URL")
    else:
        job_data = job_parser.parse_job_description_text(job_description.strip())
        
        if not job_data:
            raise HTTPException(status_code=400, detail="Could not parse job description text")
    
    # Calculate score
    result = scoring_engine.calculate_score(resume_data, job_data)
    score = result.get('final_score', result.get('overall_score', 0))
    feedback = result
    
    return {
        "score": score,
        "feedback": feedback,
        "job_title": job_data.get("title", "Unknown"),
        "company": job_data.get("company", "Unknown"),
        "model_used": "openai"
    }

@app.post("/resume/compare")
async def compare_multiple_jobs(
    resume: UploadFile = File(...),
    job_urls: str = Form(...),
    user_comments: Optional[str] = Form(None)  # User comments for context
):
    
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
    
    file_content = await resume.read()
    file_stream = io.BytesIO(file_content)
    
    if resume.filename.endswith('.pdf'):
        resume_data = resume_parser.parse_pdf(file_stream)
    elif resume.filename.endswith('.docx'):
        resume_data = resume_parser.parse_docx(file_stream)
    
    if not resume_data:
        raise HTTPException(status_code=400, detail="Could not parse resume content")
    
    if user_comments and user_comments.strip():
        resume_data['user_comments'] = user_comments.strip()
        resume_data['full_text'] = resume_data.get('full_text', '') + f"\n\nAdditional Context from User:\n{user_comments.strip()}"
    
    # Parse and score each job
    results = []
    for job_url in urls_list:
        job_data = job_parser.parse_linkedin_job(job_url)
        
        if not job_data:
            results.append({
                "job_url": job_url,
                "error": "Could not parse job description from URL"
            })
            continue
            
        result = scoring_engine.calculate_score(resume_data, job_data)
        score = result.get('final_score', result.get('overall_score', 0))
        feedback = result
        results.append({
            "job_url": job_url,
            "job_title": job_data.get("title", "Unknown"),
            "company": job_data.get("company", "Unknown"),
            "score": score,
            "feedback": feedback,
            "model_used": "openai"
        })
    
    return results

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "ResumeRoast API is running"}

# Model information endpoint
@app.get("/models")
async def get_available_models():
    return {
        "available_models": [
            {
                "name": "openai",
                "description": "Fast and reliable analysis using OpenAI GPT-4o-mini",
                "features": ["OpenAI GPT-4o-mini", "Structured analysis", "Quick processing"],
                "recommended": True
            }
        ],
        "default_model": "openai"
    }

# AI Chat endpoint for scoring insights
@app.post("/ai/chat")
async def chat_with_ai(
    question: str = Form(...),
    context: Optional[str] = Form(None)  # Optional context about recent scoring
):
    
    import openai
    
    messages = [
        {
            "role": "system", 
            "content": "You are a senior technical recruiter AI assistant. Help users understand resume scoring decisions, provide career advice, and explain recruitment insights. Be concise, helpful, and professional."
        },
        {
            "role": "user",
            "content": f"Context: {context}\n\nQuestion: {question}" if context else question
        }
    ]
    
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
        seed=42
    )
    
    return {
        "response": response.choices[0].message.content,
        "model_used": "openai",
        "success": True
    }

# Alternative endpoint for debugging
@app.get("/test")
async def test_endpoint():
    return {"message": "backend is working correctly"}
