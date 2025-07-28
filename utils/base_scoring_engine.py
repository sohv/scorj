from typing import Dict, Any, List
from datetime import datetime
import logging

from .skills_matcher import SkillsProcessor
from .structured_comments import process_user_comments
from .embedding_matcher import EmbeddingSkillsMatcher
from .dynamic_weights import DynamicWeightCalculator

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScoringEngine:
    
    def __init__(self):
        # Initialize new components
        self.embedding_matcher = EmbeddingSkillsMatcher()
        self.weight_calculator = DynamicWeightCalculator()
        
        # No hardcoded fallback weights - will use equal distribution if needed
        
        # Simplified 3-tier scoring system
        self.score_ranges = {
            (70, 100): "Strong Match",
            (40, 69): "Good Match", 
            (0, 39): "Weak Match"
        }
        
        # Keep legacy skills processor as fallback
        self.skills_processor = SkillsProcessor()
    
    def get_dynamic_weights(self, job_data: Dict[str, Any]) -> Dict[str, float]:
        """Get dynamic weights for scoring based on job context"""
        return self.weight_calculator.calculate_scoring_weights(job_data)

    def _enhanced_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Use embedding-based semantic matching with fallback to legacy matcher"""
        try:
            # Try embedding-based matching first
            embedding_result = self.embedding_matcher.calculate_semantic_similarity(resume_skills, job_skills)
            
            # Convert to expected format
            return {
                'match_percentage': embedding_result['coverage_percentage'],
                'matching_skills': embedding_result['matched_skills'],
                'total_job_skills': embedding_result['total_job_skills'],
                'total_matched': embedding_result['total_matched'],
                'skill_matches': embedding_result['skill_matches'],
                'similarity_score': embedding_result['similarity_score'],
                'method': 'embedding'
            }
        except Exception as e:
            logger.warning(f"Embedding matching failed, using fallback: {e}")
            # Fallback to legacy matching
            legacy_result = self.skills_processor.match_skills(resume_skills, job_skills)
            legacy_result['method'] = 'legacy'
            return legacy_result

    def _calculate_experience_relevance(self, experience: List[Dict], job_title: str, job_description: str) -> Dict[str, Any]:
        """Use embedding-based experience matching with fallback to legacy method"""
        if not experience:
            return {'relevance_score': 0, 'relevant_years': 0, 'total_years': 0}
        
        try:
            # Try embedding-based experience matching
            embedding_result = self.embedding_matcher.calculate_experience_similarity(experience, job_description)
            
            # Calculate years for relevant experiences
            total_years = self._calculate_experience_years(experience)
            relevant_years = 0
            
            for rel_exp in embedding_result['relevant_experiences']:
                exp_index = rel_exp['index']
                years = self._extract_years_from_date(experience[exp_index].get('date', ''), datetime.now().year)
                # Weight years by similarity score
                relevant_years += years * rel_exp['similarity']
            
            return {
                'relevance_score': embedding_result['similarity_score'] * 100,
                'relevant_years': relevant_years,
                'total_years': total_years,
                'relevance_ratio': relevant_years / max(1, total_years),
                'relevant_experiences': embedding_result['relevant_experiences'],
                'method': 'embedding'
            }
            
        except Exception as e:
            logger.warning(f"Embedding experience matching failed, using fallback: {e}")
            # Fallback to legacy method
            return self._legacy_calculate_experience_relevance(experience, job_title, job_description)
    
    def _legacy_calculate_experience_relevance(self, experience: List[Dict], job_title: str, job_description: str) -> Dict[str, Any]:
        """Legacy keyword-based experience relevance calculation"""
        
        total_years = 0
        relevant_years = 0
        
        # Extract key job keywords
        job_keywords = set()
        for word in (job_title + " " + job_description).lower().split():
            if len(word) > 3:  # Filter out short words
                job_keywords.add(word)
        
        for exp in experience:
            years = self._extract_years_from_date(exp.get('date', ''), datetime.now().year)
            total_years += years
            
            # Check relevance based on title and description similarity
            exp_title = exp.get('title', '').lower()
            exp_desc = exp.get('description', '').lower()
            
            # Extract experience keywords
            exp_keywords = set()
            for word in (exp_title + " " + exp_desc).split():
                if len(word) > 3:
                    exp_keywords.add(word)
            
            # Calculate keyword overlap
            overlap = len(job_keywords.intersection(exp_keywords))
            total_job_keywords = len(job_keywords)
            
            # More generous relevance calculation
            if total_job_keywords > 0:
                relevance_factor = min(1.0, overlap / (total_job_keywords * 0.3))  # 30% overlap = 100% relevance
            else:
                relevance_factor = 0.5  # Default moderate relevance
            
            # Boost relevance for obvious title matches
            if any(key in exp_title for key in ['engineer', 'developer', 'analyst', 'manager']):
                if any(key in job_title.lower() for key in ['engineer', 'developer', 'analyst', 'manager']):
                    relevance_factor = max(relevance_factor, 0.8)
            
            relevant_years += years * relevance_factor
        
        relevance_score = min(100, (relevant_years / max(1, total_years)) * 100)
        
        return {
            'relevance_score': relevance_score,
            'relevant_years': relevant_years,
            'total_years': total_years,
            'relevance_ratio': relevant_years / max(1, total_years),
            'method': 'legacy'
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

    def _create_base_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any], provider: str = "AI", dynamic_weights: Dict[str, float] = None) -> str:
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')
        job_title = job_data.get('title', 'Not specified')
        experience_level = job_data.get('experience_level', 'not specified')
        
        # Extract structured data for context
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        # Check for user comments with enhanced contextual integration
        user_comments = resume_data.get('user_comments', '')
        user_comments_section = ""
        structured_comments_data = {}
        
        if user_comments:
            # Process structured comments
            structured_comments_data = process_user_comments(user_comments, job_data)
            
            # Extract company name from job data if available
            company_name = job_data.get('company', 'the company')
            
            # Create enhanced section with structured feedback
            structured_feedback = structured_comments_data.get('structured_feedback', '')
            total_bonus = structured_comments_data.get('total_bonus', 0)
            
            # IMPORTANT: Only include comments in AI prompt if they provide positive bonus
            # This prevents misaligned comments from negatively influencing the base score
            if total_bonus > 0:
                user_comments_section = f"""

