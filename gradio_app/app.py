import gradio as gr
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
    files = {"resume": resume_file}
    data = {"job_url": job_url}
    
    response = requests.post(
        f"{API_URL}/resume/score",
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return (
            f"Score: {result['score']:.2f}/100\n\n"
            f"Feedback:\n{json.dumps(result['feedback'], indent=2)}"
        )
    else:
        return f"Error scoring resume: {response.json()['detail']}"

def compare_multiple_jobs(resume_file, job_urls: str):
    """Compare resume against multiple job descriptions."""
    urls = [url.strip() for url in job_urls.split("\n") if url.strip()]
    files = {"resume": resume_file}
    data = {"job_urls": urls}
    
    response = requests.post(
        f"{API_URL}/resume/compare",
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        results = response.json()
        output = "Comparison Results:\n\n"
        for result in results:
            output += (
                f"Job: {result['job_title']} at {result['company']}\n"
                f"Score: {result['score']:.2f}/100\n"
                f"Feedback:\n{json.dumps(result['feedback'], indent=2)}\n"
                f"---\n"
            )
        return output
    else:
        return f"Error comparing jobs: {response.json()['detail']}"

# Gradio Interface
with gr.Blocks(title="ResumeRoast") as demo:
    gr.Markdown("# ResumeRoast")
    gr.Markdown("Score your resume against job descriptions")
    
    with gr.Tab("Resume Scoring"):
        gr.Markdown("### Score your resume against a job description")
        resume_file = gr.File(label="Upload your resume (PDF or DOCX)")
        job_url = gr.Textbox(label="Enter LinkedIn job URL")
        score_button = gr.Button("Score Resume")
        score_output = gr.Textbox(label="Results", lines=10)
    
    with gr.Tab("Multiple Job Comparison"):
        gr.Markdown("### Compare your resume with multiple jobs")
        compare_resume_file = gr.File(label="Upload your resume (PDF or DOCX)")
        job_urls = gr.Textbox(label="Enter multiple LinkedIn job URLs (one per line)", lines=5)
        compare_button = gr.Button("Compare with Multiple Jobs")
        compare_output = gr.Textbox(label="Comparison Results", lines=15)
    
    # Event handlers
    score_button.click(
        score_resume,
        inputs=[resume_file, job_url],
        outputs=[score_output]
    )
    
    compare_button.click(
        compare_multiple_jobs,
        inputs=[compare_resume_file, job_urls],
        outputs=[compare_output]
    )

if __name__ == "__main__":
    demo.launch()