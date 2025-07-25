from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

@dataclass
class IntentAnalysis:
    # Core preferences
    work_preference_strength: float = 0.0  # 0-1 scale
    work_preference_type: str = ""
    availability_urgency: float = 0.0  # 0-1 scale
    availability_timeline: str = ""
    
    # Skills and growth
    technical_interests: List[str] = None  # Technologies mentioned
    learning_motivation: float = 0.0  # 0-1 scale
    learning_areas: List[str] = None
    experience_confidence: float = 0.0  # 0-1 scale
    
    # Company/role fit
    company_interest: float = 0.0  # Interest in specific company/mission
    role_motivation: float = 0.0  # Why they want this specific role
    culture_preferences: List[str] = None  # Team size, culture, values
    
    # Practical considerations
    salary_motivation: float = 0.0  # Compensation importance
    career_goals: List[str] = None  # Long-term aspirations
    relocation_flexibility: float = 0.0  # 0-1 scale
    
    # Any other strengths/motivations
    additional_strengths: List[str] = None
    additional_motivations: List[str] = None
    
    def __post_init__(self):
        if self.technical_interests is None:
            self.technical_interests = []
        if self.learning_areas is None:
            self.learning_areas = []
        if self.culture_preferences is None:
            self.culture_preferences = []
        if self.career_goals is None:
            self.career_goals = []
        if self.additional_strengths is None:
            self.additional_strengths = []
        if self.additional_motivations is None:
            self.additional_motivations = []

class GPTIntentAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    def analyze_intent(self, comments: str, job_data: Dict[str, Any]) -> IntentAnalysis:
        if not comments or not comments.strip():
            return IntentAnalysis()
        
        try:
            prompt = self._create_intent_prompt(comments, job_data)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at understanding candidate intentions and motivations from their comments."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._parse_gpt_response(result)
            
        except Exception as e:
            logger.error(f"GPT intent analysis failed: {e}")
            return IntentAnalysis()

    def _create_intent_prompt(self, comments: str, job_data: Dict[str, Any]) -> str:
        job_context = ""
        if job_data:
            job_title = job_data.get('title', '')
            job_desc = job_data.get('description', '')
            if job_title or job_desc:
                job_context = f"\n\nJob Context:\nTitle: {job_title}\nDescription: {job_desc[:300]}..."

        return f"""Analyze the candidate's free-form comments and extract ALL relevant information they mention. They can write about ANYTHING - work preferences, technology interests, salary expectations, company culture, career goals, availability, etc.

Rate each dimension on a 0-1 scale where:
- 0 = Not mentioned or no clear indication
- 0.3 = Briefly mentioned or weak indication
- 0.7 = Clearly stated or strong indication  
- 1.0 = Major focus or passionate emphasis

Candidate Comments: "{comments}"{job_context}

Extract and analyze everything they mention. Return JSON with:
{{
    "work_preference_strength": 0.0-1.0,
    "work_preference_type": "remote/hybrid/onsite/flexible/none",
    "availability_urgency": 0.0-1.0,
    "availability_timeline": "immediate/weeks/month/flexible/none",
    
    "technical_interests": ["python", "ai", "react"],
    "learning_motivation": 0.0-1.0,
    "learning_areas": ["machine learning", "devops"],
    "experience_confidence": 0.0-1.0,
    
    "company_interest": 0.0-1.0,
    "role_motivation": 0.0-1.0,
    "culture_preferences": ["small team", "startup", "collaborative"],
    
    "salary_motivation": 0.0-1.0,
    "career_goals": ["leadership", "technical expert"],
    "relocation_flexibility": 0.0-1.0,
    
    "additional_strengths": ["project management", "mentoring"],
    "additional_motivations": ["work-life balance", "innovation"]
}}

Extract EVERYTHING they mention - don't limit to specific categories. If they mention salary, benefits, company mission, team size, growth opportunities, specific technologies, work-life balance, etc. - capture it all."""

    def _parse_gpt_response(self, response: Dict) -> IntentAnalysis:
        return IntentAnalysis(
            work_preference_strength=float(response.get('work_preference_strength', 0)),
            work_preference_type=response.get('work_preference_type', ''),
            availability_urgency=float(response.get('availability_urgency', 0)),
            availability_timeline=response.get('availability_timeline', ''),
            
            technical_interests=response.get('technical_interests', []),
            learning_motivation=float(response.get('learning_motivation', 0)),
            learning_areas=response.get('learning_areas', []),
            experience_confidence=float(response.get('experience_confidence', 0)),
            
            company_interest=float(response.get('company_interest', 0)),
            role_motivation=float(response.get('role_motivation', 0)),
            culture_preferences=response.get('culture_preferences', []),
            
            salary_motivation=float(response.get('salary_motivation', 0)),
            career_goals=response.get('career_goals', []),
            relocation_flexibility=float(response.get('relocation_flexibility', 0)),
            
            additional_strengths=response.get('additional_strengths', []),
            additional_motivations=response.get('additional_motivations', [])
        )

