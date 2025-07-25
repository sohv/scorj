#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.skills_matcher import SkillsProcessor

def test_skills_matching():
    print("Testing Enhanced Skills Processing System")
    print("=" * 50)
    
    processor = SkillsProcessor()
    
    # Test case 1: Exact matches
    print("\n1. Testing Exact Matches:")
    resume_skills_1 = ["Python", "JavaScript", "React", "Node.js"]
    job_skills_1 = ["Python", "JavaScript", "React"]
    
    result_1 = processor.match_skills(resume_skills_1, job_skills_1)
    print(f"Resume Skills: {resume_skills_1}")
    print(f"Job Skills: {job_skills_1}")
    print(f"Match Percentage: {result_1['match_percentage']:.1f}%")
    print(f"Matched Skills: {len(result_1['matched_skills'])}")
    print(f"Missing Skills: {result_1['missing_skills']}")
    
    # Test case 2: Fuzzy matches (variations)
    print("\n2. Testing Fuzzy Matches (Variations):")
    resume_skills_2 = ["ReactJS", "Node", "Javascript", "MySQL"]
    job_skills_2 = ["React", "Node.js", "JavaScript", "PostgreSQL"]
    
    result_2 = processor.match_skills(resume_skills_2, job_skills_2)
    print(f"Resume Skills: {resume_skills_2}")
    print(f"Job Skills: {job_skills_2}")
    print(f"Match Percentage: {result_2['match_percentage']:.1f}%")
    print("Matched Skills:")
    for match in result_2['matched_skills']:
        print(f"  - {match['job_skill']} ↔ {match['resume_skill']} (similarity: {match['similarity']:.2f}, type: {match['match_type']})")
    print(f"Missing Skills: {result_2['missing_skills']}")
    
    # Test case 3: Complex scenario
    print("\n3. Testing Complex Scenario:")
    resume_skills_3 = ["Python3", "Django", "React.js", "AWS", "Docker", "Git", "MySQL"]
    job_skills_3 = ["Python", "FastAPI", "React", "Amazon Web Services", "Kubernetes", "PostgreSQL", "Redis"]
    
    result_3 = processor.match_skills(resume_skills_3, job_skills_3)
    print(f"Resume Skills: {resume_skills_3}")
    print(f"Job Skills: {job_skills_3}")
    print(f"Match Percentage: {result_3['match_percentage']:.1f}%")
    print("Matched Skills:")
    for match in result_3['matched_skills']:
        print(f"  - {match['job_skill']} ↔ {match['resume_skill']} (similarity: {match['similarity']:.2f}, type: {match['match_type']})")
    print(f"Missing Skills: {result_3['missing_skills']}")
    
    # Test case 4: Skills categorization
    print("\n4. Testing Skills Categorization:")
    all_skills = ["Python", "React", "AWS", "MySQL", "TensorFlow", "Docker", "JavaScript"]
    categories = processor.categorize_skills(all_skills)
    print(f"Skills: {all_skills}")
    print("Categories:")
    for category, skills in categories.items():
        if skills:
            print(f"  - {category}: {skills}")
    
    # Test case 5: Normalization
    print("\n5. Testing Skill Normalization:")
    test_skills = ["Javascript", "reactjs", "node.js", "C++", "PostgreSQL"]
    print("Normalization examples:")
    for skill in test_skills:
        normalized = processor.normalize_skill(skill)
        print(f"  - '{skill}' → '{normalized}'")
    
    print("\n" + "=" * 50)
    print("Enhanced Skills Matching Test Complete!")

if __name__ == "__main__":
    test_skills_matching()
