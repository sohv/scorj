import pytest
import os
import sys
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from utils.scoring_engine_openai import ScoringEngine as OpenAIScoringEngine
from utils.base_scoring_engine import BaseScoringEngine


class TestBaseScoringEngine:
    
    @pytest.fixture
    def base_engine(self):
        return BaseScoringEngine()
    
    def test_base_engine_initialization(self, base_engine):
        assert base_engine is not None
        assert hasattr(base_engine, 'weights')
        assert hasattr(base_engine, 'score_ranges')
    
    def test_weights_configuration(self, base_engine):
        weights = base_engine.weights
        
        assert 'skills_match' in weights
        assert 'experience_match' in weights
        assert 'education_match' in weights
        assert 'domain_expertise' in weights
        
        # Weights should sum to 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_score_ranges_configuration(self, base_engine):
        score_ranges = base_engine.score_ranges
        
        assert len(score_ranges) > 0
        # Check that ranges cover the full 0-100 spectrum
        all_ranges = list(score_ranges.keys())
        min_score = min(range_tuple[0] for range_tuple in all_ranges)
        max_score = max(range_tuple[1] for range_tuple in all_ranges)
        
        assert min_score <= 0
        assert max_score >= 100
    
    def test_degree_scoring(self, base_engine):
        # Test different degree levels
        phd_score = base_engine._get_degree_score("PhD in Computer Science")
        masters_score = base_engine._get_degree_score("Master of Science")
        bachelors_score = base_engine._get_degree_score("Bachelor of Engineering")
        
        assert phd_score > masters_score > bachelors_score
        assert phd_score == 100
        assert masters_score == 80
        assert bachelors_score == 60
    
    def test_experience_calculation(self, base_engine):
        sample_experience = [
            {"date": "2020-2023", "position": "Senior Developer"},
            {"date": "2018-2020", "position": "Developer"}
        ]
        
        years = base_engine._calculate_experience_years(sample_experience)
        assert years > 0
        assert years <= 10  # Should be reasonable


class TestOpenAIScoringEngine:
    
    @pytest.fixture
    def openai_engine(self):
        return OpenAIScoringEngine()
    
    @pytest.fixture
    def sample_resume_data(self):
        return {
            'full_text': 'John Doe, Senior Developer with 5 years experience...',
            'skills': [
                {'skill': 'Python', 'category': 'Programming'},
                {'skill': 'React', 'category': 'Frontend'}
            ],
            'experience': [
                {'position': 'Senior Developer', 'company': 'TechCorp', 'date': '2020-2023'}
            ],
            'education': [
                {'degree': 'Bachelor of Science', 'institution': 'University'}
            ]
        }
    
    @pytest.fixture
    def sample_job_data(self):
        return {
            'title': 'Senior Full Stack Developer',
            'description': 'Looking for experienced developer...',
            'required_skills': ['Python', 'React', 'Node.js'],
            'experience_level': 'senior'
        }
    
    def test_openai_engine_initialization(self, openai_engine):
        assert openai_engine is not None
        assert isinstance(openai_engine, BaseScoringEngine)
        assert hasattr(openai_engine, 'calculate_score')
    
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not available")
    def test_calculate_score_integration(self, openai_engine, sample_resume_data, sample_job_data):
        result = openai_engine.calculate_score(sample_resume_data, sample_job_data)
        
        assert result is not None
        assert 'overall_score' in result
        assert 'confidence_level' in result
        assert 'score_breakdown' in result
        
        # Score should be between 0 and 100
        score = result['overall_score']
        assert 0 <= score <= 100
    
    def test_structured_analysis(self, openai_engine, sample_resume_data, sample_job_data):
        structured_analysis = openai_engine._analyze_structured_data(
            sample_resume_data, sample_job_data
        )
        
        assert structured_analysis is not None
        assert 'skills_analysis' in structured_analysis
        assert 'experience_analysis' in structured_analysis
        assert 'education_analysis' in structured_analysis
    
    def test_calculate_score_mocked(self, openai_engine, sample_resume_data, sample_job_data):
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "overall_score": 85,
            "confidence_level": "High",
            "score_breakdown": {"skills_score": 80, "experience_score": 90, "education_score": 75, "domain_score": 85},
            "match_category": "Excellent Match",
            "summary": "Strong candidate",
            "strengths": ["Python experience", "React skills"],
            "concerns": ["Limited Node.js experience"],
            "missing_skills": ["Node.js"],
            "matching_skills": ["Python", "React"],
            "experience_assessment": {"relevant_years": 5, "role_progression": "Good", "industry_fit": "Excellent"},
            "recommendations": ["Learn Node.js"],
            "risk_factors": ["Technology gap"]
        }
        '''
    
        # Mock the client directly on the instance
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        openai_engine.openai_client = mock_client
    
        result = openai_engine.calculate_score(sample_resume_data, sample_job_data)
    
        assert result is not None
        assert result['overall_score'] == 85
        assert result['confidence_level'] == 'High'
