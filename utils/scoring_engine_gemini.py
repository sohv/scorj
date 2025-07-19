import os
import json
import google.generativeai as genai
from typing import Dict, Any, Tuple
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiScoringEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.weights = {
            'skills_match': 0.35,
            'experience_match': 0.30,
            'education_match': 0.15,
            'domain_expertise': 0.20
        }
        
        # Score thresholds for transparency
        self.score_ranges = {
            (90, 100): "Excellent Match - Strong candidate for the role",
            (75, 89): "Good Match - Meets most requirements with minor gaps",
            (60, 74): "Moderate Match - Some relevant experience, needs development",
            (40, 59): "Weak Match - Significant gaps in required qualifications",
            (0, 39): "Poor Match - Does not meet basic requirements"
        }

    def _create_gemini_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> str:
        """Create a Gemini-optimized prompt."""
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')
        job_title = job_data.get('title', 'Not specified')
        experience_level = job_data.get('experience_level', 'not specified')
        
        # Extract structured data for context
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        prompt = f"""
You are a senior technical recruiter. Analyze this resume against the job requirements and provide scoring.

**CONTEXT:**
Position: {job_title}
Experience Level: {experience_level}
Pre-calculated Skills Match: {skills_analysis.get('skills_match_percentage', 0):.1f}%
Experience: {experience_analysis.get('total_years_experience', 0)} years
Education: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING WEIGHTS:**
- Technical Skills (35%)
- Experience Relevance (30%) 
- Education & Qualifications (15%)
- Domain Expertise (20%)

Provide your analysis as JSON with these exact keys:
1. "overall_score": integer 0-100
2. "confidence_level": "High"/"Medium"/"Low"
3. "score_breakdown": {{"skills_score": 0-100, "experience_score": 0-100, "education_score": 0-100, "domain_score": 0-100}}
4. "match_category": score interpretation 
5. "summary": brief executive summary
6. "strengths": list of key strengths
7. "concerns": list of concerns
8. "missing_skills": list of missing skills
9. "matching_skills": list of matching skills
10. "experience_assessment": {{"relevant_years": number, "role_progression": assessment, "industry_fit": assessment}}
11. "recommendations": list of improvements
12. "risk_factors": list of potential risks

**RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

Return only valid JSON.
        """
        return prompt

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Score using Gemini."""
        try:
            prompt = self._create_gemini_prompt(resume_data, job_data, structured_analysis)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.9,
                    max_output_tokens=4000,
                    response_mime_type="application/json"
                )
            )
            
            # Debug: Log the raw response
            logger.debug(f"Gemini raw response: {response.text}")
            
            # Try to clean and parse the JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            llm_response = json.loads(response_text)
            
            # Add processing info
            processing_info = {
                'model_used': 'gemini-1.5-pro',
                'provider': 'Google Gemini',
                'processing_timestamp': datetime.now().isoformat(),
                'response_length': len(response.text) if response.text else 0
            }
            
            logger.info(f"Gemini scoring completed. Score: {llm_response.get('overall_score', 0)}")
            return llm_response, processing_info
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parsing failed. Raw response: {response.text if 'response' in locals() else 'No response'}")
            logger.error(f"JSON error: {e}")
            return self._create_error_response(f"JSON parsing error: {str(e)}"), {'error': True, 'provider': 'Gemini'}
        except Exception as e:
            logger.error(f"Gemini scoring failed: {e}")
            return self._create_error_response(str(e)), {'error': True, 'provider': 'Gemini'}

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response for failed Gemini analysis."""
        return {
            "overall_score": 0,
            "confidence_level": "Low",
            "score_breakdown": {"skills_score": 0, "experience_score": 0, "education_score": 0, "domain_score": 0},
            "match_category": "Error - Gemini analysis failed",
            "summary": f"Analysis failed due to Gemini error: {error_message}",
            "strengths": [],
            "concerns": ["Gemini analysis unavailable"],
            "missing_skills": [],
            "matching_skills": [],
            "experience_assessment": {"relevant_years": 0, "role_progression": "Unknown", "industry_fit": "Unknown"},
            "recommendations": ["Retry analysis when Gemini service is available"],
            "risk_factors": ["Gemini analysis incomplete"],
            "error_occurred": True,
            "error_message": error_message
        }

    def _get_score_interpretation(self, score: int) -> Dict[str, str]:
        """Get interpretation for the score."""
        for (min_score, max_score), interpretation in self.score_ranges.items():
            if min_score <= score <= max_score:
                return {
                    'range': f"{min_score}-{max_score}",
                    'interpretation': interpretation,
                    'hiring_recommendation': self._get_hiring_recommendation(score)
                }
        return {
            'range': 'Invalid',
            'interpretation': 'Score out of valid range',
            'hiring_recommendation': 'Review required'
        }

    def _get_hiring_recommendation(self, score: int) -> str:
        """Get hiring recommendation based on score."""
        if score >= 85:
            return "Strong hire - Proceed with interview process"
        elif score >= 70:
            return "Consider for interview - Good potential match"
        elif score >= 55:
            return "Conditional consideration - Address key gaps first"
        elif score >= 40:
            return "Weak candidate - Significant development required"
        else:
            return "Do not proceed - Poor fit for role requirements"
