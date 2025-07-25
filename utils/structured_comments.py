from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from openai import OpenAI
import os
import re

@dataclass
class TechnicalAlignment:
    claimed_skills: List[str] = None
    experience_claims: List[str] = None
    technical_confidence: float = 0.0
    alignment_score: float = 0.0
    
    def __post_init__(self):
        if self.claimed_skills is None:
            self.claimed_skills = []
        if self.experience_claims is None:
            self.experience_claims = []

@dataclass
class WorkArrangementAlignment:
    preferred_arrangement: str = ""  # remote/hybrid/onsite/flexible
    arrangement_strength: float = 0.0
    alignment_score: float = 0.0

@dataclass
class AvailabilityAlignment:
    availability_timeline: str = ""  # immediate/weeks/months/flexible
    availability_urgency: float = 0.0
    alignment_score: float = 0.0

@dataclass
class RoleFocusAlignment:
    role_interests: List[str] = None
    focus_areas: List[str] = None
    alignment_score: float = 0.0
    
    def __post_init__(self):
        if self.role_interests is None:
            self.role_interests = []
        if self.focus_areas is None:
            self.focus_areas = []

@dataclass
class ExperienceLevelAlignment:
    experience_level_claim: str = ""  # junior/mid/senior/expert
    confidence_level: float = 0.0
    alignment_score: float = 0.0

@dataclass
class MultiDimensionalAnalysis:
    technical: TechnicalAlignment = None
    work_arrangement: WorkArrangementAlignment = None
    availability: AvailabilityAlignment = None
    role_focus: RoleFocusAlignment = None
    experience_level: ExperienceLevelAlignment = None
    
    def __post_init__(self):
        if self.technical is None:
            self.technical = TechnicalAlignment()
        if self.work_arrangement is None:
            self.work_arrangement = WorkArrangementAlignment()
        if self.availability is None:
            self.availability = AvailabilityAlignment()
        if self.role_focus is None:
            self.role_focus = RoleFocusAlignment()
        if self.experience_level is None:
            self.experience_level = ExperienceLevelAlignment()

class GPTMultiDimensionalAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    def analyze_comments(self, comments: str, job_data: Dict[str, Any]) -> MultiDimensionalAnalysis:
        """Analyze user comments across all dimensions and validate against job requirements"""
        if not comments or not comments.strip():
            return MultiDimensionalAnalysis()
        
        # Extract job requirements for validation
        job_requirements = self._extract_job_requirements(job_data)
        
        # Analyze user claims across all dimensions
        analysis_prompt = self._create_analysis_prompt(comments, job_requirements)
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing candidate comments for alignment with job requirements across technical skills, work arrangement, availability, role focus, and experience level."},
                {"role": "user", "content": analysis_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1200
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Parse the GPT response into structured analysis
        multi_analysis = self._parse_multi_dimensional_response(result)
        
        # Validate each dimension against job requirements
        self._validate_technical_alignment(multi_analysis.technical, job_requirements)
        self._validate_work_arrangement_alignment(multi_analysis.work_arrangement, job_requirements)
        self._validate_availability_alignment(multi_analysis.availability, job_requirements)
        self._validate_role_focus_alignment(multi_analysis.role_focus, job_requirements)
        self._validate_experience_level_alignment(multi_analysis.experience_level, job_requirements)
        
        return multi_analysis

    def _extract_job_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key requirements from job data for validation"""
        description = job_data.get('description', '').lower()
        title = job_data.get('title', '').lower()
        
        # Extract technical requirements
        tech_keywords = ['python', 'javascript', 'java', 'react', 'angular', 'vue', 'django', 'flask', 
                        'spring', 'node.js', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'sql', 
                        'postgresql', 'mysql', 'mongodb', 'redis', 'git', 'ci/cd', 'rest', 'api']
        
        required_tech = []
        preferred_tech = []
        
        for tech in tech_keywords:
            if any(phrase in description for phrase in [f'required {tech}', f'must have {tech}', f'{tech} required']):
                required_tech.append(tech)
            elif tech in description:
                preferred_tech.append(tech)
        
        # Extract work arrangement
        work_arrangement = 'flexible'
        if any(word in description for word in ['remote', 'work from home', 'distributed']):
            work_arrangement = 'remote'
        elif any(word in description for word in ['office', 'onsite', 'on-site', 'in-person']):
            work_arrangement = 'onsite'
        elif any(word in description for word in ['hybrid']):
            work_arrangement = 'hybrid'
        
        # Extract experience level
        experience_level = 'mid'
        if any(word in title.lower() for word in ['senior', 'lead', 'principal', 'staff']):
            experience_level = 'senior'
        elif any(word in title.lower() for word in ['junior', 'entry', 'graduate', 'intern']):
            experience_level = 'junior'
        
        # Check for years of experience
        exp_match = re.search(r'(\d+)[\+\-]?\s*(?:years?|yrs?)', description)
        required_years = int(exp_match.group(1)) if exp_match else 0
        
        return {
            'required_tech': required_tech,
            'preferred_tech': preferred_tech,
            'work_arrangement': work_arrangement,
            'experience_level': experience_level,
            'required_years': required_years,
            'description': description,
            'title': title
        }

    def _create_analysis_prompt(self, comments: str, job_requirements: Dict[str, Any]) -> str:
        return f"""Analyze the candidate's comments for specific claims across 5 dimensions. Extract concrete claims, not general sentiments.

Job Requirements Context:
- Required Tech: {job_requirements.get('required_tech', [])}
- Preferred Tech: {job_requirements.get('preferred_tech', [])}
- Work Arrangement: {job_requirements.get('work_arrangement', 'flexible')}
- Experience Level: {job_requirements.get('experience_level', 'mid')}
- Required Years: {job_requirements.get('required_years', 0)}

Candidate Comments: "{comments}"

Extract specific claims and rate confidence (0-1 scale):

Return JSON:
{{
    "technical": {{
        "claimed_skills": ["skill1", "skill2"],
        "experience_claims": ["claim1", "claim2"], 
        "technical_confidence": 0.0-1.0
    }},
    "work_arrangement": {{
        "preferred_arrangement": "remote/hybrid/onsite/flexible",
        "arrangement_strength": 0.0-1.0
    }},
    "availability": {{
        "availability_timeline": "immediate/weeks/months/flexible",
        "availability_urgency": 0.0-1.0
    }},
    "role_focus": {{
        "role_interests": ["interest1", "interest2"],
        "focus_areas": ["area1", "area2"]
    }},
    "experience_level": {{
        "experience_level_claim": "junior/mid/senior/expert",
        "confidence_level": 0.0-1.0
    }}
}}

Only extract concrete claims. Empty arrays for no specific claims."""

    def _parse_multi_dimensional_response(self, response: Dict) -> MultiDimensionalAnalysis:
        """Parse GPT response into structured multi-dimensional analysis"""
        technical_data = response.get('technical', {})
        work_data = response.get('work_arrangement', {})
        availability_data = response.get('availability', {})
        role_data = response.get('role_focus', {})
        experience_data = response.get('experience_level', {})
        
        return MultiDimensionalAnalysis(
            technical=TechnicalAlignment(
                claimed_skills=technical_data.get('claimed_skills', []),
                experience_claims=technical_data.get('experience_claims', []),
                technical_confidence=float(technical_data.get('technical_confidence', 0))
            ),
            work_arrangement=WorkArrangementAlignment(
                preferred_arrangement=work_data.get('preferred_arrangement', ''),
                arrangement_strength=float(work_data.get('arrangement_strength', 0))
            ),
            availability=AvailabilityAlignment(
                availability_timeline=availability_data.get('availability_timeline', ''),
                availability_urgency=float(availability_data.get('availability_urgency', 0))
            ),
            role_focus=RoleFocusAlignment(
                role_interests=role_data.get('role_interests', []),
                focus_areas=role_data.get('focus_areas', [])
            ),
            experience_level=ExperienceLevelAlignment(
                experience_level_claim=experience_data.get('experience_level_claim', ''),
                confidence_level=float(experience_data.get('confidence_level', 0))
            )
        )

    def _validate_technical_alignment(self, technical: TechnicalAlignment, job_req: Dict[str, Any]):
        """Validate technical skills alignment with job requirements (40% weight)"""
        if not technical.claimed_skills and not technical.experience_claims:
            technical.alignment_score = 0.0
            return
        
        required_tech = job_req.get('required_tech', [])
        preferred_tech = job_req.get('preferred_tech', [])
        all_job_tech = required_tech + preferred_tech
        
        if not all_job_tech:
            # If no tech requirements found, NO POINTS - can't validate alignment
            technical.alignment_score = 0.0
            return
        
        # Calculate skill overlap - ONLY reward actual matches
        claimed_lower = [skill.lower() for skill in technical.claimed_skills]
        
        # Check for exact matches only
        required_matches = sum(1 for tech in required_tech if tech.lower() in claimed_lower)
        preferred_matches = sum(1 for tech in preferred_tech if tech.lower() in claimed_lower)
        
        # Check for partial/related matches (substring matching)
        partial_required = sum(1 for tech in required_tech 
                             if any(tech.lower() in skill or skill in tech.lower() 
                                   for skill in claimed_lower))
        partial_preferred = sum(1 for tech in preferred_tech 
                              if any(tech.lower() in skill or skill in tech.lower() 
                                    for skill in claimed_lower))
        
        # Calculate scores - ONLY if there are actual matches
        if required_tech:
            required_score = (required_matches + 0.5 * partial_required) / len(required_tech)
        else:
            required_score = 0
            
        if preferred_tech:
            preferred_score = (preferred_matches + 0.5 * partial_preferred) / len(preferred_tech)
        else:
            preferred_score = 0
        
        # Combine scores: required skills worth 70%, preferred skills worth 30%
        if required_tech and preferred_tech:
            base_score = (required_score * 0.7) + (preferred_score * 0.3)
        elif required_tech:
            base_score = required_score
        else:
            base_score = preferred_score
        
        # NO BASE CREDIT - only actual matches count
        if base_score == 0:
            technical.alignment_score = 0.0
            return
        
        # Apply confidence multiplier
        confidence_multiplier = max(0.5, technical.technical_confidence)
        technical.alignment_score = min(1.0, base_score * confidence_multiplier)

    def _validate_work_arrangement_alignment(self, work: WorkArrangementAlignment, job_req: Dict[str, Any]):
        """Validate work arrangement alignment (20% weight)"""
        if not work.preferred_arrangement or work.arrangement_strength < 0.3:
            work.alignment_score = 0.0
            return
        
        job_arrangement = job_req.get('work_arrangement', 'flexible')
        user_pref = work.preferred_arrangement.lower()
        
        # ONLY reward actual alignment - no participation points
        if user_pref == job_arrangement:
            work.alignment_score = 1.0
        elif (user_pref == 'flexible') or (job_arrangement == 'flexible'):
            work.alignment_score = 0.8
        elif (user_pref == 'hybrid' and job_arrangement in ['remote', 'onsite']):
            work.alignment_score = 0.6
        elif (user_pref == 'remote' and job_arrangement == 'hybrid'):
            work.alignment_score = 0.7
        elif (user_pref == 'onsite' and job_arrangement == 'hybrid'):
            work.alignment_score = 0.5
        else:
            # NO POINTS for misaligned preferences
            work.alignment_score = 0.0
        
        # Apply strength multiplier
        work.alignment_score *= work.arrangement_strength

    def _validate_availability_alignment(self, availability: AvailabilityAlignment, job_req: Dict[str, Any]):
        """Validate availability alignment (15% weight)"""
        if not availability.availability_timeline or availability.availability_urgency < 0.3:
            availability.alignment_score = 0.0
            return
        
        timeline = availability.availability_timeline.lower()
        
        # Check if job mentions urgency
        job_desc = job_req.get('description', '').lower()
        urgent_keywords = ['urgent', 'immediate', 'asap', 'start immediately', 'right away']
        job_is_urgent = any(keyword in job_desc for keyword in urgent_keywords)
        
        # ONLY reward appropriate availability - no participation points
        if timeline == 'immediate':
            availability.alignment_score = 1.0
        elif timeline in ['weeks', 'flexible']:
            availability.alignment_score = 0.8 if not job_is_urgent else 0.7
        elif timeline == 'months':
            # Give points only if job is NOT urgent
            availability.alignment_score = 0.4 if not job_is_urgent else 0.0
        else:
            availability.alignment_score = 0.5
        
        # Apply urgency multiplier
        availability.alignment_score *= availability.availability_urgency

    def _validate_role_focus_alignment(self, role_focus: RoleFocusAlignment, job_req: Dict[str, Any]):
        """Validate role focus alignment (15% weight)"""
        if not role_focus.role_interests and not role_focus.focus_areas:
            role_focus.alignment_score = 0.0
            return
        
        job_title = job_req.get('title', '').lower()
        job_desc = job_req.get('description', '').lower()
        
        # Look for role-specific keywords
        role_keywords = {
            'frontend': ['frontend', 'front-end', 'ui', 'ux', 'react', 'angular', 'vue', 'css', 'html', 'javascript'],
            'backend': ['backend', 'back-end', 'api', 'server', 'database', 'microservices', 'rest'],
            'fullstack': ['fullstack', 'full-stack', 'full stack'],
            'data': ['data', 'analytics', 'machine learning', 'ml', 'ai', 'analysis', 'scientist'],
            'devops': ['devops', 'infrastructure', 'deployment', 'ci/cd', 'docker', 'kubernetes', 'aws'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter', 'app'],
            'web': ['web', 'website', 'application', 'development']
        }
        
        # Determine job focus
        job_focus = []
        for focus_type, keywords in role_keywords.items():
            if any(keyword in job_title or keyword in job_desc for keyword in keywords):
                job_focus.append(focus_type)
        
        # If we can't determine job focus, NO POINTS
        if not job_focus:
            role_focus.alignment_score = 0.0
            return
        
        # Check user interests alignment - ONLY reward actual matches
        user_interests = [interest.lower() for interest in role_focus.role_interests + role_focus.focus_areas]
        user_text = ' '.join(user_interests)
        
        alignment_count = 0
        total_checks = len(job_focus)
        
        for focus_type in job_focus:
            keywords = role_keywords[focus_type]
            # Check for exact keyword matches or partial matches
            if any(keyword in user_text or any(user_word in keyword for user_word in user_interests) 
                   for keyword in keywords):
                alignment_count += 1
        
        # Calculate alignment - NO PARTICIPATION POINTS
        if alignment_count > 0:
            role_focus.alignment_score = alignment_count / total_checks
        else:
            # NO POINTS for having unrelated role focus
            role_focus.alignment_score = 0.0

    def _validate_experience_level_alignment(self, experience: ExperienceLevelAlignment, job_req: Dict[str, Any]):
        """Validate experience level alignment (10% weight)"""
        if not experience.experience_level_claim or experience.confidence_level < 0.3:
            experience.alignment_score = 0.0
            return
        
        job_level = job_req.get('experience_level', 'mid')
        user_level = experience.experience_level_claim.lower()
        
        # Strict level compatibility matrix - NO PARTICIPATION POINTS
        level_scores = {
            ('junior', 'junior'): 1.0,
            ('junior', 'mid'): 0.6,     # Some points for junior applying to mid-level
            ('junior', 'senior'): 0.0,  # NO POINTS for junior applying to senior
            ('mid', 'junior'): 0.0,     # NO POINTS for overqualification
            ('mid', 'mid'): 1.0,
            ('mid', 'senior'): 0.5,     # Some points for mid applying to senior
            ('senior', 'junior'): 0.0,  # NO POINTS for overqualification
            ('senior', 'mid'): 0.0,     # NO POINTS for overqualification
            ('senior', 'senior'): 1.0,
            ('expert', 'senior'): 1.0,
            ('expert', 'mid'): 0.0,     # NO POINTS for overqualification
            ('expert', 'junior'): 0.0   # NO POINTS for overqualification
        }
        
        base_score = level_scores.get((user_level, job_level), 0.0)  # Default 0 instead of 0.6
        
        # Apply confidence multiplier
        experience.alignment_score = base_score * experience.confidence_level


def calculate_multi_dimensional_bonuses(analysis: MultiDimensionalAnalysis) -> Dict[str, float]:
    """Calculate weighted bonuses based on multi-dimensional alignment scores"""
    bonuses = {}
    
    # Technical Skills Alignment (40% weight, max 8 points)
    if analysis.technical.alignment_score > 0:
        bonuses['technical_alignment'] = analysis.technical.alignment_score * 8.0
    
    # Work Arrangement Alignment (20% weight, max 4 points)
    if analysis.work_arrangement.alignment_score > 0:
        bonuses['work_arrangement'] = analysis.work_arrangement.alignment_score * 4.0
    
    # Availability Alignment (15% weight, max 3 points)
    if analysis.availability.alignment_score > 0:
        bonuses['availability'] = analysis.availability.alignment_score * 3.0
    
    # Role Focus Alignment (15% weight, max 3 points)
    if analysis.role_focus.alignment_score > 0:
        bonuses['role_focus'] = analysis.role_focus.alignment_score * 3.0
    
    # Experience Level Alignment (10% weight, max 2 points)
    if analysis.experience_level.alignment_score > 0:
        bonuses['experience_level'] = analysis.experience_level.alignment_score * 2.0
    
    return bonuses


def generate_multi_dimensional_feedback(analysis: MultiDimensionalAnalysis, bonuses: Dict[str, float]) -> str:
    """Generate detailed feedback based on multi-dimensional analysis"""
    feedback_parts = []
    
    # Technical alignment feedback
    if analysis.technical.claimed_skills:
        tech_feedback = f"Technical Skills: {', '.join(analysis.technical.claimed_skills[:3])}"
        if analysis.technical.alignment_score > 0.7:
            tech_feedback += " (Strong match)"
        elif analysis.technical.alignment_score > 0.3:
            tech_feedback += " (Partial match)"
        else:
            tech_feedback += " (Limited match)"
        feedback_parts.append(tech_feedback)
    
    # Work arrangement feedback
    if analysis.work_arrangement.preferred_arrangement:
        work_feedback = f"Work Style: {analysis.work_arrangement.preferred_arrangement.title()}"
        if analysis.work_arrangement.alignment_score > 0.7:
            work_feedback += " (Aligned)"
        elif analysis.work_arrangement.alignment_score > 0:
            work_feedback += " (Compatible)"
        else:
            work_feedback += " (Misaligned)"
        feedback_parts.append(work_feedback)
    
    # Availability feedback
    if analysis.availability.availability_timeline:
        avail_feedback = f"Availability: {analysis.availability.availability_timeline.title()}"
        if analysis.availability.alignment_score > 0.7:
            avail_feedback += " (Excellent)"
        elif analysis.availability.alignment_score > 0.3:
            avail_feedback += " (Good)"
        feedback_parts.append(avail_feedback)
    
    # Role focus feedback
    if analysis.role_focus.role_interests:
        role_feedback = f"Focus Areas: {', '.join(analysis.role_focus.role_interests[:2])}"
        if analysis.role_focus.alignment_score > 0.7:
            role_feedback += " (Well aligned)"
        elif analysis.role_focus.alignment_score > 0.3:
            role_feedback += " (Somewhat aligned)"
        feedback_parts.append(role_feedback)
    
    # Experience level feedback
    if analysis.experience_level.experience_level_claim:
        exp_feedback = f"Experience Level: {analysis.experience_level.experience_level_claim.title()}"
        if analysis.experience_level.alignment_score > 0.7:
            exp_feedback += " (Good fit)"
        elif analysis.experience_level.alignment_score > 0.3:
            exp_feedback += " (Acceptable fit)"
        feedback_parts.append(exp_feedback)
    
    # Bonus summary
    total_bonus = sum(bonuses.values())
    if total_bonus > 0:
        feedback_parts.append(f"Total Alignment Bonus: +{total_bonus:.1f} points")
    
    if not feedback_parts:
        return "No specific claims found - consider adding technical skills, work preferences, or availability details"
    
    return " | ".join(feedback_parts)


def process_user_comments(comments: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user comments using multi-dimensional analysis and proper alignment validation"""
    if not comments or not comments.strip():
        return {
            "multi_dimensional_analysis": {},
            "alignment_scores": {},
            "scoring_adjustments": {},
            "structured_feedback": "No context provided",
            "total_bonus": 0
        }
    
    analyzer = GPTMultiDimensionalAnalyzer()
    analysis = analyzer.analyze_comments(comments, job_data)
    bonuses = calculate_multi_dimensional_bonuses(analysis)
    feedback = generate_multi_dimensional_feedback(analysis, bonuses)
    
    # Extract alignment scores
    alignment_scores = {
        'technical': analysis.technical.alignment_score,
        'work_arrangement': analysis.work_arrangement.alignment_score,
        'availability': analysis.availability.alignment_score,
        'role_focus': analysis.role_focus.alignment_score,
        'experience_level': analysis.experience_level.alignment_score
    }
    
    return {
        "multi_dimensional_analysis": asdict(analysis),
        "alignment_scores": alignment_scores,
        "scoring_adjustments": bonuses,
        "structured_feedback": feedback,
        "total_bonus": sum(bonuses.values())
    }