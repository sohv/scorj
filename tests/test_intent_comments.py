import pytest
import json
from unittest.mock import patch, MagicMock
from utils.structured_comments import (
    process_user_comments,
    GPTMultiDimensionalAnalyzer,
    MultiDimensionalAnalysis,
    TechnicalAlignment,
    WorkArrangementAlignment,
    AvailabilityAlignment,
    RoleFocusAlignment,
    ExperienceLevelAlignment,
    calculate_multi_dimensional_bonuses,
    generate_multi_dimensional_feedback
)

# Test for empty or invalid input
def test_process_empty_comments():
    """Test that empty comments return a default structure with zero bonus."""
    result = process_user_comments("", {})
    assert result['total_bonus'] == 0
    assert result['structured_feedback'] == "No context provided"
    # The 'multi_dimensional_analysis' key should be present but empty
    assert result['multi_dimensional_analysis'] == {}

# Test the main dataclass
def test_multi_dimensional_analysis_creation():
    """Test the creation of the main analysis dataclass."""
    analysis = MultiDimensionalAnalysis(
        technical=TechnicalAlignment(claimed_skills=["Python"], alignment_score=0.8),
        work_arrangement=WorkArrangementAlignment(preferred_arrangement="remote", alignment_score=1.0)
    )
    assert analysis.technical.alignment_score == 0.8
    assert analysis.work_arrangement.preferred_arrangement == "remote"
    assert analysis.availability.alignment_score == 0.0  # Default value

# Test bonus calculation
def test_calculate_multi_dimensional_bonuses():
    """Test the bonus calculation logic with dynamic weights."""
    analysis = MultiDimensionalAnalysis(
        technical=TechnicalAlignment(alignment_score=0.9),
        work_arrangement=WorkArrangementAlignment(alignment_score=1.0),
        availability=AvailabilityAlignment(alignment_score=0.0), # No alignment
        role_focus=RoleFocusAlignment(alignment_score=0.7),
        experience_level=ExperienceLevelAlignment(alignment_score=0.5)
    )
    
    # With dynamic weights
    dynamic_weights = {
        'technical_skills': 0.4,
        'work_arrangement': 0.1,
        'availability': 0.1,
        'role_focus': 0.2,
        'experience_level': 0.2
    }
    
    bonuses = calculate_multi_dimensional_bonuses(analysis, dynamic_weights)
    
    # Max bonus is 20 points
    assert bonuses['technical_alignment'] == pytest.approx(0.9 * (0.4 * 20))
    assert bonuses['work_arrangement'] == pytest.approx(1.0 * (0.1 * 20))
    assert 'availability' not in bonuses # Score is 0, so no bonus key
    assert bonuses['role_focus'] == pytest.approx(0.7 * (0.2 * 20))
    assert bonuses['experience_level'] == pytest.approx(0.5 * (0.2 * 20))

# Test feedback generation
def test_generate_multi_dimensional_feedback():
    """Test the generation of human-readable feedback."""
    analysis = MultiDimensionalAnalysis(
        technical=TechnicalAlignment(claimed_skills=["Python", "AWS"], alignment_score=0.8),
        work_arrangement=WorkArrangementAlignment(preferred_arrangement="remote", alignment_score=1.0)
    )
    bonuses = {'technical_alignment': 5.0, 'work_arrangement': 2.0}
    
    feedback = generate_multi_dimensional_feedback(analysis, bonuses)
    
    assert "Technical Skills: Python, AWS (Strong match)" in feedback
    assert "Work Style: Remote (Aligned)" in feedback
    assert "Total Alignment Bonus: +7.0 points" in feedback

# Mock the GPT call for the analyzer
@patch('utils.structured_comments.OpenAI')
def test_gpt_analyzer_success(mock_openai):
    """Test a successful analysis by the GPTMultiDimensionalAnalyzer."""
    mock_response_content = {
        "technical": {
            "claimed_skills": ["Python", "React"],
            "experience_claims": ["Built a full-stack app"],
            "technical_confidence": 0.9
        },
        "work_arrangement": {
            "preferred_arrangement": "remote",
            "arrangement_strength": 0.8
        },
        "availability": {
            "availability_timeline": "immediate",
            "availability_urgency": 1.0
        },
        "role_focus": {
            "role_interests": ["frontend development"],
            "focus_areas": ["UI/UX"]
        },
        "experience_level": {
            "experience_level_claim": "mid",
            "confidence_level": 0.85
        }
    }
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(mock_response_content)
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    analyzer = GPTMultiDimensionalAnalyzer()
    # Mock job data for validation context
    job_data = {
        'description': 'seeking a remote python developer for a mid-level role.',
        'title': 'Software Engineer'
    }
    
    analysis = analyzer.analyze_comments("I am a mid-level python dev looking for a remote role.", job_data)
    
    # Check if parsing was successful
    assert analysis.technical.technical_confidence == 0.9
    assert analysis.work_arrangement.preferred_arrangement == "remote"
    
    # Check if validation logic was triggered and produced a score > 0
    assert analysis.technical.alignment_score > 0
    assert analysis.work_arrangement.alignment_score > 0
    assert analysis.experience_level.alignment_score > 0

