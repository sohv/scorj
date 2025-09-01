import os
import json
import re
from openai import OpenAI
from typing import Dict, Any, Tuple, List
from datetime import datetime
import logging
from dotenv import load_dotenv
from .base_scoring_engine import BaseScoringEngine

# Load environment variables
load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoringEngine(BaseScoringEngine):
    def __init__(self):
        super().__init__()  # Initialize base class
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.openai_model = "gpt-4o-mini"

    def _analyze_structured_data(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Enhanced skills analysis with semantic matching
        resume_skills = resume_data.get('skills', [])
        job_skills = job_data.get('skills', []) or job_data.get('required_skills', [])
        
        if job_skills:
            # Use enhanced skills matching from base class
            skills_match_result = self._enhanced_skills_match(resume_skills, job_skills)
            analysis['skills_analysis'] = skills_match_result
        
        # Enhanced experience analysis with relevance weighting
        resume_experience = resume_data.get('experience', [])
        if resume_experience:
            job_title = job_data.get('title', '')
            job_description = job_data.get('description', '')
            required_level = job_data.get('experience_level', 'not specified')
            
            # Calculate experience relevance
            relevance_result = self._calculate_experience_relevance(resume_experience, job_title, job_description)
            
            # Traditional experience calculation for fallback
            total_years = self._calculate_experience_years(resume_experience)
            
            analysis['experience_analysis'] = {
                'total_years': total_years,
                'relevant_years': relevance_result['relevant_years'],
                'relevance_score': relevance_result['relevance_score'],
                'relevance_ratio': relevance_result['relevance_ratio'],
                'number_of_positions': len(resume_experience),
                'required_experience_level': required_level,
                'experience_level_match': self._evaluate_experience_level(total_years, required_level)
            }
        
        # Education analysis (unchanged)
        resume_education = resume_data.get('education', [])
        if resume_education:
            highest_degree = self._get_highest_degree(resume_education)
            analysis['education_analysis'] = {
                'highest_degree': highest_degree,
                'education_count': len(resume_education),
                'degree_level_score': self._get_degree_score(highest_degree)
            }
        
        return analysis

    def _create_enhanced_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any], dynamic_weights: Dict[str, float] = None) -> str:
        return self._create_base_prompt(resume_data, job_data, structured_analysis, "OpenAI", dynamic_weights)

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting OpenAI resume scoring with dynamic weights and embeddings...")
            start_time = datetime.now()
            
            # Phase 0: Get dynamic weights for this job
            logger.info("Phase 0: Calculating dynamic weights...")
            dynamic_weights = self.get_dynamic_weights(job_data)
            logger.info(f"Dynamic weights: {dynamic_weights}")
            
            # Phase 1: Structured Data Analysis with embeddings
            logger.info("Phase 1: Performing structured data analysis with embeddings...")
            structured_analysis = self._analyze_structured_data(resume_data, job_data)
            
            # Phase 2: OpenAI Analysis with dynamic weights
            logger.info("Phase 2: Performing OpenAI analysis with dynamic weights...")
            try:
                prompt = self._create_enhanced_prompt(resume_data, job_data, structured_analysis, dynamic_weights)
                
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
                    top_p=0.9,
                    seed=42
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
            
            # Phase 3: Final Score Calculation with Structured Comments Bonus
            base_score = openai_result.get('overall_score', 0)
            
            # Process structured comments and apply bonus with dynamic weights
            user_comments = resume_data.get('user_comments', '')
            structured_bonus = 0
            structured_comments_data = {}
            
            if user_comments:
                from .structured_comments import process_user_comments
                # Get dynamic weights for comment evaluation
                try:
                    comment_weights = self.weight_calculator.calculate_comment_weights(job_data)
                except Exception as e:
                    logger.warning(f"Failed to get dynamic comment weights: {e}")
                    comment_weights = None
                
                structured_comments_data = process_user_comments(user_comments, job_data, comment_weights)
                structured_bonus = structured_comments_data.get('total_bonus', 0)
            
            # Only apply bonus if comments actually align with job requirements
            if structured_bonus > 0:
                final_score = min(100, base_score + structured_bonus)
                logger.info(f"Score calculation: Base={base_score}, Aligned Bonus={structured_bonus}, Final={final_score}")
            else:
                final_score = base_score
                logger.info(f"Score calculation: Base={base_score}, No alignment bonus (comments don't match job), Final={final_score}")
            
            # Phase 4: Create Comprehensive Response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            comprehensive_response = {
                **openai_result,
                'final_score': final_score,
                'structured_analysis': structured_analysis,
                'structured_comments': structured_comments_data,
                'openai_results': {
                    'result': openai_result,
                    'processing_info': processing_info
                },
                'transparency': {
                    'methodology': 'OpenAI GPT + Embeddings + Dynamic Weights + Context Bonuses',
                    'processing_time_seconds': round(processing_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'dynamic_weights': dynamic_weights,
                    'score_components': {
                        'structured_score': structured_analysis.get('structured_score', 0),
                        'openai_base_score': openai_result.get('overall_score', 0) if not openai_result.get('error_occurred') else 0,
                        'context_bonus': structured_bonus,
                        'bonus_applied': structured_bonus > 0,
                        'final_score': final_score
                    },
                    'validation': {
                        'embedding_matching': structured_analysis.get('skills_analysis', {}).get('method') == 'embedding',
                        'dynamic_weights_applied': bool(dynamic_weights),
                        'openai_available': not openai_result.get('error_occurred', False),
                        'fallback_used': openai_result.get('error_occurred', False),
                        'comments_provided': bool(user_comments),
                        'comments_aligned_with_job': bool(user_comments and structured_bonus > 0),
                        'bonus_earned': structured_bonus > 0
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
