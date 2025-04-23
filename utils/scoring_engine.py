from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

class ScoringEngine:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Gemini Pro
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')

    def create_embeddings(self, text: str) -> np.ndarray:
        """Create embeddings for the given text."""
        return self.model.encode(text)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        embedding1 = self.create_embeddings(text1)
        embedding2 = self.create_embeddings(text2)
        return cosine_similarity([embedding1], [embedding2])[0][0]

    def calculate_score(self, resume_data: Dict, job_data: Dict) -> Tuple[float, Dict]:
        """Calculate the overall score and detailed feedback."""
        # Calculate different component scores
        skill_score = self._calculate_skill_score(resume_data, job_data)
        experience_score = self._calculate_experience_score(resume_data, job_data)
        education_score = self._calculate_education_score(resume_data, job_data)
        
        # Calculate semantic similarity scores
        semantic_scores = self._calculate_semantic_scores(resume_data, job_data)
        
        # Calculate overall score (weighted average)
        overall_score = (
            skill_score * 0.3 +
            experience_score * 0.3 +
            education_score * 0.2 +
            semantic_scores['overall'] * 0.2
        )

        # Generate detailed feedback using Gemini
        feedback = self._generate_feedback(resume_data, job_data, {
            'skill_score': skill_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'semantic_scores': semantic_scores
        })

        return overall_score, feedback

    def _calculate_semantic_scores(self, resume_data: Dict, job_data: Dict) -> Dict[str, float]:
        """Calculate semantic similarity scores for different sections."""
        scores = {}
        
        # Calculate similarity for each section
        for section in ['skills', 'experience', 'education']:
            resume_text = resume_data.get('sections', {}).get(section, '')
            job_text = job_data.get(section, '')
            if resume_text and job_text:
                scores[section] = self.calculate_similarity(resume_text, job_text)
            else:
                scores[section] = 0.0
        
        # Calculate overall semantic similarity
        resume_full = resume_data.get('full_text', '')
        job_full = job_data.get('description', '')
        scores['overall'] = self.calculate_similarity(resume_full, job_full)
        
        return scores

    def _calculate_skill_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate skill matching score using both exact and semantic matching."""
        resume_skills = set(resume_data.get('skills', []))
        job_skills = set(job_data.get('skills', []))

        if not job_skills:
            return 0.0

        # Calculate exact skill overlap
        matching_skills = resume_skills.intersection(job_skills)
        exact_match_score = len(matching_skills) / len(job_skills)

        # Calculate semantic similarity for skills
        resume_skills_text = ' '.join(resume_skills)
        job_skills_text = ' '.join(job_skills)
        semantic_score = self.calculate_similarity(resume_skills_text, job_skills_text)

        # Combine scores (70% exact match, 30% semantic)
        return 0.7 * exact_match_score + 0.3 * semantic_score

    def _calculate_experience_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate experience matching score using both structured and semantic matching."""
        job_level = job_data.get('experience_level', 'not specified')
        resume_experience = resume_data.get('experience', [])

        if not resume_experience:
            return 0.0

        # Calculate years of experience
        total_years = sum(self._extract_years(exp.get('date', '')) for exp in resume_experience)

        # Structured scoring based on experience level
        if job_level == 'entry':
            structured_score = min(total_years / 2, 1.0)
        elif job_level == 'mid':
            structured_score = min(total_years / 5, 1.0)
        elif job_level == 'senior':
            structured_score = min(total_years / 8, 1.0)
        else:
            structured_score = 0.5

        # Semantic scoring for experience descriptions
        experience_text = ' '.join([exp.get('description', '') for exp in resume_experience])
        job_description = job_data.get('description', '')
        semantic_score = self.calculate_similarity(experience_text, job_description)

        # Combine scores (60% structured, 40% semantic)
        return 0.6 * structured_score + 0.4 * semantic_score

    def _calculate_education_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate education matching score using both structured and semantic matching."""
        education = resume_data.get('education', [])
        if not education:
            return 0.0

        # Structured scoring based on highest degree
        highest_degree = max(education, key=lambda x: self._get_degree_level(x.get('degree', '')))
        structured_score = self._get_degree_level(highest_degree.get('degree', '')) / 4.0

        # Semantic scoring for education descriptions
        education_text = ' '.join([edu.get('description', '') for edu in education])
        job_description = job_data.get('description', '')
        semantic_score = self.calculate_similarity(education_text, job_description)

        # Combine scores (70% structured, 30% semantic)
        return 0.7 * structured_score + 0.3 * semantic_score

    def _generate_feedback(self, resume_data: Dict, job_data: Dict, scores: Dict) -> Dict:
        """Generate detailed feedback using Gemini."""
        prompt = f"""
        Analyze the following resume and job description match:
        
        Job Title: {job_data.get('title')}
        Company: {job_data.get('company')}
        
        Scores:
        - Skills Match: {scores['skill_score']:.2f}
        - Experience Match: {scores['experience_score']:.2f}
        - Education Match: {scores['education_score']:.2f}
        - Semantic Similarity: {scores['semantic_scores']['overall']:.2f}
        
        Provide specific feedback on:
        1. What skills are missing from the resume
        2. How to improve experience presentation
        3. Specific suggestions for improvement
        """

        response = self.gemini_model.generate_content(prompt)
        return {
            'missing_skills': self._extract_missing_skills(resume_data, job_data),
            'improvement_suggestions': response.text,
            'detailed_scores': scores
        }

    def _extract_years(self, date_str: str) -> float:
        """Extract years from date string."""
        try:
            return float(date_str.split('-')[0])
        except:
            return 0.0

    def _get_degree_level(self, degree: str) -> float:
        """Get numerical level for degree."""
        degree = degree.lower()
        if 'phd' in degree or 'doctorate' in degree:
            return 4.0
        elif 'master' in degree:
            return 3.0
        elif 'bachelor' in degree:
            return 2.0
        elif 'associate' in degree:
            return 1.0
        else:
            return 0.5

    def _extract_missing_skills(self, resume_data: Dict, job_data: Dict) -> List[str]:
        """Extract skills that are in job description but not in resume."""
        resume_skills = set(resume_data.get('skills', []))
        job_skills = set(job_data.get('skills', []))
        return list(job_skills - resume_skills)