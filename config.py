import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class JobParserConfig:
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout: int = 15
    cache_enabled: bool = True
    cache_duration_hours: int = 24
    user_agents: List[str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ]


@dataclass
class ScoringConfig:
    # Model configurations
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-2.0-flash"
    
    # Scoring weights (must sum to 1.0)
    skills_weight: float = 0.35
    experience_weight: float = 0.30
    education_weight: float = 0.15
    domain_weight: float = 0.20
    
    # Scoring thresholds
    strong_match_threshold: int = 70
    good_match_threshold: int = 40
    
    # AI parameters
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout_seconds: int = 30
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.6
    
    def __post_init__(self):
        # Validate weights sum to 1.0
        total_weight = self.skills_weight + self.experience_weight + self.education_weight + self.domain_weight
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total_weight}")


@dataclass
class CacheConfig:
    base_dir: str = "cache"
    job_cache_dir: str = "job_descriptions"
    resume_cache_dir: str = "resumes"
    results_cache_dir: str = "scoring_results"
    max_cache_size_mb: int = 100
    cleanup_interval_hours: int = 168  # 1 week


@dataclass
class APIConfig:
    # Default values are set to None and should be provided via environment variables
    openai_api_key: str = None
    gemini_api_key: str = None
    max_requests_per_minute: int = 60
    
    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/resumeroast.log"
    max_file_size_mb: int = 10
    backup_count: int = 5


class ResumeRoastConfig:
    
    def __init__(self):
        self.job_parser = JobParserConfig()
        self.scoring = ScoringConfig()
        self.cache = CacheConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        directories = [
            self.cache.base_dir,
            f"{self.cache.base_dir}/{self.cache.job_cache_dir}",
            f"{self.cache.base_dir}/{self.cache.resume_cache_dir}",
            f"{self.cache.base_dir}/{self.cache.results_cache_dir}",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_api_keys(self) -> Dict[str, bool]:
        return {
            "openai": bool(self.api.openai_api_key),
            "gemini": bool(self.api.gemini_api_key)
        }
    
    def get_skills_taxonomy(self) -> Dict[str, List[str]]:
        return {
            "programming_languages": [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
                "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "HTML", "CSS"
            ],
            "web_frameworks": [
                "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "FastAPI",
                "Spring", "ASP.NET", "Ruby on Rails", "Laravel", "Next.js", "Nuxt.js"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server",
                "SQLite", "DynamoDB", "Cassandra", "Neo4j"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible",
                "Jenkins", "GitLab CI", "GitHub Actions"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
                "Scikit-learn", "Jupyter", "Apache Spark", "Hadoop", "Tableau", "Power BI"
            ],
            "mobile_development": [
                "iOS", "Android", "React Native", "Flutter", "Xamarin", "Swift", "Kotlin", "Ionic"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Problem Solving", "Team Collaboration", "Project Management",
                "Agile", "Scrum", "Critical Thinking", "Adaptability", "Time Management"
            ]
        }
    
    def get_experience_level_mapping(self) -> Dict[str, Dict]:
        return {
            "entry": {
                "years_range": (0, 2),
                "keywords": ["entry", "junior", "graduate", "trainee", "intern", "associate"],
                "typical_titles": ["Junior Developer", "Software Engineer I", "Associate"]
            },
            "mid": {
                "years_range": (3, 6),
                "keywords": ["mid", "intermediate", "software engineer", "developer"],
                "typical_titles": ["Software Engineer", "Developer", "Software Engineer II"]
            },
            "senior": {
                "years_range": (7, float('inf')),
                "keywords": ["senior", "lead", "principal", "architect", "manager", "director"],
                "typical_titles": ["Senior Developer", "Lead Engineer", "Principal Engineer", "Architect"]
            }
        }


# Global configuration instance
config = ResumeRoastConfig()
