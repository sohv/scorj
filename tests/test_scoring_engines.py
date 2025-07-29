import pytest
from unittest.mock import patch, MagicMock
from utils.base_scoring_engine import BaseScoringEngine
from utils.scoring_engine_openai import ScoringEngine

@pytest.fixture
def base_engine():
    return BaseScoringEngine()

@pytest.fixture
def openai_engine():
    return ScoringEngine()

class TestBaseScoringEngine:
    def test_base_engine_initialization(self, base_engine):
        assert base_engine is not None
        # Test that dynamic components are initialized
        assert hasattr(base_engine, 'embedding_matcher')
        assert hasattr(base_engine, 'weight_calculator')

    def test_score_ranges_configuration(self, base_engine):
        assert isinstance(base_engine.score_ranges, dict)
        assert (70, 100) in base_engine.score_ranges

    def test_degree_scoring(self, base_engine):
        assert base_engine._get_degree_score('phd') == 100
        assert base_engine._get_degree_score('master of science') == 80
        assert base_engine._get_degree_score('bachelor of arts') == 60
        assert base_engine._get_degree_score('associate') == 40
        # A diploma should be better than nothing
        assert base_engine._get_degree_score('high school diploma') > 0

    def test_experience_calculation(self, base_engine):
        experience = [
            {'date': '2020-present'},
            {'date': '2018-2020'}
        ]
        # This will vary based on the current year, so we check it's positive
        assert base_engine._calculate_experience_years(experience) > 3

class TestOpenAIScoringEngine:
    def test_openai_engine_initialization(self, openai_engine):
        assert openai_engine is not None
        assert hasattr(openai_engine, 'openai_client')

    @patch('utils.scoring_engine_openai.ScoringEngine._analyze_structured_data')
    def test_calculate_score_integration(self, mock_analyze, openai_engine):
        mock_analyze.return_value = {}
        # This test now only checks if the method runs without error with a mock
        # A full integration test would require mocking the OpenAI API call itself
        with patch('utils.scoring_engine_openai.ScoringEngine._create_enhanced_prompt') as mock_prompt:
            mock_prompt.return_value = "Test Prompt"
            try:
                openai_engine.calculate_score({}, {})
            except Exception as e:
                pytest.fail(f"calculate_score raised an exception: {e}")

    def test_structured_analysis(self, openai_engine):
        resume_data = {
            'skills': ['Python', 'SQL'],
            'experience': [{'date': '2020-2022'}],
            'education': [{'degree': 'BS in Computer Science'}]
        }
        job_data = {
            'skills': ['Python', 'Java'],
            'experience_level': 'mid'
        }
        analysis = openai_engine._analyze_structured_data(resume_data, job_data)
        assert 'skills_analysis' in analysis
        assert 'experience_analysis' in analysis
        assert 'education_analysis' in analysis
        assert analysis['skills_analysis']['match_percentage'] > 0

    @patch('utils.scoring_engine_openai.OpenAI')
    def test_calculate_score_mocked(self, mock_openai, openai_engine):
        # A more robust test mocking the entire OpenAI interaction
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"overall_score": 85}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        openai_engine.openai_client = mock_client

        resume_data = {
            'skills': ['Python'], 'experience': [], 'education': [], 'user_comments': ''
        }
        job_data = {
            'skills': ['Python'], 'description': 'A job'
        }

        result = openai_engine.calculate_score(resume_data, job_data)
        assert result['final_score'] == 85