# Test error handling in the analyzer
@patch('utils.structured_comments.OpenAI')
def test_gpt_analyzer_error_handling(mock_openai):
    """Test that the analyzer returns a default object on API error."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    analyzer = GPTMultiDimensionalAnalyzer()
    analysis = analyzer.analyze_comments("some comment", {})
    
    # Should return a default, empty analysis object
    assert analysis.technical.alignment_score == 0.0
    assert analysis.work_arrangement.preferred_arrangement == ""

# Test the full integration of process_user_comments
@patch('utils.structured_comments.GPTMultiDimensionalAnalyzer.analyze_comments')
@patch('utils.dynamic_weights.DynamicWeightCalculator.calculate_comment_weights')
def test_process_user_comments_integration(mock_calc_weights, mock_analyze_comments):
    """Test the full process_user_comments function with mocks."""
    # Mock the analysis result
    mock_analysis = MultiDimensionalAnalysis(
        technical=TechnicalAlignment(claimed_skills=["Python"], alignment_score=0.8),
        work_arrangement=WorkArrangementAlignment(preferred_arrangement="remote", alignment_score=0.9)
    )
    mock_analyze_comments.return_value = mock_analysis
    
    # Mock the dynamic weights
    mock_weights = {'technical_skills': 0.5, 'work_arrangement': 0.5}
    mock_calc_weights.return_value = mock_weights
    
    comments = "I am a great fit"
    job_data = {'description': 'a job'}
    
    result = process_user_comments(comments, job_data)
    
    assert result['total_bonus'] > 0
    assert result['scoring_adjustments']['technical_alignment'] > 0
    assert result['scoring_adjustments']['work_arrangement'] > 0
    assert "Technical Skills" in result['structured_feedback'] # Check if feedback was generated

# Test specific validation scenarios
def test_alignment_validation_logic():
    """Test specific validation cases for alignment scores."""
    analyzer = GPTMultiDimensionalAnalyzer()
    
    # SCENARIO 1: Misaligned work preference (Job: remote, User: onsite)
    work_pref = WorkArrangementAlignment(preferred_arrangement="onsite", arrangement_strength=0.9)
    job_req_remote = analyzer._extract_job_requirements({'description': 'fully remote job'})
    analyzer._validate_work_arrangement_alignment(work_pref, job_req_remote)
    assert work_pref.alignment_score == 0.0 # Should be 0 for direct conflict

    # SCENARIO 2: Aligned technical skills (Job requires Python, User claims Python)
    tech_claim = TechnicalAlignment(claimed_skills=["Python"], technical_confidence=0.9)
    job_req_python = analyzer._extract_job_requirements({'description': 'must have python'})
    analyzer._validate_technical_alignment(tech_claim, job_req_python)
    assert tech_claim.alignment_score > 0.7 # Should be high

    # SCENARIO 3: Misaligned technical skills (Job requires Python, User claims Java)
    tech_claim_wrong = TechnicalAlignment(claimed_skills=["Java"], technical_confidence=0.9)
    analyzer._validate_technical_alignment(tech_claim_wrong, job_req_python)
    assert tech_claim_wrong.alignment_score == 0.0 # Should be 0

    # SCENARIO 4: Misaligned experience level (Job: senior, User: junior)
    exp_claim = ExperienceLevelAlignment(experience_level_claim="junior", confidence_level=0.9)
    job_req_senior = analyzer._extract_job_requirements({'title': 'senior software engineer'})
    analyzer._validate_experience_level_alignment(exp_claim, job_req_senior)
    assert exp_claim.alignment_score == 0.0 # Junior applying to senior is 0

if __name__ == "__main__":
    pytest.main([__file__])