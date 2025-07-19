import os
from typing import Dict, Any, List
from datetime import datetime
import logging
import asyncio

from .scoring_engine_openai import ScoringEngine as OpenAIScoringEngine
from .scoring_engine_gemini import GeminiScoringEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoringResult:
    def __init__(self, result_dict: Dict[str, Any]):
        self.raw_result = result_dict
        self.score = result_dict.get('overall_score', 0)
        self.final_score = result_dict.get('final_score', self.score)
        self.confidence = self._calculate_confidence(result_dict)
        self.error_occurred = result_dict.get('error_occurred', False)
        self.provider = self._get_provider(result_dict)
        
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        if result.get('error_occurred', False):
            return 0.0
            
        confidence_level = result.get('confidence_level', 'Medium').lower()
        base_confidence = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.4
        }.get(confidence_level, 0.5)
        
        # Adjust based on score certainty (scores near extremes are more confident)
        score = self.score
        if score >= 85 or score <= 25:
            base_confidence += 0.1
        elif 40 <= score <= 70:
            base_confidence -= 0.1
            
        # Adjust based on data completeness
        transparency = result.get('transparency', {})
        if transparency.get('validation', {}).get('fallback_used', False):
            base_confidence -= 0.2
            
        return max(0.1, min(1.0, base_confidence))
    
    def _get_provider(self, result: Dict[str, Any]) -> str:
        if 'openai_results' in result:
            return 'OpenAI'
        elif 'gemini_results' in result:
            return 'Gemini'
        else:
            return 'Unknown'

