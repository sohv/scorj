"""
Unit tests for resume parsing functionality.
"""
import pytest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from utils.resume_parser import ResumeParser


class TestResumeParser:
    """Test cases for ResumeParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a ResumeParser instance for testing."""
        return ResumeParser()
    
    @pytest.fixture
    def sample_resume_text(self):
        """Sample resume text for testing."""
        return """
        John Doe
        Senior Software Engineer
        john.doe@email.com
        
        EXPERIENCE
        Senior Software Developer at Tech Corp (2020-2023)
        - Developed web applications using React and Node.js
        - Implemented CI/CD pipelines with Docker and Jenkins
        - Led a team of 5 developers
        
        SKILLS
        Python, JavaScript, React, Node.js, Docker, Jenkins
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology (2016-2020)
        """
    
    def test_parser_initialization(self, parser):
        """Test that parser initializes correctly."""
        assert parser is not None
        assert hasattr(parser, 'parse_pdf')
        assert hasattr(parser, 'parse_docx')
        assert hasattr(parser, '_structure_text')
    
    def test_structure_text_basic(self, parser, sample_resume_text):
        """Test basic text structuring functionality."""
        result = parser._structure_text(sample_resume_text)
        
        assert result is not None
        assert 'full_text' in result
        assert 'contact_info' in result
        assert 'skills' in result
        assert 'experience' in result
        assert 'education' in result
    
    def test_skills_extraction(self, parser, sample_resume_text):
        """Test that skills are extracted correctly."""
        result = parser._structure_text(sample_resume_text)
        skills = result.get('skills', [])
        
        assert len(skills) > 0
        # Check for some expected skills
        skill_names = [skill.get('skill', '').lower() for skill in skills]
        assert any('python' in skill for skill in skill_names)
    
    def test_experience_extraction(self, parser, sample_resume_text):
        """Test that experience is extracted correctly."""
        result = parser._structure_text(sample_resume_text)
        experience = result.get('experience', [])
        
        assert len(experience) > 0
        # Check for expected experience fields
        exp = experience[0]
        assert 'position' in exp
        assert 'company' in exp
        assert 'date' in exp
    
    def test_education_extraction(self, parser, sample_resume_text):
        """Test that education is extracted correctly."""
        result = parser._structure_text(sample_resume_text)
        education = result.get('education', [])
        
        assert len(education) > 0
        # Check for expected education fields
        edu = education[0]
        assert 'degree' in edu
        assert 'institution' in edu
    
    def test_contact_info_extraction(self, parser, sample_resume_text):
        """Test that contact info is extracted correctly."""
        result = parser._structure_text(sample_resume_text)
        contact_info = result.get('contact_info', {})
        
        assert 'email' in contact_info
        assert contact_info['email'] == 'john.doe@email.com'