def validate_comment_alignment(analysis: IntentAnalysis, job_data: Dict[str, Any]) -> bool:
    """Pre-validate if user comments align with job requirements before scoring"""
    job_desc = job_data.get('description', '').lower()
    job_title = job_data.get('title', '').lower()
    job_text = f"{job_desc} {job_title}"
    
    # Check work preference alignment
    if analysis.work_preference_strength > 0.5:
        pref_type = analysis.work_preference_type.lower()
        
        # If job mentions remote but user wants onsite - misaligned
        if 'remote' in job_text and pref_type in ['onsite', 'office', 'in-person']:
            return False
            
        # If job mentions onsite/office but user wants remote - misaligned  
        if any(word in job_text for word in ['office', 'onsite', 'on-site', 'in-person']) and pref_type == 'remote':
            return False
    
    # Check availability timeline alignment
    if analysis.availability_urgency > 0.5:
        timeline = analysis.availability_timeline.lower()
        
        # If job needs immediate start but user needs months - misaligned
        if any(word in job_text for word in ['urgent', 'immediate', 'asap', 'start immediately']) and timeline in ['month', 'months', 'later']:
            return False
    
    # Check technical interests vs job requirements
    if analysis.technical_interests:
        user_tech = [tech.lower() for tech in analysis.technical_interests]
        
        # If user mentions technologies that conflict with job stack
        for tech in user_tech:
            # Check if they mention competing technologies
            if 'python' in job_text and tech in ['java', 'c#', '.net'] and len(user_tech) == 1:
                # Only flag if they ONLY mention competing tech
                return False
            if 'react' in job_text and tech in ['vue', 'angular'] and len(user_tech) == 1:
                return False
    
    # Check learning vs required skills alignment
    if analysis.learning_motivation > 0.5 and analysis.learning_areas:
        user_areas = [area.lower() for area in analysis.learning_areas]
        
        # Check if user wants to learn technologies that are required
        if 'required' in job_text or 'must have' in job_text:
            for area in user_areas:
                if f"required {area}" in job_text or f"must have {area}" in job_text:
                    return False
    
    # Check salary expectations vs job level
    if analysis.salary_motivation > 0.8:
        # If user is very focused on salary but job is entry-level or non-profit
        if any(phrase in job_text for phrase in ['entry level', 'junior', 'internship', 'non-profit', 'volunteer']):
            return False
    
    # Check company culture preferences
    if analysis.culture_preferences:
        culture_prefs = [pref.lower() for pref in analysis.culture_preferences]
        
        # Check for culture mismatches
        if 'startup' in culture_prefs and any(word in job_text for word in ['enterprise', 'corporation', 'fortune 500']):
            return False
        if 'large company' in culture_prefs and any(word in job_text for word in ['startup', 'small team']):
            return False
    
    # Check relocation/location alignment  
    if analysis.relocation_flexibility > 0.5:
        # If job explicitly states "no relocation" or "local only" but user mentions relocation
        if any(phrase in job_text for phrase in ['no relocation', 'local only', 'must be local', 'local candidates only']):
            return False
    
    # Check experience confidence alignment
    if analysis.experience_confidence > 0:
        # If job requires senior/expert level but user seems uncertain about their experience
        if any(word in job_text for word in ['senior', 'expert', 'lead', 'principal']) and analysis.experience_confidence < 0.7:
            return False
        
        # If job is entry-level but user is overconfident
        if any(word in job_text for word in ['entry level', 'junior', 'graduate', 'intern']) and analysis.experience_confidence > 0.9:
            return False
    
    # If we get here, either no strong preferences stated or preferences align
    return True

