import os
from typing import Dict, Any
from datetime import datetime
import logging

from .scoring_engine_openai import ScoringEngine as OpenAIScoringEngine
from .scoring_engine_gemini import GeminiScoringEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualScoringEngine:
    """Dual model scoring engine that uses both OpenAI and Gemini for comprehensive analysis."""
    
    def __init__(self):
        self.openai_engine = OpenAIScoringEngine()
        self.gemini_engine = GeminiScoringEngine()

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive resume score using both OpenAI and Gemini with transparency.
        
        Args:
            resume_data: Parsed resume data from ResumeParser
            job_data: Parsed job data from JobParser
            
        Returns:
            Dict containing dual-model scores, analysis, and transparency information
        """
        try:
            logger.info("Starting dual-model resume scoring...")
            start_time = datetime.now()
            
            # Phase 1: Structured Data Analysis (using OpenAI engine's method)
            logger.info("Phase 1: Performing structured data analysis...")
            structured_analysis = self.openai_engine._analyze_structured_data(resume_data, job_data)
            
            # Phase 2: Dual AI Analysis
            logger.info("Phase 2: Performing dual AI analysis (OpenAI + Gemini)...")
            
            # Get OpenAI analysis
            openai_result = self.openai_engine.calculate_score(resume_data, job_data)
            openai_score = openai_result.get('overall_score', 0)
            openai_processing = openai_result.get('openai_results', {}).get('processing_info', {})
            
            # Get Gemini analysis
            try:
                gemini_result, gemini_processing = self.gemini_engine.calculate_score(resume_data, job_data, structured_analysis)
                gemini_score = gemini_result.get('overall_score', 0)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                gemini_result = self.gemini_engine._create_error_response(str(e))
                gemini_processing = {'error': True, 'provider': 'Gemini'}
                gemini_score = 0
            
            # Phase 3: Combine AI Results
            logger.info("Phase 3: Combining AI results and creating consensus...")
            combined_analysis = self._combine_ai_scores(openai_result, gemini_result, structured_analysis)
            
            # Phase 4: Final Score Calculation
            final_score = combined_analysis.get('overall_score', 0)
            
            # Phase 5: Create Comprehensive Response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            comprehensive_response = {
                **combined_analysis,
                'final_score': final_score,
                'structured_analysis': structured_analysis,
                'dual_model_results': {
                    'openai': {
                        'result': openai_result,
                        'processing_info': openai_processing
                    },
                    'gemini': {
                        'result': gemini_result,
                        'processing_info': gemini_processing
                    }
                },
                'transparency': {
                    'methodology': 'Dual AI (OpenAI + Gemini) + Structured Analysis',
                    'processing_time_seconds': round(processing_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'score_components': {
                        'structured_score': structured_analysis.get('structured_score', 0),
                        'openai_score': openai_score if not openai_result.get('error_occurred') else 0,
                        'gemini_score': gemini_score if not gemini_result.get('error_occurred') else 0,
                        'final_combined_score': final_score
                    },
                    'validation': {
                        'models_agreement': combined_analysis.get('ai_comparison', {}).get('consensus_level', 'Unknown'),
                        'score_variance': combined_analysis.get('ai_comparison', {}).get('score_variance'),
                        'both_models_available': not (openai_result.get('error_occurred') or gemini_result.get('error_occurred')),
                        'fallback_used': openai_result.get('error_occurred') and gemini_result.get('error_occurred')
                    }
                }
            }
            
            logger.info(f"Dual-model resume scoring completed. Final score: {final_score}")
            return comprehensive_response
            
        except Exception as e:
            logger.error(f"Error in dual model calculate_score: {e}")
            return {
                'overall_score': 0,
                'confidence_level': 'Low',
                'match_category': 'Error',
                'summary': f'Dual model analysis failed: {str(e)}',
                'error': True,
                'error_message': str(e)
            }

    def _combine_ai_scores(self, openai_result: Dict[str, Any], gemini_result: Dict[str, Any], structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine scores from both AI providers."""
        
        # Extract scores
        openai_score = openai_result.get('overall_score', 0) if not openai_result.get('error_occurred') else 0
        gemini_score = gemini_result.get('overall_score', 0) if not gemini_result.get('error_occurred') else 0
        
        # Calculate combined metrics
        if openai_score > 0 and gemini_score > 0:
            # Both models provided scores
            combined_score = int((openai_score + gemini_score) / 2)
            score_variance = abs(openai_score - gemini_score)
            consensus_level = "High" if score_variance <= 10 else "Medium" if score_variance <= 20 else "Low"
        elif openai_score > 0:
            # Only OpenAI provided a score
            combined_score = openai_score
            score_variance = None
            consensus_level = "Single Model (OpenAI)"
        elif gemini_score > 0:
            # Only Gemini provided a score
            combined_score = gemini_score
            score_variance = None
            consensus_level = "Single Model (Gemini)"
        else:
            # Both failed, use structured analysis fallback
            skills_score = structured_analysis.get('skills_analysis', {}).get('skills_match_percentage', 0)
            experience_score = structured_analysis.get('experience_analysis', {}).get('level_match_score', 0)
            education_score = structured_analysis.get('education_analysis', {}).get('degree_level_score', 0)
            combined_score = int(skills_score * 0.5 + experience_score * 0.3 + education_score * 0.2)
            score_variance = None
            consensus_level = "Fallback Only"
        
        # Combine qualitative feedback (prefer non-error responses)
        primary_result = openai_result if not openai_result.get('error_occurred') else gemini_result
        if primary_result.get('error_occurred'):
            primary_result = self._create_fallback_qualitative_response(structured_analysis)
        
        # Create combined response
        combined_response = {
            **primary_result,
            "overall_score": combined_score,
            "ai_comparison": {
                "openai_score": openai_score,
                "gemini_score": gemini_score,
                "score_variance": score_variance,
                "consensus_level": consensus_level,
                "agreement_analysis": self._analyze_agreement(openai_result, gemini_result)
            }
        }
        
        return combined_response

    def _analyze_agreement(self, openai_result: Dict[str, Any], gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agreement between the two AI models."""
        analysis = {
            "both_available": not (openai_result.get('error_occurred') or gemini_result.get('error_occurred')),
            "score_agreement": None,
            "qualitative_agreement": None
        }
        
        if analysis["both_available"]:
            openai_score = openai_result.get('overall_score', 0)
            gemini_score = gemini_result.get('overall_score', 0)
            score_diff = abs(openai_score - gemini_score)
            
            if score_diff <= 5:
                analysis["score_agreement"] = "Very High"
            elif score_diff <= 10:
                analysis["score_agreement"] = "High"
            elif score_diff <= 15:
                analysis["score_agreement"] = "Moderate"
            elif score_diff <= 25:
                analysis["score_agreement"] = "Low"
            else:
                analysis["score_agreement"] = "Very Low"
            
            # Compare key qualitative aspects
            openai_strengths = set(openai_result.get('strengths', []))
            gemini_strengths = set(gemini_result.get('strengths', []))
            strength_overlap = len(openai_strengths.intersection(gemini_strengths))
            
            analysis["qualitative_agreement"] = {
                "strength_overlap": strength_overlap,
                "total_strengths": len(openai_strengths.union(gemini_strengths)),
                "agreement_percentage": (strength_overlap / max(len(openai_strengths.union(gemini_strengths)), 1)) * 100
            }
        
        return analysis

    def _create_fallback_qualitative_response(self, structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create qualitative response from structured analysis when both AIs fail."""
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        
        return {
            "confidence_level": "Low",
            "score_breakdown": {
                "skills_score": int(skills_analysis.get('skills_match_percentage', 0)),
                "experience_score": int(experience_analysis.get('level_match_score', 50)),
                "education_score": int(structured_analysis.get('education_analysis', {}).get('degree_level_score', 50)),
                "domain_score": 0
            },
            "match_category": "Analysis Limited - AI Unavailable",
            "summary": "Analysis completed using structured data only due to AI service unavailability.",
            "strengths": skills_analysis.get('matching_skills', [])[:3],
            "concerns": ["Limited analysis depth", "AI services unavailable"],
            "missing_skills": skills_analysis.get('missing_skills', []),
            "matching_skills": skills_analysis.get('matching_skills', []),
            "experience_assessment": experience_analysis,
            "recommendations": ["Retry when AI services are available", "Manual review recommended"],
            "risk_factors": ["Incomplete analysis"]
        }
