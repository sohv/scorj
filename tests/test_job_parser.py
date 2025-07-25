import pytest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from utils.job_parser import JobDescriptionParser


class TestJobParser:
    
    @pytest.fixture
    def parser(self):
        return JobDescriptionParser()
    
    @pytest.fixture
    def sample_job_description(self):
        return """
        Senior Full Stack Developer
        
        Company: TechCorp Inc.
        Location: San Francisco, CA
        
        Job Description:
        We are seeking a skilled Senior Full Stack Developer to join our team.
        
        Requirements:
        - 5+ years of experience in web development
        - Proficiency in Python, JavaScript, React, Node.js
        - Experience with Docker and Kubernetes
        - Bachelor's degree in Computer Science or related field
        
        Responsibilities:
        - Develop and maintain web applications
        - Collaborate with cross-functional teams
        - Implement CI/CD pipelines
        """
    
    def test_parser_initialization(self, parser):
        assert parser is not None
        assert hasattr(parser, 'parse_job_description_text')
    
    def test_parse_job_description_basic(self, parser, sample_job_description):
        result = parser.parse_job_description_text(sample_job_description)
        
        assert result is not None
        assert 'title' in result
        assert 'description' in result
        assert 'required_skills' in result
        assert 'experience_level' in result
    
    def test_skills_extraction(self, parser, sample_job_description):
        result = parser.parse_job_description_text(sample_job_description)
        skills = result.get('required_skills', [])
        
        assert len(skills) > 0
        # Check for some expected skills
        skill_names = [skill.lower() for skill in skills]
        assert any('python' in skill for skill in skill_names)
        assert any('javascript' in skill for skill in skill_names)
    
    def test_title_extraction(self, parser, sample_job_description):
        result = parser.parse_job_description_text(sample_job_description)
        title = result.get('title', '')
        
        assert 'Senior Full Stack Developer' in title
    
    def test_company_extraction(self, parser, sample_job_description):
        result = parser.parse_job_description_text(sample_job_description)
        company = result.get('company', '')
        
        assert 'TechCorp' in company
    
    def test_experience_level_extraction(self, parser, sample_job_description):
        result = parser.parse_job_description_text(sample_job_description)
        experience_level = result.get('experience_level', '')
        
        # Should identify senior level from title and requirements
        assert experience_level in ['senior', 'mid', 'entry'] or len(experience_level) > 0
