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
    st.error("⚠️ Cannot connect to backend server. Please make sure it's running on " + API_URL)
    st.info("To start the backend server, run: `uvicorn main:app --reload`")
else:
    st.success("✅ Connected to backend server")

# Resume upload
st.write("### Upload Resume")
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if resume_file:
    st.success(f"✅ Resume uploaded: {resume_file.name}")

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
            st.subheader("📊 Results")
            
            # Display score with color coding
            score = result.get('score', 0)
            if score >= 80:
                st.success(f"🎉 Excellent Match: {score:.1f}/100")
            elif score >= 60:
                st.warning(f"👍 Good Match: {score:.1f}/100")
            else:
                st.error(f"💡 Needs Improvement: {score:.1f}/100")
            
            # Display job info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Job Title", result.get('job_title', 'N/A'))
            with col2:
                st.metric("Company", result.get('company', 'N/A'))
            
            # Display feedback
            st.write("### 💬 Detailed Feedback")
            feedback = result.get('feedback', {})
            if isinstance(feedback, dict):
                for key, value in feedback.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.write(feedback)

# Footer
st.write("---")
st.caption("💡 Tip: Make sure your LinkedIn job URLs are publicly accessible and in the format: https://www.linkedin.com/jobs/view/[job_id]")