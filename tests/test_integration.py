"""
Integration tests for the complete resume scoring workflow.
"""
import pytest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser
from utils.scoring_engine_openai import ScoringEngine as OpenAIScoringEngine


class TestIntegrationWorkflow:
    
    @pytest.fixture
    def resume_parser(self):
        return ResumeParser()
    
    @pytest.fixture
    def job_parser(self):
        return JobDescriptionParser()
    
    @pytest.fixture
    def scoring_engine(self):
        return OpenAIScoringEngine()
    
    @pytest.fixture
    def sample_resume_text(self):
        return """
        Jane Smith
        Senior Python Developer
        jane.smith@email.com | (555) 123-4567
        
        PROFESSIONAL EXPERIENCE
        Senior Python Developer | TechCorp Inc. | 2020 - Present
        • Developed microservices using Python and FastAPI
        • Implemented CI/CD pipelines with Docker and Jenkins
        • Led a team of 4 junior developers
        • Built RESTful APIs serving 1M+ requests daily
        
        Python Developer | StartupCo | 2018 - 2020
        • Created web applications using Django and React
        • Optimized database queries reducing response time by 40%
        • Implemented automated testing with pytest
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript, SQL
        Frameworks: Django, FastAPI, React, Node.js
        Tools: Docker, Jenkins, Git, PostgreSQL, Redis
        Cloud: AWS, Azure
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of California, Berkeley | 2014 - 2018
        GPA: 3.8/4.0
        """
    
    @pytest.fixture
    def sample_job_description(self):
        return """
        Senior Backend Developer
        
        Company: InnovateNext
        Location: Remote
        Salary: $120,000 - $150,000
        
        We are looking for a Senior Backend Developer to join our growing team.
        
        Requirements:
        • 5+ years of Python development experience
        • Strong experience with FastAPI or Django
        • Experience with microservices architecture
        • Proficiency in Docker and containerization
        • Experience with cloud platforms (AWS preferred)
        • Bachelor's degree in Computer Science or related field
        
        Responsibilities:
        • Design and develop scalable backend systems
        • Build and maintain RESTful APIs
        • Collaborate with frontend and DevOps teams
        • Implement automated testing and CI/CD
        • Mentor junior developers
        
        Nice to have:
        • Experience with Kubernetes
        • Knowledge of machine learning
        • Leadership experience
        """
    
    def test_complete_workflow_without_api(self, resume_parser, job_parser, sample_resume_text, sample_job_description):
        # Parse resume
        resume_data = resume_parser._structure_text(sample_resume_text)
        assert resume_data is not None
        assert 'skills' in resume_data
        assert 'experience' in resume_data
        assert 'education' in resume_data
        
        # Parse job description
        job_data = job_parser.parse_job_description_text(sample_job_description)
        assert job_data is not None
        assert 'required_skills' in job_data
        assert 'title' in job_data
        
        # Verify data quality
        assert len(resume_data['skills']) > 0
        assert len(resume_data['experience']) > 0
        assert len(job_data['required_skills']) > 0
        
        # Check for skill matching potential (handle both string and object formats)
        if resume_data['skills'] and isinstance(resume_data['skills'][0], str):
            resume_skills = [skill.lower() for skill in resume_data['skills']]
        else:
            resume_skills = [skill.get('skill', '').lower() for skill in resume_data['skills']]
        job_skills = [skill.lower() for skill in job_data['required_skills']]
        
        common_skills = set(resume_skills) & set(job_skills)
        assert len(common_skills) > 0, "Should find some matching skills"
    
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not available")
    def test_complete_workflow_with_scoring(self, resume_parser, job_parser, scoring_engine, 
                                          sample_resume_text, sample_job_description):
        # Parse resume
        resume_data = resume_parser._structure_text(sample_resume_text)
        
        # Parse job description
        job_data = job_parser.parse_job_description_text(sample_job_description)
        
        # Calculate score
        result = scoring_engine.calculate_score(resume_data, job_data)
        
        assert result is not None
        assert 'overall_score' in result
        assert 'confidence_level' in result
        assert 'score_breakdown' in result
        assert 'strengths' in result
        assert 'recommendations' in result
        
        # Validate score range
        score = result['overall_score']
        assert 0 <= score <= 100
        
        # This should be a good match given the sample data
        assert score >= 60, f"Expected good match score, got {score}"
        
        # Check confidence level
        assert result['confidence_level'] in ['High', 'Medium', 'Low']
        
        # Validate score breakdown
        breakdown = result['score_breakdown']
        for category in ['skills_score', 'experience_score', 'education_score', 'domain_score']:
            assert category in breakdown
            assert 0 <= breakdown[category] <= 100
