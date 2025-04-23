import streamlit as st
import requests
import json
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

def score_resume(resume_file, job_url: str):
    """Score resume against job description."""
    try:
        files = {"resume": resume_file}
        data = {"job_url": job_url}
        
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

def compare_multiple_jobs(resume_file, job_urls: List[str]):
    """Compare resume against multiple job descriptions."""
    files = {"resume": resume_file}
    data = {"job_urls": job_urls}
    
    response = requests.post(
        f"{API_URL}/resume/compare",
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error comparing jobs: {response.json()['detail']}")
        return None

# Streamlit UI
st.title("ResumeRoast")
st.subheader("Score your resume against job descriptions")

# Resume upload
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

# Job URL input
job_url = st.text_input("Enter LinkedIn job URL")

# Compare multiple jobs
st.write("---")
st.subheader("Compare with multiple jobs")
job_urls = st.text_area("Enter multiple LinkedIn job URLs (one per line)")

if st.button("Score Resume"):
    if resume_file and job_url:
        with st.spinner("Analyzing resume..."):
            result = score_resume(resume_file, job_url)
            if result:
                st.write("---")
                st.subheader("Results")
                st.write(f"Score: {result['score']:.2f}/100")
                st.write("Feedback:")
                st.json(result['feedback'])

if st.button("Compare with Multiple Jobs"):
    if resume_file and job_urls:
        with st.spinner("Comparing with multiple jobs..."):
            urls = [url.strip() for url in job_urls.split("\n") if url.strip()]
            results = compare_multiple_jobs(resume_file, urls)
            if results:
                st.write("---")
                st.subheader("Comparison Results")
                for result in results:
                    st.write(f"Job: {result['job_title']} at {result['company']}")
                    st.write(f"Score: {result['score']:.2f}/100")
                    st.write("Feedback:")
                    st.json(result['feedback'])
                    st.write("---") 