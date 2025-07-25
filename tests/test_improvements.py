#!/usr/bin/env python3

import sys
import os
import traceback

sys.path.append('.')

from utils.base_scoring_engine import BaseScoringEngine

def test_fixed_weights():
    engine = BaseScoringEngine()
    
    # Test that weights remain the same regardless of job title
    original_weights = engine.weights.copy()
    print(f"Fixed weights: {engine.weights}")
    
    # Weights should be consistent
    assert engine.weights['skills_match'] == 0.35
    assert engine.weights['experience_match'] == 0.30
    assert engine.weights['education_match'] == 0.15
    assert engine.weights['domain_expertise'] == 0.20
    
    print("Fixed weight system working correctly")

def test_enhanced_skills_matching():
    engine = BaseScoringEngine()
    
    resume_skills = ["Python", "Machine Learning", "Data Analysis", "JavaScript"]
    job_skills = ["Python", "ML", "Data Science", "React"]
    
    result = engine._enhanced_skills_match(resume_skills, job_skills)
    
    print(f"Enhanced skills match result: {result}")
    print(f"Match percentage: {result['match_percentage']:.1f}%")
    print(f"Matched skills: {result['matched_skills']}")
    print(f"Missing skills: {result['missing_skills']}")
    
    # Should find enhanced matches
    assert result['match_percentage'] > 0
    print("Enhanced skills matching working correctly")

def test_experience_relevance():
    engine = BaseScoringEngine()
    
    experience = [
        {
            "title": "Software Engineer",
            "description": "Developed Python applications using Django framework",
            "date": "2020-2023"
        },
        {
            "title": "Data Analyst", 
            "description": "Analyzed customer data using SQL and Excel",
            "date": "2018-2020"
        }
    ]
    
    job_title = "Senior Python Developer"
    job_description = "Looking for experienced Python developer with Django knowledge"
    
    result = engine._calculate_experience_relevance(experience, job_title, job_description)
    
    print(f"Experience relevance result: {result}")
    print(f"Relevance score: {result['relevance_score']:.1f}%")
    print(f"Relevant years: {result['relevant_years']:.1f}")
    print(f"Total years: {result['total_years']:.1f}")
    
    # Should find high relevance due to Python/Django match
    assert result['relevance_score'] > 50
    print("Experience relevance calculation working correctly")

def test_simplified_scoring():
    engine = BaseScoringEngine()
    
    # Test score interpretation
    score_85 = None
    score_50 = None
    score_20 = None
    
    for (min_score, max_score), category in engine.score_ranges.items():
        if min_score <= 85 <= max_score:
            score_85 = category
        if min_score <= 50 <= max_score:
            score_50 = category
        if min_score <= 20 <= max_score:
            score_20 = category
    
    print(f"Score 85 → {score_85}")
    print(f"Score 50 → {score_50}")
    print(f"Score 20 → {score_20}")
    
    assert score_85 == "Strong Match"
    assert score_50 == "Good Match"
    assert score_20 == "Weak Match"
    
    print("Simplified 3-tier scoring working correctly")

if __name__ == "__main__":
    print("Testing improved scoring engine functionality...\n")
    
    try:
        test_fixed_weights()
        print()
        
        test_enhanced_skills_matching()
        print()
        
        test_experience_relevance()
        print()
        
        test_simplified_scoring()
        print()
        
        print("All tests passed! Improvements are working correctly.")
        
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
