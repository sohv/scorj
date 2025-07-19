"""
Base scoring engine with common functionality shared across all scoring engines.
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScoringEngine:
    
    def __init__(self):
        # Fixed scoring weights across all roles
        self.weights = {
            'skills_match': 0.35,
            'experience_match': 0.30,
            'education_match': 0.15,
            'domain_expertise': 0.20
        }
        
        # Simplified 3-tier scoring system
        self.score_ranges = {
            (70, 100): "Strong Match",
            (40, 69): "Good Match", 
            (0, 39): "Weak Match"
        }
        
        # TF-IDF vectorizer for semantic skills matching
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)

    def _semantic_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Calculate semantic skills matching using TF-IDF and cosine similarity"""
        if not resume_skills or not job_skills:
            return {'match_percentage': 0, 'matched_skills': [], 'missing_skills': job_skills}
        
        # Combine all skills for vectorization
        all_skills = resume_skills + job_skills
        
        try:
            # Create TF-IDF vectors
            skill_vectors = self.vectorizer.fit_transform(all_skills)
            
            # Split vectors
            resume_vectors = skill_vectors[:len(resume_skills)]
            job_vectors = skill_vectors[len(resume_skills):]
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(resume_vectors, job_vectors)
            
            # Find best matches
            matched_skills = []
            missing_skills = []
            
            for j, job_skill in enumerate(job_skills):
                # Find best matching resume skill
                best_match_idx = np.argmax(similarity_matrix[:, j])
                best_similarity = similarity_matrix[best_match_idx, j]
                
                # Threshold for considering a match (0.3 is relatively permissive)
                if best_similarity > 0.3:
                    matched_skills.append({
                        'job_skill': job_skill,
                        'resume_skill': resume_skills[best_match_idx],
                        'similarity': float(best_similarity)
                    })
                else:
                    missing_skills.append(job_skill)
            
            match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
            
            return {
                'match_percentage': match_percentage,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills)
            }
            
        except Exception as e:
            logger.warning(f"Semantic matching failed, falling back to exact match: {e}")
            return self._exact_skills_match(resume_skills, job_skills)

    def _exact_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Fallback exact string matching"""
        resume_set = set(skill.lower().strip() for skill in resume_skills)
        job_set = set(skill.lower().strip() for skill in job_skills)
        
        matched = resume_set.intersection(job_set)
        missing = job_set - resume_set
        
        match_percentage = (len(matched) / len(job_set)) * 100 if job_set else 0
        
        return {
            'match_percentage': match_percentage,
            'matched_skills': [{'job_skill': skill, 'resume_skill': skill, 'similarity': 1.0} for skill in matched],
            'missing_skills': list(missing),
            'total_job_skills': len(job_skills),
            'total_resume_skills': len(resume_skills)
        }

    def _calculate_experience_relevance(self, experience: List[Dict], job_title: str, job_description: str) -> Dict[str, Any]:
        """Calculate experience relevance with weighted scoring"""
        if not experience:
            return {'relevance_score': 0, 'relevant_years': 0, 'total_years': 0}
        
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
            'relevance_ratio': relevant_years / max(1, total_years)
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
Pre-calculated Skills Match: {skills_analysis.get('match_percentage', 0):.1f}%
Experience: {experience_analysis.get('total_years', 0)} years
Education: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING METHODOLOGY:**
Use these exact weights for scoring:
- Technical Skills Match (35%)
- Experience Relevance (30%) 
- Education & Qualifications (15%)
- Domain Expertise (20%)

**CRITICAL SCORING GUIDELINES:**
- Use the FULL 0-100 range - avoid clustering around 70-85
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
