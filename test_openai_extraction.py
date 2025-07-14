"""simple test script to verify OpenAI-based extraction is working.
"""

import os
from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser

def test_resume_parsing():
    """Test resume parsing with OpenAI."""
    print("Testing Resume Parser with OpenAI...")
    
    sample_resume_text = """
    John Doe
    Software Engineer
    
    EXPERIENCE
    Senior Software Developer at Tech Corp (2020-2023)
    - Developed web applications using React and Node.js
    - Implemented CI/CD pipelines with Docker and Jenkins
    - Led a team of 5 developers
    
    SKILLS
    Python, JavaScript, React, Node.js, Docker, AWS, PostgreSQL
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology (2016-2020)
    """
    
    parser = ResumeParser()
    try:
        result = parser._structure_text(sample_resume_text)
        print("Resume parsing successful!")
        print(f"Skills found: {result.get('skills', [])}")
        print(f"Experience entries: {len(result.get('experience', []))}")
        return True
    except Exception as e:
        print(f"Resume parsing failed: {e}")
        return False

def test_job_parsing():
    """Test job description parsing with OpenAI."""
    print("\nTesting Job Parser with OpenAI...")
    
    sample_job_text = """
    Senior Full Stack Developer
    
    We are seeking a Senior Full Stack Developer with 5+ years of experience.
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 5+ years of experience in web development
    - Proficiency in React, Node.js, and Python
    - Experience with AWS cloud services
    - Knowledge of Docker and Kubernetes
    - Strong problem-solving skills
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    """
    
    parser = JobDescriptionParser()
    try:
        result = parser.parse_job_description_text(sample_job_text)
        print("Job parsing successful!")
        print(f"Skills found: {result.get('skills', [])}")
        print(f"Experience level: {result.get('experience_level', 'not specified')}")
        print(f"Requirements: {len(result.get('requirements', []))} items")
        return True
    except Exception as e:
        print(f"Job parsing failed: {e}")
        return False

def main():
    """Run tests."""
    print("OpenAI Extraction Test Suite")
    print("=" * 40)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY environment variable not set!")
        print("Please set it before running this test.")
        return
    
    resume_success = test_resume_parsing()
    job_success = test_job_parsing()
    
    print("\n" + "=" * 40)
    if resume_success and job_success:
        print("🎉 All tests passed! OpenAI extraction is working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