**CANDIDATE CONTEXT:**
Applying to {job_title} at {company_name}. 
Structured Profile: {structured_feedback}
Scoring Bonus Applied: +{total_bonus:.1f} points
Original Comments: "{user_comments}"
"""
            else:
                # Don't include misaligned comments in the prompt to avoid negative influence
                user_comments_section = ""
        
        # Use dynamic weights if provided, otherwise use defaults
        if dynamic_weights:
            skills_weight = int(dynamic_weights.get('skills_match', 0.35) * 100)
            experience_weight = int(dynamic_weights.get('experience_match', 0.30) * 100)
            education_weight = int(dynamic_weights.get('education_match', 0.15) * 100)
            domain_weight = int(dynamic_weights.get('domain_expertise', 0.20) * 100)
            weight_source = "DYNAMIC (AI-calculated for this job)"
        else:
            skills_weight = 35
            experience_weight = 30
            education_weight = 15
            domain_weight = 20
            weight_source = "STATIC (fallback)"

        base_prompt = f"""
You are a senior technical recruiter with 15+ years of experience. Analyze this resume against the job requirements and provide comprehensive scoring.

**JOB CONTEXT:**
Position: {job_title}
Experience Level: {experience_level}
Pre-calculated Skills Match: {skills_analysis.get('match_percentage', 0):.1f}%
Experience: {experience_analysis.get('total_years', 0)} years
Education: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING METHODOLOGY ({weight_source}):**
Use these exact weights for scoring:
- Technical Skills Match ({skills_weight}%)
- Experience Relevance ({experience_weight}%) 
- Education & Qualifications ({education_weight}%)
- Domain Expertise ({domain_weight}%)

**CRITICAL SCORING GUIDELINES:**
- Use FULL 0-100 range, avoid clustering around 70-85
- Score 90-100: Exceptional match, exceeds requirements
- Score 75-89: Good match with minor gaps
- Score 60-74: Moderate match, some development needed
- Score 40-59: Weak match, significant gaps
- Score 0-39: Poor match, fundamentally misaligned
- Be decisive: <30% skills = <50 score, >80% skills + good experience = >85 score
- Factor in candidate context when provided

**REQUIRED JSON OUTPUT:**
1. "overall_score": integer 0-100 (factor in candidate context)
2. "confidence_level": "High"/"Medium"/"Low"
3. "score_breakdown": {{"skills_score": 0-100, "experience_score": 0-100, "education_score": 0-100, "domain_score": 0-100}}
4. "match_category": score interpretation
5. "summary": brief executive summary (2-3 sentences)
6. "strengths": key strengths (3-5 items)
7. "concerns": main concerns (2-4 items)
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
