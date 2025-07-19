"""
Base scoring engine with common functionality shared across all scoring engines.
"""
from typing import Dict, Any, List
from datetime import datetime
import logging

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScoringEngine:
    
    def __init__(self):
        # Common scoring weights across all engines
        self.weights = {
            'skills_match': 0.35,
            'experience_match': 0.30,
            'education_match': 0.15,
            'domain_expertise': 0.20
        }
        
        # Common score interpretation ranges - encourage full spectrum usage
        self.score_ranges = {
            (95, 100): "Exceptional Match - Rare top-tier candidate, exceeds requirements",
            (85, 94): "Excellent Match - Strong candidate for the role, minor gaps only",
            (70, 84): "Good Match - Meets most requirements with some development needed",
            (55, 69): "Moderate Match - Mixed qualifications, requires significant development",
            (35, 54): "Weak Match - Major gaps in required qualifications",
            (0, 34): "Poor Match - Fundamentally misaligned with role requirements"
        }

    def _get_highest_degree(self, education: List[Dict]) -> str:
        degree_hierarchy = {
            'phd': 5, 'doctorate': 5, 'doctoral': 5,
            'master': 4, 'masters': 4, 'mba': 4, 'ms': 4, 'ma': 4,
            'bachelor': 3, 'bachelors': 3, 'bs': 3, 'ba': 3, 'be': 3,
            'associate': 2, 'associates': 2,
            'diploma': 1, 'certificate': 1
        }
        
        highest_level = 0
        highest_degree = 'No degree specified'
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            for degree_type, level in degree_hierarchy.items():
                if degree_type in degree and level > highest_level:
                    highest_level = level
                    highest_degree = edu.get('degree', degree_type)
        
        return highest_degree

    def _get_degree_score(self, degree: str) -> int:
        degree_lower = degree.lower()
        if any(term in degree_lower for term in ['phd', 'doctorate', 'doctoral']):
            return 100
        elif any(term in degree_lower for term in ['master', 'mba', 'ms', 'ma']):
            return 80
        elif any(term in degree_lower for term in ['bachelor', 'bs', 'ba', 'be']):
            return 60
        elif any(term in degree_lower for term in ['associate']):
            return 40
        elif any(term in degree_lower for term in ['diploma', 'certificate']):
            return 20
        else:
            return 0

    def _evaluate_experience_level(self, years: float, required_level: str) -> Dict[str, Any]:
        level_requirements = {
            'entry': (0, 2),
            'mid': (3, 6),
            'senior': (7, float('inf'))
        }
        
        if required_level.lower() in level_requirements:
            min_years, max_years = level_requirements[required_level.lower()]
            meets_requirement = min_years <= years <= max_years
            
            return {
                'meets_requirement': meets_requirement,
                'required_range': f"{min_years}-{max_years if max_years != float('inf') else '+'} years",
                'actual_years': years,
                'level_match_score': 100 if meets_requirement else max(0, 100 - abs(years - min_years) * 10)
            }
        
        return {
            'meets_requirement': True,  # If level not specified, assume it's okay
            'required_range': 'Not specified',
            'actual_years': years,
            'level_match_score': 70  # Neutral score
        }

    def _calculate_experience_years(self, experience: List[Dict]) -> float:
        total_years = 0
        current_year = datetime.now().year
        
        for exp in experience:
            date_str = exp.get('date', '')
            years = self._extract_years_from_date(date_str, current_year)
            total_years += years
            
        return total_years

    def _extract_years_from_date(self, date_str: str, current_year: int) -> float:
        if not date_str:
            return 0
            
        import re
        
        # Handle various date formats
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4})',  # 2020-2023
            r'(\d{4})\s*[-–]\s*(?:present|current)',  # 2020-present
            r'(\d{1,2})/(\d{4})\s*[-–]\s*(\d{1,2})/(\d{4})',  # 01/2020-12/2023
            r'(\d{4})',  # Just year
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str.lower())
            if match:
                if 'present' in date_str.lower() or 'current' in date_str.lower():
                    start_year = int(match.group(1))
                    return current_year - start_year
                elif len(match.groups()) >= 2:
                    start_year = int(match.group(1))
                    end_year = int(match.group(2)) if match.group(2).isdigit() else current_year
                    return end_year - start_year
                else:
                    return 1  # Default to 1 year if only one year found
        
        return 0

    def _create_base_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any], provider: str = "AI") -> str:
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')
        job_title = job_data.get('title', 'Not specified')
        experience_level = job_data.get('experience_level', 'not specified')
        
        # Extract structured data for context
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        base_prompt = f"""
You are a senior technical recruiter with 15+ years of experience. Analyze this resume against the job requirements and provide comprehensive scoring.

**JOB CONTEXT:**
Position: {job_title}
Experience Level: {experience_level}
Pre-calculated Skills Match: {skills_analysis.get('skills_match_percentage', 0):.1f}%
Experience: {experience_analysis.get('total_years_experience', 0)} years
Education: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING METHODOLOGY:**
Use these exact weights for scoring:
- Technical Skills Match (35%)
- Experience Relevance (30%) 
- Education & Qualifications (15%)
- Domain Expertise (20%)

**CRITICAL SCORING GUIDELINES:**
- Score 90-100: Exceptional match, rare candidates who exceed most requirements
- Score 75-89: Good match with minor gaps or slight overqualification  
- Score 60-74: Moderate match requiring some development
- Score 40-59: Weak match with significant gaps
- Score 0-39: Poor match, fundamentally misaligned
- Be decisive: if skills match is <30%, score should be <50
- Be decisive: if skills match is >80% with good experience, score should be >85
- Differentiate clearly between candidates - avoid "safe middle" scores

**REQUIRED JSON OUTPUT:**
Provide your analysis as valid JSON with these exact keys:
1. "overall_score": integer 0-100 (use full range, be decisive)
2. "confidence_level": "High"/"Medium"/"Low"
3. "score_breakdown": {{"skills_score": 0-100, "experience_score": 0-100, "education_score": 0-100, "domain_score": 0-100}}
4. "match_category": score interpretation based on overall_score
5. "summary": brief executive summary (2-3 sentences)
6. "strengths": list of key strengths (3-5 items)
7. "concerns": list of concerns (2-4 items)
8. "missing_skills": list of missing required skills
9. "matching_skills": list of matching skills found
10. "experience_assessment": {{"relevant_years": number, "role_progression": assessment, "industry_fit": assessment}}
11. "recommendations": list of improvement suggestions (3-5 items)
12. "risk_factors": list of potential hiring risks (2-3 items)

**RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

Return only valid JSON without any markdown formatting or code blocks.
"""
        return base_prompt
# add this at the start of critical scoring guidelines --- Use the FULL 0-100 range - avoid clustering around 70-85
    def _create_standard_error_response(self, provider: str, error_message: str) -> Dict[str, Any]:
        return {
            "overall_score": 0,
            "confidence_level": "Low",
            "score_breakdown": {"skills_score": 0, "experience_score": 0, "education_score": 0, "domain_score": 0},
            "match_category": f"Error - {provider} analysis failed",
            "summary": f"Analysis failed due to {provider} error: {error_message}",
            "strengths": [],
            "concerns": [f"{provider} analysis unavailable"],
            "missing_skills": [],
            "matching_skills": [],
            "experience_assessment": {"relevant_years": 0, "role_progression": "Unknown", "industry_fit": "Unknown"},
            "recommendations": [f"Retry analysis when {provider} service is available"],
            "risk_factors": [f"{provider} analysis incomplete"],
            "error_occurred": True,
            "error_message": error_message
        }
