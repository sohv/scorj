from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

@dataclass
class IntentAnalysis:
    work_preference_strength: float = 0.0  # 0-1 scale
    work_preference_type: str = ""
    availability_urgency: float = 0.0  # 0-1 scale
    availability_timeline: str = ""
    learning_motivation: float = 0.0  # 0-1 scale
    learning_areas: List[str] = None
    relocation_flexibility: float = 0.0  # 0-1 scale
    experience_confidence: float = 0.0  # 0-1 scale
    additional_strengths: List[str] = None
    
    def __post_init__(self):
        if self.learning_areas is None:
            self.learning_areas = []
        if self.additional_strengths is None:
            self.additional_strengths = []

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
                job_context = f"\n\nJob Context:\nTitle: {job_title}\nDescription: {job_desc[:200]}..."

        return f"""Analyze the candidate's intentions and motivations from their comments. Rate each dimension on a 0-1 scale where:
- 0 = No clear intention/mention
- 0.3 = Weak/passive mention  
- 0.7 = Clear preference/intention
- 1.0 = Strong passion/commitment

Comments: "{comments}"{job_context}

Return JSON with:
{{
    "work_preference_strength": 0.0-1.0,
    "work_preference_type": "remote/hybrid/onsite/flexible/none",
    "availability_urgency": 0.0-1.0,
    "availability_timeline": "immediate/weeks/month/flexible/none", 
    "learning_motivation": 0.0-1.0,
    "learning_areas": ["area1", "area2"],
    "relocation_flexibility": 0.0-1.0,
    "experience_confidence": 0.0-1.0,
    "additional_strengths": ["strength1", "strength2"]
}}

Focus on genuine intent and passion, not just keyword mentions."""

    def _parse_gpt_response(self, response: Dict) -> IntentAnalysis:
        return IntentAnalysis(
            work_preference_strength=float(response.get('work_preference_strength', 0)),
            work_preference_type=response.get('work_preference_type', ''),
            availability_urgency=float(response.get('availability_urgency', 0)),
            availability_timeline=response.get('availability_timeline', ''),
            learning_motivation=float(response.get('learning_motivation', 0)),
            learning_areas=response.get('learning_areas', []),
            relocation_flexibility=float(response.get('relocation_flexibility', 0)),
            experience_confidence=float(response.get('experience_confidence', 0)),
            additional_strengths=response.get('additional_strengths', [])
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
        
        # If job mentions future start but user wants immediate - potentially misaligned
        if any(word in job_text for word in ['start in', 'begin in', 'starting']) and timeline == 'immediate':
            # This is less strict - immediate availability is usually good
            pass
    
    # Check learning/skills alignment
    if analysis.learning_motivation > 0.5 and analysis.learning_areas:
        user_areas = [area.lower() for area in analysis.learning_areas]
        
        # Check if user wants to learn technologies that conflict with job requirements
        # For example, if job requires Python expertise but user wants to learn Python (suggests they don't know it)
        required_skills = []
        if 'required' in job_text or 'must have' in job_text:
            # Extract skills mentioned as required
            for area in user_areas:
                if f"required {area}" in job_text or f"must have {area}" in job_text:
                    # User wants to learn something that's required (red flag)
                    return False
    
    # Check relocation/location alignment  
    if analysis.relocation_flexibility > 0.5:
        # If job explicitly states "no relocation" or "local only" but user mentions relocation
        if any(phrase in job_text for phrase in ['no relocation', 'local only', 'must be local', 'local candidates only']):
            return False
    
    # Check experience confidence alignment
    if analysis.experience_confidence > 0:  # Any expressed confidence level
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
    
    # Work preference alignment (max 5 points) - only award if aligned
    if analysis.work_preference_strength > 0.5:
        job_desc = job_data.get('description', '').lower()
        pref_type = analysis.work_preference_type.lower()
        
        alignment_score = 0
        if pref_type == 'remote' and 'remote' in job_desc:
            alignment_score = 1.0
        elif pref_type in ['onsite', 'office'] and any(word in job_desc for word in ['office', 'onsite', 'on-site']):
            alignment_score = 1.0
        elif pref_type in ['hybrid', 'flexible']:
            alignment_score = 0.7
        
        if alignment_score > 0:
            bonuses['work_preference'] = analysis.work_preference_strength * alignment_score * 5
    
    # Availability urgency (max 4 points)
    if analysis.availability_urgency > 0.5:
        urgency_bonus = analysis.availability_urgency * 4
        if analysis.availability_timeline == 'immediate':
            urgency_bonus *= 1.2
        bonuses['availability'] = min(4, urgency_bonus)
    
    # Learning motivation (max 3 points)
    if analysis.learning_motivation > 0.5:
        bonuses['learning'] = analysis.learning_motivation * 3
    
    # Relocation flexibility (max 3 points)
    if analysis.relocation_flexibility > 0.5:
        location_mentioned = bool(job_data.get('location'))
        if location_mentioned:
            bonuses['relocation'] = analysis.relocation_flexibility * 3
    
    # Experience confidence (max 2 points)
    if analysis.experience_confidence > 0.7:
        bonuses['confidence'] = analysis.experience_confidence * 2
    
    return bonuses

def generate_intent_feedback(analysis: IntentAnalysis, bonuses: Dict[str, float]) -> str:
    parts = []
    
    if analysis.work_preference_strength > 0.5:
        parts.append(f"Work Style: {analysis.work_preference_type.title()} preference")
    
    if analysis.availability_urgency > 0.5:
        parts.append(f"Availability: {analysis.availability_timeline.title()} start")
    
    if analysis.learning_motivation > 0.5 and analysis.learning_areas:
        areas = ', '.join(analysis.learning_areas[:2])
        parts.append(f"Growth Focus: {areas}")
    
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
        return "No clear intentions detected - consider adding work preferences, availability, or learning goals"
    
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