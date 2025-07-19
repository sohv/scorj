#!/usr/bin/env python3
"""
Test script for dual-model scoring system (OpenAI + Gemini).
This script demonstrates the enhanced scoring capabilities.
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')
load_dotenv()

from utils.scoring_engine_openai import ScoringEngine

def test_dual_model_scoring():
    """Test the dual-model scoring system."""
    
    print("Testing Dual-Model Resume Scoring System")
    print("=" * 50)
    
    # Sample resume data
    sample_resume = {
        'full_text': """
        John Doe
        Senior Software Engineer
        
        Experience:
        - 5 years as Python Developer at TechCorp
        - Built REST APIs using FastAPI and Django
        - Worked with PostgreSQL, Redis, and AWS
        - Led team of 3 developers
        
        Skills:
        Python, JavaScript, React, SQL, Docker, Kubernetes, AWS, Git
        
        Education:
        Bachelor of Science in Computer Science, MIT 2018
        """,
        'skills': ['Python', 'JavaScript', 'React', 'SQL', 'Docker', 'Kubernetes', 'AWS', 'Git'],
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp',
                'duration': '5 years',
                'description': 'Built REST APIs using FastAPI and Django'
            }
        ],
        'education': [
            {
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'institution': 'MIT',
                'year': '2018'
            }
        ]
    }
    
    # Sample job data
    sample_job = {
        'title': 'Senior Python Developer',
        'company': 'InnovateTech',
        'description': """
        We are looking for a Senior Python Developer with 3-5 years of experience.
        
        Requirements:
        - Strong Python programming skills
        - Experience with web frameworks (FastAPI, Django, Flask)
        - Database experience (PostgreSQL, MongoDB)
        - Cloud platforms (AWS, Azure)
        - Container technologies (Docker, Kubernetes)
        - Frontend knowledge (React, JavaScript) is a plus
        
        Responsibilities:
        - Design and develop scalable web applications
        - Work with cross-functional teams
        - Mentor junior developers
        """,
        'required_skills': ['Python', 'FastAPI', 'Django', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes'],
        'nice_to_have_skills': ['React', 'JavaScript', 'MongoDB'],
        'experience_level': '3-5 years'
    }
    
    # Initialize scoring engine
    print("Initializing Dual-Model Scoring Engine...")
    try:
        scoring_engine = ScoringEngine()
        print(f"OpenAI Model: {scoring_engine.openai_model}")
        print(f"Gemini Model: Available")
        print()
    except Exception as e:
        print(f"Error initializing scoring engine: {e}")
        return
    
    # Perform scoring
    print("Calculating scores with both AI models...")
    try:
        result = scoring_engine.calculate_score(sample_resume, sample_job)
        
        print("SCORING RESULTS")
        print("=" * 30)
        
        # Final score
        final_score = result.get('final_score', result.get('overall_score', 0))
        print(f"Final Combined Score: {final_score}/100")
        
        # AI comparison
        ai_comparison = result.get('ai_comparison', {})
        if ai_comparison:
            print(f"OpenAI Score: {ai_comparison.get('openai_score', 'N/A')}/100")
            print(f"Gemini Score: {ai_comparison.get('gemini_score', 'N/A')}/100")
            print(f"Consensus Level: {ai_comparison.get('consensus_level', 'N/A')}")
            
            score_variance = ai_comparison.get('score_variance')
            if score_variance is not None:
                print(f"Score Variance: ±{score_variance} points")
        
        # Transparency info
        transparency = result.get('transparency', {})
        if transparency:
            print(f"\nTRANSPARENCY INFO")
            print(f"Methodology: {transparency.get('methodology', 'N/A')}")
            print(f"Processing Time: {transparency.get('processing_time_seconds', 0):.2f}s")
            
            validation = transparency.get('validation', {})
            print(f"Both Models Available: {validation.get('both_models_available', False)}")
            print(f"Fallback Used: {validation.get('fallback_used', False)}")
        
        # Key insights
        print(f"\nKEY INSIGHTS")
        
        strengths = result.get('strengths', [])
        if strengths:
            print("Top Strengths:")
            for i, strength in enumerate(strengths[:3], 1):
                print(f"  {i}. {strength}")
        
        concerns = result.get('concerns', [])
        if concerns:
            print("Key Concerns:")
            for i, concern in enumerate(concerns[:3], 1):
                print(f"  {i}. {concern}")
        
        # Match category and summary
        match_category = result.get('match_category', 'N/A')
        print(f"\nMatch Category: {match_category}")
        
        summary = result.get('summary', '')
        if summary:
            print(f"Summary: {summary}")
        
        print("\nDual-model scoring test completed successfully!")
        
    except Exception as e:
        print(f"Error during scoring: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if required environment variables are set
    if not os.getenv('OPENAI_API_KEY'):
        print("OPENAI_API_KEY not found in environment variables")
        sys.exit(1)
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("GOOGLE_API_KEY not found in environment variables")
        sys.exit(1)
    
    test_dual_model_scoring()
