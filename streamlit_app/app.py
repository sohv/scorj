import streamlit as st
import requests
import json
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

def score_resume(resume_file, job_url: str = None, job_description: str = None):
    """Score resume against a job description from a URL or text."""
    try:
        # Prepare files and data for the request
        files = {"resume": (resume_file.name, resume_file.getvalue(), resume_file.type)}
        data = {}
        if job_url:
            data["job_url"] = job_url.strip()
        if job_description:
            data["job_description"] = job_description.strip()
        
        response = requests.post(
            f"{API_URL}/resume/score",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text or 'Unknown error'
            st.error(f"Error scoring resume: {error_detail}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Please make sure the backend server is running.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def compare_multiple_jobs(resume_file, job_urls_text: str):
    """Compare resume against multiple job descriptions."""
    try:
        # Prepare files and data for the request
        files = {"resume": (resume_file.name, resume_file.getvalue(), resume_file.type)}
        data = {"job_urls": job_urls_text.strip()}
        
        response = requests.post(
            f"{API_URL}/resume/compare",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text or 'Unknown error'
            st.error(f"Error comparing jobs: {error_detail}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Please make sure the backend server is running.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def test_backend_connection():
    """Test if backend is accessible."""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

# Streamlit UI
st.title("ResumeRoast")
st.subheader("Score your resume against job descriptions")

# Test backend connection
if not test_backend_connection():
    st.error("Cannot connect to backend server. Please make sure it's running on " + API_URL)
    st.info("To start the backend server, run: `uvicorn main:app --reload`")
else:
    st.success("Connected to backend server")

# Resume upload
st.write("### Upload Resume")
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if resume_file:
    st.success(f"Resume uploaded: {resume_file.name}")

# Single job scoring
st.write("### Score Against Single Job")
job_input_method = st.radio("Choose input method:", ("LinkedIn URL", "Paste Job Description"))

job_url = None
job_description = None

if job_input_method == "LinkedIn URL":
    job_url = st.text_input("Enter LinkedIn job URL", placeholder="https://www.linkedin.com/jobs/view/...")
else:
    job_description = st.text_area("Paste the job description here:", height=200, placeholder="Paste the full job description...")

if st.button("Score Resume", disabled=not (resume_file and (job_url or job_description))):
    with st.spinner("Analyzing resume..."):
        result = score_resume(resume_file, job_url=job_url, job_description=job_description)
        if result:
            st.write("---")
            st.subheader("Dual AI Analysis Results")
            
            # Extract scores from dual model analysis
            feedback = result.get('feedback', {})
            final_score = feedback.get('final_score', result.get('score', 0))
            ai_comparison = feedback.get('ai_comparison', {})
            dual_model_results = feedback.get('dual_model_results', {})
            
            # Display final combined score with color coding
            if final_score >= 80:
                st.success(f"Excellent Match: {final_score}/100")
            elif final_score >= 60:
                st.warning(f"Good Match: {final_score}/100")
            else:
                st.error(f"Needs Improvement: {final_score}/100")
            
            # Display AI model comparison
            if ai_comparison:
                st.write("### AI Model Comparison")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    openai_score = ai_comparison.get('openai_score', 0)
                    st.metric("OpenAI Score", f"{openai_score}/100", 
                             delta=f"{openai_score - final_score:+}" if openai_score > 0 else None)
                
                with col2:
                    gemini_score = ai_comparison.get('gemini_score', 0)
                    st.metric("Gemini Score", f"{gemini_score}/100",
                             delta=f"{gemini_score - final_score:+}" if gemini_score > 0 else None)
                
                with col3:
                    consensus_level = ai_comparison.get('consensus_level', 'Unknown')
                    score_variance = ai_comparison.get('score_variance')
                    if score_variance is not None:
                        st.metric("Model Agreement", consensus_level, 
                                 delta=f"±{score_variance} pts" if score_variance > 0 else "Perfect match")
                    else:
                        st.metric("Model Agreement", consensus_level)
            
            # Display job info
            st.write("### Job Information")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Job Title", result.get('job_title', 'N/A'))
            with col2:
                st.metric("Company", result.get('company', 'N/A'))
            
            # Display transparency info
            transparency = feedback.get('transparency', {})
            if transparency:
                st.write("### � Analysis Transparency")
                
                col1, col2 = st.columns(2)
                with col1:
                    methodology = transparency.get('methodology', 'Unknown')
                    st.info(f"**Methodology:** {methodology}")
                    
                    processing_time = transparency.get('processing_time_seconds', 0)
                    st.info(f"**Processing Time:** {processing_time:.2f} seconds")
                
                with col2:
                    validation = transparency.get('validation', {})
                    both_models = validation.get('both_models_available', False)
                    st.info(f"**Both AI Models Available:** {'Yes' if both_models else 'No'}")
                    
                    fallback_used = validation.get('fallback_used', False)
                    st.info(f"**Fallback Used:** {'Yes' if fallback_used else 'No'}")
            
            # Display detailed feedback
            st.write("### Detailed Analysis")
            
            # Score breakdown
            score_breakdown = feedback.get('score_breakdown', {})
            if score_breakdown:
                st.write("**Score Breakdown:**")
                breakdown_cols = st.columns(4)
                breakdown_items = [
                    ("Skills", score_breakdown.get('skills_score', 0)),
                    ("Experience", score_breakdown.get('experience_score', 0)),
                    ("Education", score_breakdown.get('education_score', 0)),
                    ("Domain", score_breakdown.get('domain_score', 0))
                ]
                
                for i, (category, score) in enumerate(breakdown_items):
                    with breakdown_cols[i]:
                        st.metric(category, f"{score}/100")
            
            # Key insights
            col1, col2 = st.columns(2)
            
            with col1:
                strengths = feedback.get('strengths', [])
                if strengths:
                    st.write("**Key Strengths:**")
                    for strength in strengths[:5]:  # Show top 5
                        st.write(f"• {strength}")
                
                matching_skills = feedback.get('matching_skills', [])
                if matching_skills:
                    st.write("**Matching Skills:**")
                    for skill in matching_skills[:8]:  # Show top 8
                        st.write(f"• {skill}")
            
            with col2:
                concerns = feedback.get('concerns', [])
                if concerns:
                    st.write("**Areas of Concern:**")
                    for concern in concerns[:5]:  # Show top 5
                        st.write(f"• {concern}")
                
                missing_skills = feedback.get('missing_skills', [])
                if missing_skills:
                    st.write("**Missing Skills:**")
                    for skill in missing_skills[:8]:  # Show top 8
                        st.write(f"• {skill}")
            
            # Summary and recommendations
            summary = feedback.get('summary', '')
            if summary:
                st.write("**Executive Summary:**")
                st.write(summary)
            
            recommendations = feedback.get('recommendations', [])
            if recommendations:
                st.write("**Improvement Recommendations:**")
                for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                    st.write(f"{i}. {rec}")
            
            # Show raw data in expander for debugging
            with st.expander("Raw Analysis Data (for debugging)"):
                st.json(feedback)

# Footer
st.write("---")
st.caption("Tip: Make sure your LinkedIn job URLs are publicly accessible and in the format: https://www.linkedin.com/jobs/view/[job_id]")