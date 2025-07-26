from typing import Dict, Any, List, Set, Tuple
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class SkillsProcessor:
    
    def __init__(self):
        # Common skill variations and aliases
        self.skill_aliases = {
            # Programming Languages
            'javascript': ['js', 'javascript', 'java script', 'ecmascript'],
            'python': ['python', 'python3', 'py'],
            'java': ['java', 'java8', 'java11', 'java17'],
            'c++': ['cpp', 'c++', 'c plus plus', 'cplusplus'],
            'c#': ['csharp', 'c#', 'c sharp', 'dotnet'],
            'typescript': ['ts', 'typescript', 'type script'],
            
            # Frameworks & Libraries
            'react': ['react', 'reactjs', 'react.js', 'react js'],
            'angular': ['angular', 'angularjs', 'angular.js', 'angular js'],
            'vue': ['vue', 'vuejs', 'vue.js', 'vue js'],
            'node': ['node', 'nodejs', 'node.js', 'node js'],
            'express': ['express', 'expressjs', 'express.js', 'express js'],
            'django': ['django', 'django framework'],
            'flask': ['flask', 'flask framework'],
            'fastapi': ['fastapi', 'fast api'],
            'spring': ['spring', 'spring boot', 'springboot'],
            'laravel': ['laravel', 'laravel framework'],
            
            # Databases
            'mysql': ['mysql', 'my sql'],
            'postgresql': ['postgresql', 'postgres', 'psql'],
            'mongodb': ['mongodb', 'mongo', 'mongo db'],
            'redis': ['redis', 'redis cache'],
            'sqlite': ['sqlite', 'sqlite3'],
            
            # Cloud & DevOps
            'aws': ['aws', 'amazon web services', 'amazon aws'],
            'azure': ['azure', 'microsoft azure', 'azure cloud'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            'docker': ['docker', 'docker containers', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s', 'k8', 'kube'],
            'jenkins': ['jenkins', 'jenkins ci'],
            'github': ['github', 'git hub'],
            'git': ['git', 'version control'],
            
            # Data & ML
            'pandas': ['pandas', 'pandas library'],
            'numpy': ['numpy', 'numpy library'],
            'tensorflow': ['tensorflow', 'tensor flow', 'tf'],
            'pytorch': ['pytorch', 'torch'],
            'scikit-learn': ['sklearn', 'scikit-learn', 'scikit learn'],
            'matplotlib': ['matplotlib', 'pyplot'],
            
            # Other
            'rest': ['rest', 'restful', 'rest api', 'restful api'],
            'graphql': ['graphql', 'graph ql'],
            'html': ['html', 'html5'],
            'css': ['css', 'css3'],
            'sql': ['sql', 'structured query language'],
        }
        
        # Build reverse lookup for normalization
        self.normalized_skills = {}
        for canonical, aliases in self.skill_aliases.items():
            for alias in aliases:
                self.normalized_skills[alias.lower()] = canonical
    
    def extract_skill_string(self, skill) -> str:
        """
        Extract skill string from various formats (string, dict with 'skill' key)
        """
        if isinstance(skill, dict):
            return skill.get('skill', '')
        return str(skill)
    
    def normalize_skill(self, skill) -> str:
        # Handle both string and dict formats using helper method
        skill_str = self.extract_skill_string(skill)
            
        skill_clean = re.sub(r'[^\w\s+#]', '', skill_str.lower().strip())
        skill_clean = re.sub(r'\s+', ' ', skill_clean)
        
        # Check direct mapping
        if skill_clean in self.normalized_skills:
            return self.normalized_skills[skill_clean]
        
        # Check for partial matches
        for normalized, canonical in self.normalized_skills.items():
            if skill_clean in normalized or normalized in skill_clean:
                return canonical
        
        return skill_clean
    
    def fuzzy_similarity(self, skill1: str, skill2: str) -> float:
        # Normalize both skills
        norm1 = self.normalize_skill(skill1)
        norm2 = self.normalize_skill(skill2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Additional checks for common patterns
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def match_skills(self, resume_skills, job_skills) -> Dict[str, Any]:
        """
        Enhanced skills matching with fuzzy matching and normalization
        Handles both string lists and dict lists (with 'skill' key)
        """
        if not resume_skills or not job_skills:
            return {
                'match_percentage': 0, 
                'matched_skills': [], 
                'missing_skills': job_skills,
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills)
            }
        
        # Convert skills to strings using helper method
        resume_skill_strings = [self.extract_skill_string(skill) for skill in resume_skills]
        job_skill_strings = [self.extract_skill_string(skill) for skill in job_skills]
        
        matched_skills = []
        missing_skills = []
        used_resume_skills = set()
        
        # Higher threshold for better precision
        FUZZY_THRESHOLD = 0.75
        
        for job_skill in job_skill_strings:
            best_match = None
            best_similarity = 0.0
            best_resume_skill = None
            
            for i, resume_skill in enumerate(resume_skill_strings):
                if i in used_resume_skills:
                    continue
                    
                similarity = self.fuzzy_similarity(job_skill, resume_skill)
                
                if similarity > best_similarity and similarity >= FUZZY_THRESHOLD:
                    best_similarity = similarity
                    best_match = resume_skill
                    best_resume_skill = i
            
            if best_match:
                matched_skills.append({
                    'job_skill': job_skill,
                    'resume_skill': best_match,
                    'similarity': float(best_similarity),
                    'match_type': 'exact' if best_similarity >= 0.95 else 'fuzzy'
                })
                used_resume_skills.add(best_resume_skill)
            else:
                missing_skills.append(job_skill)
        
        match_percentage = (len(matched_skills) / len(job_skill_strings)) * 100 if job_skill_strings else 0
        
        return {
            'match_percentage': match_percentage,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_job_skills': len(job_skill_strings),
            'total_resume_skills': len(resume_skill_strings),
            'matching_details': {
                'exact_matches': len([m for m in matched_skills if m['match_type'] == 'exact']),
                'fuzzy_matches': len([m for m in matched_skills if m['match_type'] == 'fuzzy']),
                'threshold_used': FUZZY_THRESHOLD
            }
        }
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        categories = {
            'programming_languages': [],
            'frameworks_libraries': [],
            'databases': [],
            'cloud_devops': [],
            'data_ml': [],
            'other': []
        }
        
        programming_langs = ['python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'php', 'ruby', 'go', 'rust']
        frameworks = ['react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'fastapi', 'spring']
        databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite']
        cloud_devops = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins']
        data_ml = ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn']
        
        for skill in skills:
            normalized = self.normalize_skill(skill)
            
            if normalized in programming_langs:
                categories['programming_languages'].append(skill)
            elif normalized in frameworks:
                categories['frameworks_libraries'].append(skill)
            elif normalized in databases:
                categories['databases'].append(skill)
            elif normalized in cloud_devops:
                categories['cloud_devops'].append(skill)
            elif normalized in data_ml:
                categories['data_ml'].append(skill)
            else:
                categories['other'].append(skill)
        
        return categories
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using pattern matching and known skill vocabulary
        This replaces the functionality from enhanced_skills_matcher.py
        """
        if not text:
            return []
        
        text_lower = text.lower()
        extracted_skills = []
        
        # Check against our known skills vocabulary
        all_known_skills = set()
        for canonical, aliases in self.skill_aliases.items():
            all_known_skills.add(canonical)
            all_known_skills.update(aliases)
        
        # Simple pattern matching for skills in text
        for skill in all_known_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Add the canonical form
                canonical = self.normalize_skill(skill)
                if canonical not in extracted_skills:
                    extracted_skills.append(canonical)
        
        # Additional common patterns
        programming_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            r'\b(html|css|sql|bash|shell|powershell)\b',
            r'\b(react|angular|vue|node|express|django|flask|spring)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch)\b'
        ]
        
        for pattern in programming_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                normalized = self.normalize_skill(match)
                if normalized not in extracted_skills:
                    extracted_skills.append(normalized)
        
        return extracted_skills
