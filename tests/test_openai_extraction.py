"""Simple test script to verify enhanced OpenAI-based scoring is working."""

import os
import json
from utils.resume_parser import ResumeParser
from utils.job_parser import JobDescriptionParser
from utils.scoring_engine_openai import ScoringEngine

def test_enhanced_scoring():
    """Test the enhanced scoring engine with transparency and hybrid approach."""
    print("Testing Enhanced Scoring Engine...")
    
    # Sample data
    sample_resume_text = """
    John Doe
    Senior Software Engineer
    
    EXPERIENCE
    Senior Software Developer at Tech Corp (2020-2023)
    - Developed web applications using React and Node.js
    - Implemented CI/CD pipelines with Docker and Jenkins
    - Led a team of 5 developers
    - Built microservices architecture using Python and FastAPI
    
    Software Engineer at StartupCo (2018-2020)
    - Created REST APIs using Python and Django
    - Worked with PostgreSQL and Redis
    - Implemented automated testing with pytest
    
    SKILLS
    Python, JavaScript, React, Node.js, Docker, AWS, PostgreSQL, FastAPI, Django, Git, Jenkins
    
    EDUCATION
    Master of Science in Computer Science
    University of Technology (2016-2018)
    
    Bachelor of Science in Computer Science
    State University (2012-2016)
    """
    
    sample_job_text = """
    Senior Full Stack Developer
    
    We are seeking a Senior Full Stack Developer with 5+ years of experience to join our growing team.
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 5+ years of experience in web development
    - Proficiency in Python, JavaScript, and React
    - Experience with cloud services (AWS preferred)
    - Knowledge of containerization (Docker, Kubernetes)
    - Database experience with PostgreSQL or similar
    - Strong problem-solving and communication skills
    - Experience with CI/CD pipelines
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    - Participate in code reviews and architecture decisions
    """
    
    try:
        # Parse resume and job
        resume_parser = ResumeParser()
        job_parser = JobDescriptionParser()
        scoring_engine = ScoringEngine()
        
        print("Parsing resume...")
        resume_data = resume_parser._structure_text(sample_resume_text)
        print(f"Resume parsed. Skills found: {len(resume_data.get('skills', []))}")
        
        print("Parsing job description...")
        job_data = job_parser.parse_job_description_text(sample_job_text)
        print(f"Job parsed. Skills found: {len(job_data.get('skills', []))}")
        
        print("Calculating enhanced score...")
        result = scoring_engine.calculate_score(resume_data, job_data)
        
        # Extract score and feedback from the new format
        score = result.get('final_score', result.get('overall_score', 0))
        feedback = result
        
        print(f"\nSCORING RESULTS")
        print("=" * 50)
        print(f"Overall Score: {score}/100")
        print(f"Confidence Level: {feedback.get('confidence_level', 'Unknown')}")
        print(f"Match Category: {feedback.get('match_category', 'Unknown')}")
        
        # Show score breakdown
        breakdown = feedback.get('score_breakdown', {})
        print(f"\nScore Breakdown:")
        for component, score_val in breakdown.items():
            print(f"  {component.replace('_', ' ').title()}: {score_val}")
        
        # Show transparency info
        transparency = feedback.get('transparency', {})
        print(f"\nTransparency Info:")
        print(f"  Methodology: {transparency.get('scoring_methodology', 'Unknown')}")
        print(f"  Analysis Quality: {transparency.get('analysis_completeness', {}).get('quality_assessment', 'Unknown')}")
        
        # Show structured analysis
        structured = feedback.get('structured_analysis', {})
        skills_analysis = structured.get('skills_analysis', {})
        if skills_analysis:
            print(f"\nSkills Analysis:")
            print(f"  Skills Match: {skills_analysis.get('skills_match_percentage', 0):.1f}%")
            print(f"  Matching Skills: {skills_analysis.get('matching_skills_count', 0)}")
            print(f"  Missing Skills: {skills_analysis.get('missing_skills_count', 0)}")
        
        print(f"\nSummary: {feedback.get('summary', 'No summary available')}")
        
        # Save detailed results
        with open('test_scoring_results.json', 'w') as f:
            json.dump(feedback, f, indent=2)
        print(f"\nDetailed results saved to 'test_scoring_results.json'")
        
        return True
        
    except Exception as e:
        print(f"Enhanced scoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run enhanced scoring test."""
    print("Enhanced Scoring Engine Test")
    print("=" * 40)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY environment variable not set!")
        print("Please set it before running this test.")
        return
    
    success = test_enhanced_scoring()
    
    print("\n" + "=" * 40)
    if success:
        print("Enhanced scoring test passed!")
        print("Check 'test_scoring_results.json' for detailed analysis.")
    else:
        print("Enhanced scoring test failed.")

if __name__ == "__main__":
    main()