class DualScoringEngine:
    def __init__(self):
        self.openai_engine = OpenAIScoringEngine()
        self.gemini_engine = GeminiScoringEngine()

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
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
            openai_scoring_result = ScoringResult(openai_result)
            
            # Get Gemini analysis  
            try:
                gemini_result = self.gemini_engine.calculate_score(resume_data, job_data, structured_analysis)
                gemini_scoring_result = ScoringResult(gemini_result)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                error_result = self.gemini_engine._create_standardized_error_response(
                    self.gemini_engine._create_error_response(str(e)),
                    {'error': True, 'provider': 'Gemini'}
                )
                gemini_scoring_result = ScoringResult(error_result)
            
            # Phase 3: Combine AI Results with intelligent scoring
            logger.info("Phase 3: Combining AI results with intelligent consensus...")
            scoring_results = [openai_scoring_result, gemini_scoring_result]
            combined_analysis = self._intelligent_score_combination(scoring_results, structured_analysis)
            
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
                        'processing_info': openai_result.get('openai_results', {}).get('processing_info', {})
                    },
                    'gemini': {
                        'result': gemini_result,
                        'processing_info': gemini_result.get('gemini_results', {}).get('processing_info', {})
                    }
                },
                'transparency': {
                    'methodology': 'Dual AI (OpenAI + Gemini) + Structured Analysis',
                    'processing_time_seconds': round(processing_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'score_components': {
                        'structured_score': structured_analysis.get('structured_score', 0),
                        'openai_score': openai_scoring_result.score if not openai_scoring_result.error_occurred else 0,
                        'gemini_score': gemini_scoring_result.score if not gemini_scoring_result.error_occurred else 0,
                        'final_combined_score': final_score
                    },
                    'validation': {
                        'models_agreement': combined_analysis.get('ai_comparison', {}).get('consensus_level', 'Unknown'),
                        'score_variance': combined_analysis.get('ai_comparison', {}).get('score_variance'),
                        'both_models_available': not (openai_scoring_result.error_occurred or gemini_scoring_result.error_occurred),
                        'fallback_used': openai_scoring_result.error_occurred and gemini_scoring_result.error_occurred,
                        'confidence_weighted_scoring': True
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

    def _intelligent_score_combination(self, scoring_results: List[ScoringResult], structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        
        # Filter out error results and calculate weighted score
        valid_results = [r for r in scoring_results if not r.error_occurred and r.score > 0]
        
        if len(valid_results) >= 2:
            # Both models provided scores - use confidence-weighted average
            weighted_sum = sum(r.score * r.confidence for r in valid_results)
            total_confidence = sum(r.confidence for r in valid_results)
            combined_score = int(weighted_sum / total_confidence) if total_confidence > 0 else 0
            
            # Calculate variance and consensus using coefficient of variation
            scores = [r.score for r in valid_results]
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5
            coefficient_of_variation = (std_dev / mean_score) if mean_score > 0 else 1.0
            
            # More sophisticated consensus assessment
            if coefficient_of_variation <= 0.1:  # ≤10% variation
                consensus_level = "Very High"
            elif coefficient_of_variation <= 0.2:  # ≤20% variation
                consensus_level = "High" 
            elif coefficient_of_variation <= 0.35:  # ≤35% variation
                consensus_level = "Medium"
            elif coefficient_of_variation <= 0.5:  # ≤50% variation
                consensus_level = "Low"
            else:
                consensus_level = "Very Low"
                
            score_variance = std_dev
            
        elif len(valid_results) == 1:
            # Single model provided score
            result = valid_results[0]
            combined_score = result.score
            score_variance = None
            consensus_level = f"Single Model ({result.provider})"
            
        else:
            # Both failed, use structured analysis fallback with improved weighting
            skills_score = structured_analysis.get('skills_analysis', {}).get('skills_match_percentage', 0)
            experience_analysis = structured_analysis.get('experience_analysis', {})
            experience_score = experience_analysis.get('level_match_score', 50)
            education_score = structured_analysis.get('education_analysis', {}).get('degree_level_score', 50)
            
            # More balanced fallback weighting (matches individual engine weights)
            combined_score = int(
                skills_score * 0.35 +          # Skills match (35%)
                experience_score * 0.30 +      # Experience (30%) 
                education_score * 0.15 +       # Education (15%)
                0 * 0.20                       # Domain expertise (20% - unavailable in fallback)
            )
            score_variance = None
            consensus_level = "Fallback Only"
        
        # Select best qualitative feedback intelligently
        primary_result = self._select_primary_result(scoring_results, structured_analysis)
        
        # Enhanced agreement analysis
        agreement_analysis = self._enhanced_agreement_analysis(scoring_results)
        
        # Create combined response
        combined_response = {
            **primary_result,
            "overall_score": combined_score,
            "ai_comparison": {
                "openai_score": next((r.score for r in scoring_results if r.provider == 'OpenAI'), 0),
                "gemini_score": next((r.score for r in scoring_results if r.provider == 'Gemini'), 0),
                "score_variance": score_variance,
                "consensus_level": consensus_level,
                "agreement_analysis": agreement_analysis,
                "confidence_weights": {
                    r.provider.lower(): r.confidence for r in scoring_results
                }
            }
        }
        
        return combined_response

    def _select_primary_result(self, scoring_results: List[ScoringResult], structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        
        # Find the result with highest confidence and no errors
        valid_results = [r for r in scoring_results if not r.error_occurred]
        
        if not valid_results:
            # Both failed - create enhanced fallback response
            return self._create_enhanced_fallback_response(structured_analysis)
        
        # Select result with highest confidence
        best_result = max(valid_results, key=lambda r: r.confidence)
        return best_result.raw_result

    def _enhanced_agreement_analysis(self, scoring_results: List[ScoringResult]) -> Dict[str, Any]:
        
        valid_results = [r for r in scoring_results if not r.error_occurred]
        
        analysis = {
            "both_available": len(valid_results) >= 2,
            "models_used": [r.provider for r in scoring_results],
            "confidence_scores": {r.provider.lower(): r.confidence for r in scoring_results},
            "score_agreement": None,
            "qualitative_agreement": None
        }
        
        if len(valid_results) >= 2:
            # Calculate score agreement with statistical measures
            scores = [r.score for r in valid_results]
            mean_score = sum(scores) / len(scores)
            max_deviation = max(abs(s - mean_score) for s in scores)
            
            # More nuanced agreement levels
            if max_deviation <= 3:
                analysis["score_agreement"] = "Exceptional"
            elif max_deviation <= 7:
                analysis["score_agreement"] = "Very High"
            elif max_deviation <= 12:
                analysis["score_agreement"] = "High"
            elif max_deviation <= 18:
                analysis["score_agreement"] = "Moderate"
            elif max_deviation <= 25:
                analysis["score_agreement"] = "Low"
            else:
                analysis["score_agreement"] = "Very Low"
            
            # Enhanced qualitative comparison
            try:
                openai_result = next(r.raw_result for r in valid_results if r.provider == 'OpenAI')
                gemini_result = next(r.raw_result for r in valid_results if r.provider == 'Gemini')
                
                # Compare multiple qualitative aspects
                openai_strengths = set(openai_result.get('strengths', []))
                gemini_strengths = set(gemini_result.get('strengths', []))
                
                openai_concerns = set(openai_result.get('concerns', []))
                gemini_concerns = set(gemini_result.get('concerns', []))
                
                strength_overlap = len(openai_strengths.intersection(gemini_strengths))
                concern_overlap = len(openai_concerns.intersection(gemini_concerns))
                
                total_unique_strengths = len(openai_strengths.union(gemini_strengths))
                total_unique_concerns = len(openai_concerns.union(gemini_concerns))
                
                analysis["qualitative_agreement"] = {
                    "strength_overlap": strength_overlap,
                    "concern_overlap": concern_overlap,
                    "total_strengths": total_unique_strengths,
                    "total_concerns": total_unique_concerns,
                    "strength_agreement_pct": (strength_overlap / max(total_unique_strengths, 1)) * 100,
                    "concern_agreement_pct": (concern_overlap / max(total_unique_concerns, 1)) * 100
                }
            except (StopIteration, KeyError):
                analysis["qualitative_agreement"] = {"error": "Could not compare qualitative aspects"}
        
        return analysis

    def _create_enhanced_fallback_response(self, structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        # More intelligent fallback recommendations
        missing_skills = skills_analysis.get('missing_skills', [])
        matching_skills = skills_analysis.get('matching_skills', [])
        skills_match_pct = skills_analysis.get('skills_match_percentage', 0)
        
        # Generate contextual recommendations
        recommendations = []
        if skills_match_pct < 50:
            recommendations.append("Focus on developing technical skills mentioned in job requirements")
        if missing_skills:
            recommendations.extend([f"Consider gaining experience with {skill}" for skill in missing_skills[:3]])
        recommendations.extend([
            "Retry analysis when AI services are available", 
            "Consider manual review by hiring manager"
        ])
        
        return {
            "confidence_level": "Low",
            "score_breakdown": {
                "skills_score": int(skills_match_pct),
                "experience_score": int(experience_analysis.get('level_match_score', 50)),
                "education_score": int(education_analysis.get('degree_level_score', 50)),
                "domain_score": 0
            },
            "match_category": "Analysis Limited - AI Services Unavailable",
            "summary": f"Structured analysis shows {skills_match_pct:.1f}% skills match. Limited depth due to AI service unavailability.",
            "strengths": matching_skills[:3] if matching_skills else ["Analysis incomplete"],
            "concerns": ["Limited analysis depth", "AI services unavailable"] + (["Significant skills gaps"] if skills_match_pct < 30 else []),
            "missing_skills": missing_skills[:5],
            "matching_skills": matching_skills,
            "experience_assessment": experience_analysis,
            "recommendations": recommendations[:5],  # Limit to 5 recommendations
            "risk_factors": ["Incomplete analysis", "AI verification unavailable"]
        }


