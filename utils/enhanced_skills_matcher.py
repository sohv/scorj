"""
Enhanced Skills Matching System
Implements semantic similarity, taxonomy-based matching, and skill normalization
"""
import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import config


@dataclass
class SkillMatch:
    job_skill: str
    resume_skill: str
    similarity: float
    match_type: str  # 'exact', 'semantic', 'taxonomy', 'related'
    confidence: float


class EnhancedSkillsMatcher:
    """Advanced skills matching with semantic similarity and taxonomy"""
    
    def __init__(self):
        self.skills_taxonomy = config.get_skills_taxonomy()
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000,
            lowercase=True
        )
        
        # Build skill normalization mappings
        self.skill_normalizations = self._build_skill_normalizations()
        self.skill_aliases = self._build_skill_aliases()
        
    def _build_skill_normalizations(self) -> Dict[str, str]:
        """Build mappings for skill normalization"""
        normalizations = {}
        
        # Common variations and normalizations
        variations = {
            "javascript": ["js", "ecmascript", "es6", "es2015", "es2020"],
            "typescript": ["ts"],
            "python": ["python3", "python2", "py"],
            "machine learning": ["ml", "artificial intelligence", "ai"],
            "react.js": ["react", "reactjs"],
            "node.js": ["nodejs", "node"],
            "postgresql": ["postgres", "psql"],
            "mongodb": ["mongo"],
            "docker": ["containerization", "containers"],
            "kubernetes": ["k8s", "container orchestration"],
            "amazon web services": ["aws", "amazon cloud"],
            "google cloud platform": ["gcp", "google cloud"],
            "microsoft azure": ["azure"],
            "rest api": ["restful", "rest", "api development"],
            "graphql": ["graph ql"],
            "version control": ["git", "github", "gitlab", "bitbucket"],
            "agile methodology": ["agile", "scrum", "kanban"],
            "test driven development": ["tdd", "unit testing"],
            "continuous integration": ["ci/cd", "devops", "continuous deployment"],
            "artificial intelligence": ["ai", "machine learning", "ml"],
            "deep learning": ["neural networks", "dl"],
            "data analysis": ["data analytics", "data science"],
            "frontend": ["front-end", "client-side"],
            "backend": ["back-end", "server-side"],
            "fullstack": ["full-stack", "full stack"]
        }
        
        for canonical, aliases in variations.items():
            for alias in aliases:
                normalizations[alias.lower()] = canonical
                
        return normalizations
    
    def _build_skill_aliases(self) -> Dict[str, List[str]]:
        """Build skill aliases for better matching"""
        return {
            "programming": ["coding", "software development", "development"],
            "web development": ["frontend", "backend", "fullstack", "web programming"],
            "data science": ["data analysis", "analytics", "business intelligence"],
            "cloud computing": ["cloud services", "cloud infrastructure", "devops"],
            "mobile development": ["app development", "mobile apps", "mobile programming"],
            "database": ["data storage", "data management", "database administration"]
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to canonical form"""
        skill_lower = skill.lower().strip()
        
        # Remove common prefixes/suffixes
        skill_lower = re.sub(r'\b(experience\s+with|knowledge\s+of|proficient\s+in)\b', '', skill_lower)
        skill_lower = re.sub(r'\s+', ' ', skill_lower).strip()
        
        # Apply normalizations
        return self.skill_normalizations.get(skill_lower, skill_lower)
    
    def extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract skills from job description or resume text"""
        if not text:
            return set()
            
        text_lower = text.lower()
        extracted_skills = set()
        
        # Extract from all taxonomy categories
        for category, skills in self.skills_taxonomy.items():
            for skill in skills:
                skill_lower = skill.lower()
                # Look for exact matches and word boundaries
                if re.search(rf'\b{re.escape(skill_lower)}\b', text_lower):
                    extracted_skills.add(skill)
                    
        # Extract additional patterns
        skill_patterns = [
            r'\b\w+\.js\b',  # JavaScript frameworks
            r'\b\w+\s+framework\b',  # Frameworks
            r'\b\w+\s+language\b',  # Languages
            r'\b\w+\s+database\b',  # Databases
            r'\b\w+\s+platform\b',  # Platforms
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                extracted_skills.add(match.strip())
                
        return extracted_skills
    
    def calculate_semantic_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate semantic similarity between two skills"""
        try:
            # Normalize skills
            norm_skill1 = self.normalize_skill(skill1)
            norm_skill2 = self.normalize_skill(skill2)
            
            # Exact match after normalization
            if norm_skill1 == norm_skill2:
                return 1.0
                
            # TF-IDF similarity
            documents = [norm_skill1, norm_skill2]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            similarity = similarity_matrix[0, 1]
            
            # Boost similarity for related skills in same category
            category_bonus = self._get_category_bonus(norm_skill1, norm_skill2)
            similarity += category_bonus
            
            return min(1.0, similarity)
            
        except Exception:
            return 0.0
    
    def _get_category_bonus(self, skill1: str, skill2: str) -> float:
        """Give bonus for skills in the same category"""
        for category, skills in self.skills_taxonomy.items():
            skills_lower = [s.lower() for s in skills]
            if skill1.lower() in skills_lower and skill2.lower() in skills_lower:
                return 0.2  # 20% bonus for same category
        return 0.0
    
    def match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, any]:
        """Perform comprehensive skills matching"""
        if not resume_skills or not job_skills:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': job_skills,
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills),
                'confidence': 0.0
            }
        
        # Normalize all skills
        norm_resume_skills = [self.normalize_skill(skill) for skill in resume_skills]
        norm_job_skills = [self.normalize_skill(skill) for skill in job_skills]
        
        matched_skills = []
        missing_skills = []
        similarity_threshold = 0.7
        
        for job_skill in job_skills:
            norm_job_skill = self.normalize_skill(job_skill)
            best_match = None
            best_similarity = 0.0
            
            for resume_skill in resume_skills:
                norm_resume_skill = self.normalize_skill(resume_skill)
                similarity = self.calculate_semantic_similarity(norm_job_skill, norm_resume_skill)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = resume_skill
            
            if best_similarity >= similarity_threshold:
                match_type = self._determine_match_type(best_similarity)
                matched_skills.append(SkillMatch(
                    job_skill=job_skill,
                    resume_skill=best_match,
                    similarity=best_similarity,
                    match_type=match_type,
                    confidence=best_similarity
                ))
            else:
                missing_skills.append(job_skill)
        
        # Calculate metrics
        match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
        avg_confidence = np.mean([match.confidence for match in matched_skills]) if matched_skills else 0
        
        return {
            'match_percentage': round(match_percentage, 1),
            'matched_skills': [
                {
                    'job_skill': match.job_skill,
                    'resume_skill': match.resume_skill,
                    'similarity': round(match.similarity, 2),
                    'match_type': match.match_type
                } for match in matched_skills
            ],
            'missing_skills': missing_skills,
            'total_job_skills': len(job_skills),
            'total_resume_skills': len(resume_skills),
            'confidence': round(avg_confidence, 2),
            'skill_categories_analysis': self._analyze_skill_categories(matched_skills, missing_skills)
        }
    
    def _determine_match_type(self, similarity: float) -> str:
        """Determine the type of skill match based on similarity"""
        if similarity >= 0.95:
            return 'exact'
        elif similarity >= 0.85:
            return 'semantic'
        elif similarity >= 0.75:
            return 'taxonomy'
        else:
            return 'related'
    
    def _analyze_skill_categories(self, matched_skills: List[SkillMatch], missing_skills: List[str]) -> Dict[str, any]:
        """Analyze skills by category for better insights"""
        category_analysis = {}
        
        for category, category_skills in self.skills_taxonomy.items():
            category_skills_lower = [s.lower() for s in category_skills]
            
            matched_in_category = [
                match for match in matched_skills 
                if self.normalize_skill(match.job_skill).lower() in category_skills_lower
            ]
            
            missing_in_category = [
                skill for skill in missing_skills 
                if self.normalize_skill(skill).lower() in category_skills_lower
            ]
            
            total_in_category = len(matched_in_category) + len(missing_in_category)
            
            if total_in_category > 0:
                category_analysis[category] = {
                    'matched_count': len(matched_in_category),
                    'missing_count': len(missing_in_category),
                    'match_percentage': (len(matched_in_category) / total_in_category) * 100,
                    'strength': self._categorize_strength(len(matched_in_category), total_in_category)
                }
        
        return category_analysis
    
    def _categorize_strength(self, matched: int, total: int) -> str:
        """Categorize strength level for a skill category"""
        if total == 0:
            return 'not_required'
        
        percentage = (matched / total) * 100
        
        if percentage >= 80:
            return 'strong'
        elif percentage >= 60:
            return 'good'
        elif percentage >= 40:
            return 'moderate'
        else:
            return 'weak'
    
    def get_skill_recommendations(self, missing_skills: List[str], matched_skills: List[dict]) -> List[str]:
        """Generate skill improvement recommendations"""
        recommendations = []
        
        # Prioritize missing skills by category importance
        critical_categories = ['programming_languages', 'web_frameworks', 'databases']
        important_categories = ['cloud_platforms', 'data_science']
        
        for category in critical_categories:
            category_skills = [s.lower() for s in self.skills_taxonomy.get(category, [])]
            critical_missing = [
                skill for skill in missing_skills 
                if self.normalize_skill(skill).lower() in category_skills
            ]
            
            if critical_missing:
                recommendations.append(f"Priority: Develop {', '.join(critical_missing[:3])} skills")
        
        # Add learning path recommendations
        if any('react' in skill.lower() for skill in missing_skills):
            recommendations.append("Consider learning React.js ecosystem (Redux, Next.js)")
        
        if any('cloud' in skill.lower() for skill in missing_skills):
            recommendations.append("Gain cloud platform experience (AWS, Azure, or GCP)")
        
        return recommendations[:5]  # Limit to top 5 recommendations


# Global skills matcher instance
skills_matcher = EnhancedSkillsMatcher()
