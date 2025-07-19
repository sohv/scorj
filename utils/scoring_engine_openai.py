import os
import json
import re
from openai import OpenAI
from typing import Dict, Any, Tuple, List
from datetime import datetime
import logging

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.openai_model = "gpt-4o-mini"
        
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

    def _analyze_structured_data(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform structured analysis before LLM processing."""
        analysis = {
            'skills_analysis': {},
            'experience_analysis': {},
            'education_analysis': {},
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'resume_length': len(resume_data.get('full_text', '')),
                'job_description_length': len(job_data.get('description', ''))
            }
        }
        
        # Skills analysis
        resume_skills = set(skill.lower().strip() for skill in resume_data.get('skills', []))
        job_skills = set(skill.lower().strip() for skill in job_data.get('skills', []))
        
        if job_skills:
            matching_skills = resume_skills.intersection(job_skills)
            missing_skills = job_skills - resume_skills
            
            analysis['skills_analysis'] = {
                'total_required_skills': len(job_skills),
                'matching_skills_count': len(matching_skills),
                'missing_skills_count': len(missing_skills),
                'skills_match_percentage': (len(matching_skills) / len(job_skills)) * 100 if job_skills else 0,
                'matching_skills': list(matching_skills),
                'missing_skills': list(missing_skills)
            }
        
        # Experience analysis
        resume_experience = resume_data.get('experience', [])
        if resume_experience:
            total_years = self._calculate_experience_years(resume_experience)
            required_level = job_data.get('experience_level', 'not specified')
            
            analysis['experience_analysis'] = {
                'total_years_experience': total_years,
                'number_of_positions': len(resume_experience),
                'required_experience_level': required_level,
                'experience_level_match': self._evaluate_experience_level(total_years, required_level)
            }
        
        # Education analysis
        resume_education = resume_data.get('education', [])
        if resume_education:
            highest_degree = self._get_highest_degree(resume_education)
            analysis['education_analysis'] = {
                'highest_degree': highest_degree,
                'education_count': len(resume_education),
                'degree_level_score': self._get_degree_score(highest_degree)
            }
        
        return analysis

    def _calculate_experience_years(self, experience: List[Dict]) -> float:
        """Calculate total years of experience from structured data."""
        total_years = 0
        current_year = datetime.now().year
        
        for exp in experience:
            date_str = exp.get('date', '')
            years = self._extract_years_from_date(date_str, current_year)
            total_years += years
            
        return total_years

    def _extract_years_from_date(self, date_str: str, current_year: int) -> float:
        """Extract years of experience from date string."""
        if not date_str:
            return 0
            
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

    def _evaluate_experience_level(self, years: float, required_level: str) -> Dict[str, Any]:
        """Evaluate if experience matches required level."""
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

    def _get_highest_degree(self, education: List[Dict]) -> str:
        """Get the highest degree from education list."""
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
        """Get numerical score for degree level."""
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
            
    def _create_enhanced_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> str:
        """Create an enhanced OpenAI prompt with structured context."""
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')
        job_title = job_data.get('title', 'Not specified')
        experience_level = job_data.get('experience_level', 'not specified')
        
        # Extract structured data for context
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        prompt = f"""
You are a senior technical recruiter with 15+ years of experience. Analyze this resume against the job requirements.

**JOB CONTEXT:**
Position: {job_title}
Experience Level: {experience_level}

**PRE-ANALYSIS DATA:**
- Skills Match: {skills_analysis.get('skills_match_percentage', 0):.1f}%
- Candidate Experience: {experience_analysis.get('total_years_experience', 0)} years
- Education Level: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING CRITERIA:**
Rate each category 0-100, then provide overall score:
1. Technical Skills (35% weight): Depth and relevance of technical abilities
2. Experience Relevance (30% weight): Years and quality of relevant experience
3. Education & Qualifications (15% weight): Academic background and certifications
4. Domain Expertise (20% weight): Industry knowledge and specialized skills

**RESPONSE FORMAT:**
Provide your analysis as valid JSON with these exact keys:
{{"overall_score": <0-100>, "confidence_level": "High/Medium/Low", "score_breakdown": {{"skills_score": <0-100>, "experience_score": <0-100>, "education_score": <0-100>, "domain_score": <0-100>}}, "match_category": "<interpretation>", "summary": "<executive summary>", "strengths": ["<strength1>", "<strength2>"], "concerns": ["<concern1>", "<concern2>"], "missing_skills": ["<skill1>", "<skill2>"], "matching_skills": ["<skill1>", "<skill2>"], "experience_assessment": {{"relevant_years": <number>, "role_progression": "<assessment>", "industry_fit": "<assessment>"}}, "recommendations": ["<rec1>", "<rec2>"], "risk_factors": ["<risk1>", "<risk2>"]}}

**RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

Provide only valid JSON in your response.
        """
        return prompt

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive resume score using OpenAI with transparency.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            job_data: Parsed job data from JobParser
            
        Returns:
            Dict containing OpenAI analysis and transparency information
        """
        try:
            logger.info("Starting OpenAI resume scoring...")
            start_time = datetime.now()
            
            # Phase 1: Structured Data Analysis
            logger.info("Phase 1: Performing structured data analysis...")
            structured_analysis = self._analyze_structured_data(resume_data, job_data)
            
            # Phase 2: OpenAI Analysis
            logger.info("Phase 2: Performing OpenAI analysis...")
            try:
                prompt = self._create_enhanced_prompt(resume_data, job_data, structured_analysis)
                
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a senior technical recruiter with 15+ years of experience in talent acquisition across multiple industries. You provide detailed, objective, and actionable resume analysis."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=2000,
                    top_p=0.9
                )
                
                feedback_json = response.choices[0].message.content
                openai_result = json.loads(feedback_json)
                
                # Add processing info
                processing_info = {
                    'model_used': self.openai_model,
                    'provider': 'OpenAI',
                    'processing_timestamp': datetime.now().isoformat(),
                    'prompt_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') else 'unknown',
                    'completion_tokens': response.usage.completion_tokens if hasattr(response, 'usage') else 'unknown',
                    'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
                }
                
                logger.info(f"OpenAI scoring completed. Score: {openai_result.get('overall_score', 0)}")
                
            except Exception as e:
                logger.error(f"OpenAI scoring failed: {e}")
                openai_result = self._create_error_response(str(e))
                processing_info = {'error': True, 'provider': 'OpenAI'}
            
            # Phase 3: Final Score Calculation
            final_score = openai_result.get('overall_score', 0)
            
            # Phase 4: Create Comprehensive Response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            comprehensive_response = {
                **openai_result,
                'final_score': final_score,
                'structured_analysis': structured_analysis,
                'openai_results': {
                    'result': openai_result,
                    'processing_info': processing_info
                },
                'transparency': {
                    'methodology': 'OpenAI GPT + Structured Analysis',
                    'processing_time_seconds': round(processing_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'score_components': {
                        'structured_score': structured_analysis.get('structured_score', 0),
                        'openai_score': openai_result.get('overall_score', 0) if not openai_result.get('error_occurred') else 0,
                        'final_score': final_score
                    },
                    'validation': {
                        'openai_available': not openai_result.get('error_occurred', False),
                        'fallback_used': openai_result.get('error_occurred', False)
                    }
                }
            }
            
            logger.info(f"OpenAI resume scoring completed. Final score: {final_score}")
            return comprehensive_response
            
        except Exception as e:
            logger.error(f"Error in calculate_score: {e}")
            return {
                'overall_score': 0,
                'confidence_level': 'Low',
                'match_category': 'Error',
                'summary': f'Analysis failed: {str(e)}',
                'error': True,
                'error_message': str(e)
            }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response for failed OpenAI analysis."""
        return {
            "overall_score": 0,
            "confidence_level": "Low",
            "score_breakdown": {"skills_score": 0, "experience_score": 0, "education_score": 0, "domain_score": 0},
            "match_category": "Error - OpenAI analysis failed",
            "summary": f"Analysis failed due to OpenAI error: {error_message}",
            "strengths": [],
            "concerns": ["OpenAI analysis unavailable"],
            "missing_skills": [],
            "matching_skills": [],
            "experience_assessment": {"relevant_years": 0, "role_progression": "Unknown", "industry_fit": "Unknown"},
            "recommendations": ["Retry analysis when OpenAI service is available"],
            "risk_factors": ["OpenAI analysis incomplete"],
            "error_occurred": True,
            "error_message": error_message
        }
