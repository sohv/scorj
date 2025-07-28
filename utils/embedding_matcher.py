from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class ModelSingleton:
    """Singleton to ensure model is loaded only once"""
    _instance: Optional['ModelSingleton'] = None
    _model: Optional[SentenceTransformer] = None
    _model_name: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self, model_name: str = "all-MiniLM-L6-v2") -> Optional[SentenceTransformer]:
        """Get model, loading it only if not already loaded or if different model requested"""
        if self._model is None or self._model_name != model_name:
            try:
                logger.info(f"Loading embedding model: {model_name}")
                self._model = SentenceTransformer(model_name)
                self._model_name = model_name
                logger.info(f"Successfully loaded embedding model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self._model = None
                self._model_name = None
        else:
            logger.debug(f"Reusing cached embedding model: {model_name}")
        
        return self._model

class EmbeddingSkillsMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a lightweight, fast sentence transformer model"""
        self.model_singleton = ModelSingleton()
        self.model_name = model_name
    
    @property
    def model(self) -> Optional[SentenceTransformer]:
        """Get the model from singleton"""
        return self.model_singleton.get_model(self.model_name)
    
    @classmethod
    def preload_model(cls, model_name: str = "all-MiniLM-L6-v2"):
        """Preload the model at application startup"""
        singleton = ModelSingleton()
        singleton.get_model(model_name)
        logger.info("Embedding model preloaded at startup")
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts"""
        if not self.model:
            return np.array([])
        
        # Clean and normalize texts
        cleaned_texts = [text.strip().lower() for text in texts if text.strip()]
        if not cleaned_texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(cleaned_texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])
    
    def calculate_semantic_similarity(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Calculate semantic similarity between resume and job skills"""
        if not resume_skills or not job_skills:
            return {
                'similarity_score': 0.0,
                'matched_skills': [],
                'skill_matches': [],
                'coverage_percentage': 0.0
            }
        
        # Get embeddings
        resume_embeddings = self.get_embeddings(resume_skills)
        job_embeddings = self.get_embeddings(job_skills)
        
        if resume_embeddings.size == 0 or job_embeddings.size == 0:
            return {
                'similarity_score': 0.0,
                'matched_skills': [],
                'skill_matches': [],
                'coverage_percentage': 0.0
            }
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(resume_embeddings, job_embeddings)
        
        # Find best matches for each job skill
        matched_skills = []
        skill_matches = []
        
        for j, job_skill in enumerate(job_skills):
            # Find best matching resume skill
            best_resume_idx = np.argmax(similarity_matrix[:, j])
            best_similarity = similarity_matrix[best_resume_idx, j]
            
            # Only consider it a match if similarity > threshold
            if best_similarity > 0.5:  # Adjust threshold as needed
                matched_skills.append(job_skill)
                skill_matches.append({
                    'job_skill': job_skill,
                    'resume_skill': resume_skills[best_resume_idx],
                    'similarity': float(best_similarity)
                })
        
        # Calculate overall metrics
        coverage_percentage = (len(matched_skills) / len(job_skills)) * 100
        overall_similarity = np.mean([match['similarity'] for match in skill_matches]) if skill_matches else 0.0
        
        return {
            'similarity_score': float(overall_similarity),
            'matched_skills': matched_skills,
            'skill_matches': skill_matches,
            'coverage_percentage': coverage_percentage,
            'total_job_skills': len(job_skills),
            'total_matched': len(matched_skills)
        }
    
    def calculate_experience_similarity(self, resume_experience: List[Dict], job_description: str) -> Dict[str, Any]:
        """Calculate semantic similarity between resume experience and job requirements"""
        if not resume_experience or not job_description:
            return {'similarity_score': 0.0, 'relevant_experiences': []}
        
        # Extract experience descriptions
        experience_texts = []
        for exp in resume_experience:
            exp_text = f"{exp.get('title', '')} {exp.get('description', '')}"
            experience_texts.append(exp_text)
        
        if not experience_texts:
            return {'similarity_score': 0.0, 'relevant_experiences': []}
        
        # Get embeddings
        exp_embeddings = self.get_embeddings(experience_texts)
        job_embedding = self.get_embeddings([job_description])
        
        if exp_embeddings.size == 0 or job_embedding.size == 0:
            return {'similarity_score': 0.0, 'relevant_experiences': []}
        
        # Calculate similarities
        similarities = cosine_similarity(exp_embeddings, job_embedding).flatten()
        
        # Find relevant experiences (similarity > threshold)
        relevant_experiences = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.4:  # Lower threshold for experience
                relevant_experiences.append({
                    'experience': resume_experience[i],
                    'similarity': float(similarity),
                    'index': i
                })
        
        # Sort by similarity
        relevant_experiences.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Calculate overall experience similarity
        overall_similarity = np.mean(similarities) if len(similarities) > 0 else 0.0
        
        return {
            'similarity_score': float(overall_similarity),
            'relevant_experiences': relevant_experiences,
            'total_experiences': len(resume_experience),
            'relevant_count': len(relevant_experiences)
        }
    
    def calculate_education_relevance(self, resume_education: List[Dict], job_description: str) -> Dict[str, Any]:
        """Calculate semantic relevance of education to job requirements"""
        if not resume_education or not job_description:
            return {'relevance_score': 0.0, 'relevant_education': []}
        
        # Extract education descriptions
        education_texts = []
        for edu in resume_education:
            edu_text = f"{edu.get('degree', '')} {edu.get('field', '')} {edu.get('school', '')}"
            education_texts.append(edu_text)
        
        if not education_texts:
            return {'relevance_score': 0.0, 'relevant_education': []}
        
        # Get embeddings
        edu_embeddings = self.get_embeddings(education_texts)
        job_embedding = self.get_embeddings([job_description])
        
        if edu_embeddings.size == 0 or job_embedding.size == 0:
            return {'relevance_score': 0.0, 'relevant_education': []}
        
        # Calculate similarities
        similarities = cosine_similarity(edu_embeddings, job_embedding).flatten()
        
        # Find most relevant education
        max_similarity = np.max(similarities) if len(similarities) > 0 else 0.0
        
        relevant_education = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.3:  # Education threshold
                relevant_education.append({
                    'education': resume_education[i],
                    'relevance': float(similarity),
                    'index': i
                })
        
        return {
            'relevance_score': float(max_similarity),
            'relevant_education': relevant_education,
            'total_education': len(resume_education)
        }