import pytest
from unittest.mock import patch, MagicMock
from utils.structured_comments import (
    process_user_comments, 
    GPTIntentAnalyzer, 
    IntentAnalysis,
    calculate_intent_bonuses,
    generate_intent_feedback
)

def test_empty_comments():
    """Test handling of empty input"""
    result = process_user_comments("", {})
    
    assert result['total_bonus'] == 0
    assert 'No context provided' in result['structured_feedback']
    assert result['intent_analysis'] == {}

def test_intent_analysis_creation():
    """Test IntentAnalysis dataclass creation"""
    analysis = IntentAnalysis(
        work_preference_strength=0.8,
        work_preference_type="remote",
        availability_urgency=0.9,
        availability_timeline="immediate"
    )
    
    assert analysis.work_preference_strength == 0.8
    assert analysis.work_preference_type == "remote"
    assert analysis.learning_areas == []  # default empty list

def test_calculate_intent_bonuses():
    """Test bonus calculation logic"""
    analysis = IntentAnalysis(
        work_preference_strength=0.8,
        work_preference_type="remote",
        availability_urgency=0.9,
        availability_timeline="immediate",
        learning_motivation=0.7
    )
    
    job_data = {'description': 'remote work opportunity with machine learning'}
    bonuses = calculate_intent_bonuses(analysis, job_data)
    
    assert 'work_preference' in bonuses
    assert 'availability' in bonuses
    assert 'learning' in bonuses
    assert bonuses['work_preference'] > 0  # Should get remote work bonus
    assert bonuses['availability'] > 0     # Should get availability bonus

def test_generate_intent_feedback():
    """Test feedback generation"""
    analysis = IntentAnalysis(
        work_preference_strength=0.8,
        work_preference_type="remote",
        availability_urgency=0.7,
        availability_timeline="immediate",
        learning_areas=["Python", "AI"]
    )
    
    bonuses = {'work_preference': 4.0, 'availability': 3.0}
    feedback = generate_intent_feedback(analysis, bonuses)
    
    assert "Work Style: Remote" in feedback
    assert "Availability: Immediate" in feedback
    assert "Intent Bonuses" in feedback

@patch('utils.structured_comments.OpenAI')
def test_gpt_analyzer_success(mock_openai):
    """Test successful GPT analysis"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '''
    {
        "work_preference_strength": 0.8,
        "work_preference_type": "remote",
        "availability_urgency": 0.9,
        "availability_timeline": "immediate",
        "learning_motivation": 0.7,
        "learning_areas": ["Machine Learning"],
        "relocation_flexibility": 0.5,
        "experience_confidence": 0.6,
        "additional_strengths": ["Python"]
    }
    '''
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    analyzer = GPTIntentAnalyzer()
    result = analyzer.analyze_intent("I love remote work and am ready to start immediately", {})
    
    assert result.work_preference_strength == 0.8
    assert result.work_preference_type == "remote"
    assert result.availability_urgency == 0.9
    assert "Machine Learning" in result.learning_areas

@patch('utils.structured_comments.OpenAI')
def test_gpt_analyzer_error_handling(mock_openai):
    """Test GPT analyzer error handling"""
    # Mock OpenAI to raise an exception
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    analyzer = GPTIntentAnalyzer()
    result = analyzer.analyze_intent("Some comment", {})
    
    # Should return empty analysis on error
    assert result.work_preference_strength == 0.0
    assert result.work_preference_type == ""

@patch('utils.structured_comments.OpenAI')
def test_process_user_comments_integration(mock_openai):
    """Test the complete process_user_comments function"""
    # Mock the OpenAI client and its response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '''
    {
        "work_preference_strength": 0.8,
        "work_preference_type": "remote",
        "availability_urgency": 0.9,
        "availability_timeline": "immediate",
        "learning_motivation": 0.5,
        "learning_areas": [],
        "relocation_flexibility": 0.0,
        "experience_confidence": 0.6,
        "additional_strengths": []
    }
    '''
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    comments = "I prefer working remotely and can start immediately"
    job_data = {'description': 'remote position available'}
    
    result = process_user_comments(comments, job_data)
    
    assert result['total_bonus'] > 0
    assert 'intent_analysis' in result
    assert 'scoring_adjustments' in result
    assert 'structured_feedback' in result

if __name__ == "__main__":
    pytest.main([__file__])
