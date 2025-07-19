import os
import json
import google.generativeai as genai
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
from dotenv import load_dotenv
from .base_scoring_engine import BaseScoringEngine

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiScoringEngine(BaseScoringEngine):
    def __init__(self):
        super().__init__()  # Initialize base class
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _create_gemini_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> str:
        return self._create_base_prompt(resume_data, job_data, structured_analysis, "Gemini")

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            logger.info("Starting Gemini resume scoring...")
            start_time = datetime.now()
            
            # Use provided structured analysis or create minimal fallback
            if structured_analysis is None:
                structured_analysis = {
                    'skills_analysis': {},
                    'experience_analysis': {},
                    'education_analysis': {}
                }
            
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
            
            gemini_result = json.loads(response_text)
            
            # Add processing info
            processing_info = {
                'model_used': 'gemini-1.5-pro',
                'provider': 'Google Gemini',
                'processing_timestamp': datetime.now().isoformat(),
                'response_length': len(response.text) if response.text else 0
            }
            
            # Phase 3: Final Score Calculation
            final_score = gemini_result.get('overall_score', 0)
            
            # Phase 4: Create Comprehensive Response (matching OpenAI format)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            comprehensive_response = {
                **gemini_result,
                'final_score': final_score,
                'structured_analysis': structured_analysis,
                'gemini_results': {
                    'result': gemini_result,
                    'processing_info': processing_info
                },
                'transparency': {
                    'methodology': 'Google Gemini + Structured Analysis',
                    'processing_time_seconds': round(processing_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'score_components': {
                        'structured_score': structured_analysis.get('structured_score', 0),
                        'gemini_score': gemini_result.get('overall_score', 0) if not gemini_result.get('error_occurred') else 0,
                        'final_score': final_score
                    },
                    'validation': {
                        'gemini_available': not gemini_result.get('error_occurred', False),
                        'fallback_used': gemini_result.get('error_occurred', False)
                    }
                }
            }
            
            logger.info(f"Gemini resume scoring completed. Final score: {final_score}")
            return comprehensive_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parsing failed. Raw response: {response.text if 'response' in locals() else 'No response'}")
            logger.error(f"JSON error: {e}")
            error_response = self._create_error_response(f"JSON parsing error: {str(e)}")
            processing_info = {'error': True, 'provider': 'Gemini'}
            return self._create_standardized_error_response(error_response, processing_info)
        except Exception as e:
            logger.error(f"Gemini scoring failed: {e}")
            error_response = self._create_error_response(str(e))
            processing_info = {'error': True, 'provider': 'Gemini'}
            return self._create_standardized_error_response(error_response, processing_info)

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        return self._create_standard_error_response("Gemini", error_message)

    def _get_score_interpretation(self, score: int) -> Dict[str, str]:
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
