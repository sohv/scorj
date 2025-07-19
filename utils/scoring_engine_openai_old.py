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

    def _score_with_openai(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Score using OpenAI."""
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
            llm_response = json.loads(feedback_json)
            
            # Add processing info
            processing_info = {
                'model_used': self.openai_model,
                'provider': 'OpenAI',
                'processing_timestamp': datetime.now().isoformat(),
                'prompt_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') else 'unknown',
                'completion_tokens': response.usage.completion_tokens if hasattr(response, 'usage') else 'unknown',
                'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
            }
            
            logger.info(f"OpenAI scoring completed. Score: {llm_response.get('overall_score', 0)}")
            return llm_response, processing_info
            
        except Exception as e:
            logger.error(f"OpenAI scoring failed: {e}")
            return self._create_error_response("OpenAI", str(e)), {'error': True, 'provider': 'OpenAI'}

    def _score_with_gemini(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], structured_analysis: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Score using Gemini."""
        try:
            prompt = self._create_gemini_prompt(resume_data, job_data, structured_analysis)
            
            response = self.gemini_model.generate_content(
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
            return self._create_error_response("Gemini", f"JSON parsing error: {str(e)}"), {'error': True, 'provider': 'Gemini'}
        except Exception as e:
            logger.error(f"Gemini scoring failed: {e}")
            return self._create_error_response("Gemini", str(e)), {'error': True, 'provider': 'Gemini'}

    def _create_error_response(self, provider: str, error_message: str) -> Dict[str, Any]:
        """Create an error response for a failed provider."""
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
            consensus_level = "Single Model"
        elif gemini_score > 0:
            # Only Gemini provided a score
            combined_score = gemini_score
            score_variance = None
            consensus_level = "Single Model"
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
        """Create an enhanced prompt with structured data and clear scoring criteria."""
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')
        job_title = job_data.get('title', 'Not specified')
        experience_level = job_data.get('experience_level', 'not specified')
        
        # Extract structured data for context
        skills_analysis = structured_analysis.get('skills_analysis', {})
        experience_analysis = structured_analysis.get('experience_analysis', {})
        education_analysis = structured_analysis.get('education_analysis', {})
        
        prompt = f"""
You are an expert technical recruiter and resume analyst. Analyze this resume against the job requirements using the following structured approach.

**JOB CONTEXT:**
- Position: {job_title}
- Experience Level: {experience_level}
- Industry Focus: Extract from job description

**STRUCTURED ANALYSIS PROVIDED:**
- Skills Match: {skills_analysis.get('skills_match_percentage', 0):.1f}% ({skills_analysis.get('matching_skills_count', 0)}/{skills_analysis.get('total_required_skills', 0)} skills)
- Experience: {experience_analysis.get('total_years_experience', 0)} years (Required: {experience_analysis.get('required_range', 'Not specified')})
- Education: {education_analysis.get('highest_degree', 'Not specified')}

**SCORING CRITERIA (0-100):**
Use this weighted scoring system:
- Technical Skills Match (35%): Exact skill matches, related technologies, tool proficiency
- Experience Relevance (30%): Years of experience, role seniority, industry relevance, project complexity
- Education & Qualifications (15%): Degree level, relevant certifications, specialized training
- Domain Expertise (20%): Industry knowledge, specific methodologies, leadership experience

**SCORING RANGES:**
- 90-100: Exceptional candidate, exceeds requirements
- 75-89: Strong candidate, meets most requirements  
- 60-74: Adequate candidate, some gaps to address
- 40-59: Below threshold, significant development needed
- 0-39: Not suitable, major misalignment

**ANALYSIS REQUIREMENTS:**
Provide detailed JSON analysis with these exact keys:

1. "overall_score": Integer 0-100 based on weighted criteria above
2. "confidence_level": "High"/"Medium"/"Low" based on information quality
3. "score_breakdown": {{
   "skills_score": 0-100,
   "experience_score": 0-100,
   "education_score": 0-100,
   "domain_score": 0-100
}}
4. "match_category": One of the scoring ranges above
5. "summary": Two-sentence executive summary of candidate fit
6. "strengths": List of 3-5 specific strengths with evidence from resume
7. "concerns": List of 2-4 specific gaps or concerns with impact assessment
8. "missing_skills": List of required skills/technologies not found in resume
9. "matching_skills": List of skills that directly match job requirements
10. "experience_assessment": {{
    "relevant_years": Number,
    "role_progression": "Strong"/"Moderate"/"Weak"/"Unclear",
    "industry_fit": "Excellent"/"Good"/"Fair"/"Poor"
}}
11. "recommendations": List of 3-4 specific improvement suggestions
12. "risk_factors": List of potential hiring risks (cultural fit, overqualification, etc.)

**IMPORTANT INSTRUCTIONS:**
- Be specific and evidence-based in your analysis
- Consider role seniority and industry context
- Account for transferable skills and growth potential
- Flag any red flags (employment gaps, role regression, etc.)
- Be objective and avoid bias

---
**RESUME:**
{resume_text}

---
**JOB DESCRIPTION:**
{job_description}

---

Return ONLY a valid JSON object with the specified structure. Be thorough but concise.
        """
        return prompt

    def _validate_and_enhance_response(self, llm_response: Dict[str, Any], structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM response and enhance with structured data."""
        
        # Ensure all required fields exist
        required_fields = [
            'overall_score', 'confidence_level', 'score_breakdown', 'match_category',
            'summary', 'strengths', 'concerns', 'missing_skills', 'matching_skills',
            'experience_assessment', 'recommendations', 'risk_factors'
        ]
        
        for field in required_fields:
            if field not in llm_response:
                logger.warning(f"Missing field {field} in LLM response")
                llm_response[field] = self._get_default_value(field)
        
        # Validate score ranges
        overall_score = llm_response.get('overall_score', 0)
        if not isinstance(overall_score, int) or not (0 <= overall_score <= 100):
            logger.warning(f"Invalid overall_score: {overall_score}")
            llm_response['overall_score'] = 0
        
        # Add structured analysis data
        llm_response['structured_analysis'] = structured_analysis
        
        # Add transparency metadata
        llm_response['transparency'] = {
            'scoring_methodology': 'Hybrid: Structured analysis + LLM evaluation',
            'weight_distribution': self.weights,
            'score_interpretation': self._get_score_interpretation(overall_score),
            'analysis_completeness': self._assess_analysis_completeness(llm_response),
            'data_quality_flags': self._check_data_quality(structured_analysis)
        }
        
        return llm_response

    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields."""
        defaults = {
            'overall_score': 0,
            'confidence_level': 'Low',
            'score_breakdown': {'skills_score': 0, 'experience_score': 0, 'education_score': 0, 'domain_score': 0},
            'match_category': 'Poor Match - Analysis incomplete',
            'summary': 'Analysis could not be completed due to insufficient data.',
            'strengths': [],
            'concerns': ['Analysis incomplete'],
            'missing_skills': [],
            'matching_skills': [],
            'experience_assessment': {'relevant_years': 0, 'role_progression': 'Unclear', 'industry_fit': 'Poor'},
            'recommendations': ['Provide more detailed resume information'],
            'risk_factors': ['Incomplete analysis - results may be unreliable']
        }
        return defaults.get(field, None)

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

    def _assess_analysis_completeness(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how complete the analysis is."""
        completeness_score = 0
        total_checks = 0
        
        # Check if key sections have content
        checks = [
            ('strengths', len(response.get('strengths', [])) > 0),
            ('concerns', len(response.get('concerns', [])) > 0),
            ('missing_skills', 'missing_skills' in response),
            ('matching_skills', 'matching_skills' in response),
            ('recommendations', len(response.get('recommendations', [])) > 0),
            ('score_breakdown', isinstance(response.get('score_breakdown'), dict))
        ]
        
        for check_name, passed in checks:
            total_checks += 1
            if passed:
                completeness_score += 1
        
        completeness_percentage = (completeness_score / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            'completeness_percentage': completeness_percentage,
            'missing_elements': [name for name, passed in checks if not passed],
            'quality_assessment': 'High' if completeness_percentage > 80 else 'Medium' if completeness_percentage > 50 else 'Low'
        }

    def _check_data_quality(self, structured_analysis: Dict[str, Any]) -> List[str]:
        """Check for data quality issues."""
        flags = []
        
        metadata = structured_analysis.get('metadata', {})
        
        # Check resume length
        resume_length = metadata.get('resume_length', 0)
        if resume_length < 500:
            flags.append('Short resume - may lack detail')
        elif resume_length > 10000:
            flags.append('Very long resume - may contain irrelevant information')
        
        # Check job description length
        job_length = metadata.get('job_description_length', 0)
        if job_length < 200:
            flags.append('Brief job description - may lack detail')
        
        # Check skills data
        skills_analysis = structured_analysis.get('skills_analysis', {})
        if skills_analysis.get('total_required_skills', 0) == 0:
            flags.append('No skills extracted from job description')
        
        # Check experience data
        experience_analysis = structured_analysis.get('experience_analysis', {})
        if experience_analysis.get('total_years_experience', 0) == 0:
            flags.append('No work experience found')
        
        return flags
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
            openai_result, openai_processing = self._score_with_openai(resume_data, job_data, structured_analysis)
            
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
                    'processing_info': openai_processing
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

    def _create_fallback_response(self, error_message: str, structured_analysis: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Create a fallback response when AI analysis fails."""
        
        # Calculate basic score from structured analysis
        skills_score = structured_analysis.get('skills_analysis', {}).get('skills_match_percentage', 0)
        experience_score = structured_analysis.get('experience_analysis', {}).get('level_match_score', 0)
        education_score = structured_analysis.get('education_analysis', {}).get('degree_level_score', 0)
        
        # Simple weighted average as fallback
        fallback_score = int(
            skills_score * 0.5 + 
            experience_score * 0.3 + 
            education_score * 0.2
        )
        
        fallback_response = {
            "overall_score": fallback_score,
            "confidence_level": "Low",
            "score_breakdown": {
                "skills_score": int(skills_score),
                "experience_score": int(experience_score),
                "education_score": int(education_score),
                "domain_score": 0
            },
            "match_category": self._get_score_interpretation(fallback_score)['interpretation'],
            "summary": f"Analysis completed using fallback method due to AI processing error. Score based on structured data analysis only.",
            "strengths": structured_analysis.get('skills_analysis', {}).get('matching_skills', [])[:3],
            "concerns": ["AI analysis unavailable", "Limited analysis depth"],
            "missing_skills": structured_analysis.get('skills_analysis', {}).get('missing_skills', [])[:5],
            "matching_skills": structured_analysis.get('skills_analysis', {}).get('matching_skills', []),
            "experience_assessment": structured_analysis.get('experience_analysis', {}),
            "recommendations": ["Retry analysis when AI service is available", "Manual review recommended"],
            "risk_factors": ["Analysis incomplete due to technical issues"],
            "structured_analysis": structured_analysis,
            "error_info": {
                "error_occurred": True,
                "error_message": error_message,
                "fallback_method": "Structured analysis only",
                "timestamp": datetime.now().isoformat()
            },
            "transparency": {
                "scoring_methodology": "Fallback: Structured analysis only (AI unavailable)",
                "weight_distribution": {"skills": 0.5, "experience": 0.3, "education": 0.2},
                "score_interpretation": self._get_score_interpretation(fallback_score),
                "analysis_completeness": {"completeness_percentage": 60, "quality_assessment": "Limited"},
                "data_quality_flags": self._check_data_quality(structured_analysis)
            }
        }
        
        logger.warning(f"Using fallback scoring method. Score: {fallback_score}")
        return fallback_score, fallback_response