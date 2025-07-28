from openai import OpenAI
import json
import os
from typing import Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DynamicWeightCalculator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
    def calculate_scoring_weights(self, job_data: Dict[str, Any]) -> Dict[str, float]:
        """Use GPT to determine dynamic weights for main scoring components"""
        
        prompt = f"""
        Analyze this job posting and determine the optimal scoring weights based on what the employer emphasizes most.
        
        Job Title: {job_data.get('title', 'Not specified')}
        Company: {job_data.get('company', 'Not specified')}
        Experience Level: {job_data.get('experience_level', 'Not specified')}
        
        Job Description:
        {job_data.get('description', 'Not available')[:1500]}
        
        Based on the job posting, determine weights (0.0-1.0, must sum to 1.0) for these scoring components:
        
        - skills_match: How much technical skills and tools matter
        - experience_match: How much relevant work experience matters  
        - education_match: How much formal education/degrees matter
        - domain_expertise: How much industry/domain knowledge matters
        
        Consider:
        - What does the job description emphasize most?
        - Are specific skills listed as "required" vs "nice to have"?
        - Is years of experience heavily mentioned?
        - Are degree requirements strict or flexible?
        - Is domain knowledge critical or can it be learned?
        
        Return ONLY valid JSON:
        {{
            "weights": {{
                "skills_match": 0.XX,
                "experience_match": 0.XX,
                "education_match": 0.XX,
                "domain_expertise": 0.XX
            }},
            "reasoning": "Brief explanation of weight decisions"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter who analyzes job postings to determine what employers value most. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            weights = result.get('weights', {})
            
            # Validate and normalize weights
            if self._validate_weights(weights):
                logger.info(f"Dynamic scoring weights calculated: {weights}")
                return weights
            else:
                logger.warning("Invalid weights from GPT, using fallback")
                return self._get_fallback_scoring_weights()
                
        except Exception as e:
            logger.error(f"Error calculating dynamic scoring weights: {e}")
            return self._get_fallback_scoring_weights()
    
    def calculate_comment_weights(self, job_data: Dict[str, Any]) -> Dict[str, float]:
        """Use GPT to determine dynamic weights for comment evaluation dimensions"""
        
        prompt = f"""
        Analyze this job posting and determine how much weight each candidate self-assessment dimension should have.
        
        Job Title: {job_data.get('title', 'Not specified')}
        Company: {job_data.get('company', 'Not specified')}
        
        Job Description:
        {job_data.get('description', 'Not available')[:1200]}
        
        Based on this job, determine weights (0.0-1.0, must sum to 1.0) for evaluating candidate comments across these dimensions:
        
        - technical_skills: How much technical skill claims matter
        - work_arrangement: How much work style preferences matter (remote/office/hybrid)
        - availability: How much start date/timing matters
        - role_focus: How much role interest alignment matters
        - experience_level: How much claimed seniority level matters
        
        Consider:
        - Is this a technical role requiring specific skills?
        - Does the job mention remote/hybrid/office requirements?
        - Is there urgency in hiring timeline?
        - Is role passion/interest important for this position?
        - How critical is the experience level match?
        
        Return ONLY valid JSON:
        {{
            "weights": {{
                "technical_skills": 0.XX,
                "work_arrangement": 0.XX,
                "availability": 0.XX,
                "role_focus": 0.XX,
                "experience_level": 0.XX
            }},
            "reasoning": "Brief explanation"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter who determines what matters most in candidate self-assessments. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            weights = result.get('weights', {})
            
            # Validate and normalize weights
            if self._validate_weights(weights):
                logger.info(f"Dynamic comment weights calculated: {weights}")
                return weights
            else:
                logger.warning("Invalid comment weights from GPT, using fallback")
                return self._get_fallback_comment_weights()
                
        except Exception as e:
            logger.error(f"Error calculating dynamic comment weights: {e}")
            return self._get_fallback_comment_weights()
    
    def _validate_weights(self, weights: Dict[str, float]) -> bool:
        """Validate that weights are valid and sum to approximately 1.0"""
        if not weights or not isinstance(weights, dict):
            return False
        
        # Check all values are floats between 0 and 1
        for key, value in weights.items():
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                return False
        
        # Check sum is approximately 1.0 (allow small floating point errors)
        total = sum(weights.values())
        if not (0.95 <= total <= 1.05):
            return False
        
        return True
    
    def _get_fallback_scoring_weights(self) -> Dict[str, float]:
        """Generate equal weights if GPT fails - no hardcoding"""
        components = ['skills_match', 'experience_match', 'education_match', 'domain_expertise']
        equal_weight = 1.0 / len(components)
        return {component: equal_weight for component in components}
    
    def _get_fallback_comment_weights(self) -> Dict[str, float]:
        """Generate equal weights if GPT fails - no hardcoding"""
        dimensions = ['technical_skills', 'work_arrangement', 'availability', 'role_focus', 'experience_level']
        equal_weight = 1.0 / len(dimensions)
        return {dimension: equal_weight for dimension in dimensions}