def calculate_intent_bonuses(analysis: IntentAnalysis, job_data: Dict[str, Any]) -> Dict[str, float]:
    bonuses = {}
    
    # First validate alignment - if misaligned, return empty bonuses
    if not validate_comment_alignment(analysis, job_data):
        return bonuses
    
    job_desc = job_data.get('description', '').lower()
    job_title = job_data.get('title', '').lower()
    job_text = f"{job_desc} {job_title}"
    
    # Work preference alignment (max 5 points)
    if analysis.work_preference_strength > 0.5:
        pref_type = analysis.work_preference_type.lower()
        
        alignment_score = 0
        if pref_type == 'remote' and 'remote' in job_text:
            alignment_score = 1.0
        elif pref_type in ['onsite', 'office'] and any(word in job_text for word in ['office', 'onsite', 'on-site']):
            alignment_score = 1.0
        elif pref_type in ['hybrid', 'flexible']:
            alignment_score = 0.7
        
        if alignment_score > 0:
            bonuses['work_preference'] = analysis.work_preference_strength * alignment_score * 5
    
    # Technical interests alignment (max 6 points)
    if analysis.technical_interests:
        tech_bonus = 0
        for tech in analysis.technical_interests:
            if tech.lower() in job_text:
                tech_bonus += 1.5  # 1.5 points per matching technology
        bonuses['technical_match'] = min(6, tech_bonus)
    
    # Company/role motivation (max 4 points)
    if analysis.company_interest > 0.5 or analysis.role_motivation > 0.5:
        motivation_score = (analysis.company_interest + analysis.role_motivation) / 2
        bonuses['motivation'] = motivation_score * 4
    
    # Availability urgency (max 4 points)
    if analysis.availability_urgency > 0.5:
        urgency_bonus = analysis.availability_urgency * 4
        if analysis.availability_timeline == 'immediate':
            urgency_bonus *= 1.2
        bonuses['availability'] = min(4, urgency_bonus)
    
    # Learning motivation (max 3 points) - only if learning areas don't conflict
    if analysis.learning_motivation > 0.5:
        bonuses['learning'] = analysis.learning_motivation * 3
    
    # Career alignment (max 3 points)
    if analysis.career_goals:
        career_bonus = 0
        for goal in analysis.career_goals:
            if any(word in job_text for word in [goal.lower(), 'growth', 'advancement', 'leadership']):
                career_bonus += 1
        bonuses['career_fit'] = min(3, career_bonus)
    
    # Culture fit (max 2 points)
    if analysis.culture_preferences:
        culture_bonus = 0
        for pref in analysis.culture_preferences:
            if pref.lower() in job_text:
                culture_bonus += 0.7
        bonuses['culture_fit'] = min(2, culture_bonus)
    
    # Relocation flexibility (max 3 points)
    if analysis.relocation_flexibility > 0.5:
        location_mentioned = bool(job_data.get('location')) or 'location' in job_text
        if location_mentioned:
            bonuses['relocation'] = analysis.relocation_flexibility * 3
    
    # Experience confidence (max 2 points)
    if analysis.experience_confidence > 0.7:
        bonuses['confidence'] = analysis.experience_confidence * 2
    
    return bonuses

def generate_intent_feedback(analysis: IntentAnalysis, bonuses: Dict[str, float]) -> str:
    parts = []
    
    # Work preferences
    if analysis.work_preference_strength > 0.5:
        parts.append(f"Work Style: {analysis.work_preference_type.title()} preference")
    
    # Technical interests
    if analysis.technical_interests:
        tech_list = ', '.join(analysis.technical_interests[:3])  # Show top 3
        parts.append(f"Tech Interest: {tech_list}")
    
    # Availability
    if analysis.availability_urgency > 0.5:
        parts.append(f"Availability: {analysis.availability_timeline.title()} start")
    
    # Company/role motivation
    if analysis.company_interest > 0.5 or analysis.role_motivation > 0.5:
        parts.append("High motivation for role/company")
    
    # Learning and growth
    if analysis.learning_motivation > 0.5 and analysis.learning_areas:
        areas = ', '.join(analysis.learning_areas[:2])
        parts.append(f"Growth Focus: {areas}")
    
    # Career goals
    if analysis.career_goals:
        goals = ', '.join(analysis.career_goals[:2])
        parts.append(f"Career Goals: {goals}")
    
    # Culture preferences
    if analysis.culture_preferences:
        culture = ', '.join(analysis.culture_preferences[:2])
        parts.append(f"Culture Fit: {culture}")
    
    # Salary motivation (if high)
    if analysis.salary_motivation > 0.7:
        parts.append("Compensation-focused")
    
    # Geographic flexibility
    if analysis.relocation_flexibility > 0.5:
        parts.append("Geographic Flexibility: High")
    
    # Add bonus explanations
    bonus_parts = []
    total_bonus = sum(bonuses.values())
    
    if total_bonus > 0:
        for bonus_type, value in bonuses.items():
            if value > 0.5:
                bonus_parts.append(f"+{value:.1f}pts")
        
        if bonus_parts:
            parts.append(f"Intent Bonuses: {', '.join(bonus_parts)}")
    
    if not parts:
        return "No clear intentions detected - consider adding work preferences, technical interests, availability, or career motivations"
    
    return " | ".join(parts)

def process_user_comments(comments: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    if not comments or not comments.strip():
        return {
            "intent_analysis": {},
            "scoring_adjustments": {},
            "structured_feedback": "No context provided",
            "total_bonus": 0
        }
    
    analyzer = GPTIntentAnalyzer()
    analysis = analyzer.analyze_intent(comments, job_data)
    bonuses = calculate_intent_bonuses(analysis, job_data)
    feedback = generate_intent_feedback(analysis, bonuses)
    
    return {
        "intent_analysis": asdict(analysis),
        "scoring_adjustments": bonuses,
        "structured_feedback": feedback,
        "total_bonus": sum(bonuses.values())
    }