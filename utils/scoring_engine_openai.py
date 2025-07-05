import os
import json
from openai import OpenAI
from typing import Dict, Any, Tuple

# set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ScoringEngine:
    def __init__(self):
        self.model = "gpt-4o-mini"

    def _create_prompt(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        
        resume_text = resume_data.get('full_text', 'Not available')
        job_description = job_data.get('description', 'Not available')

        prompt = f"""
        Analyze the following resume and job description to determine a compatibility score from 0 to 100.
        Provide a detailed analysis in JSON format. The JSON output should include:
        1. "overall_score": A single integer score from 0 to 100.
        2. "summary": A brief one-sentence summary of the candidate's fit for the role.
        3. "strengths": A list of key strengths from the resume that align with the job description.
        4. "areas_for_improvement": A list of specific areas where the resume could be improved to better match the job.
        5. "missing_keywords": A list of important skills, technologies, or keywords from the job description that are missing from the resume. Only include skills that are explicitly mentioned in the job description.
        6. "matching_skills": A list of skills from the resume that directly match requirements in the job description.

        Focus on:
        - Technical skills and technologies mentioned in the job description
        - Experience levels and requirements
        - Domain knowledge and industry experience
        - Soft skills and qualifications
        - Specific tools, frameworks, and methodologies

        Be specific and avoid generic feedback. Only mention missing skills that are actually required in the job description.

        ---
        RESUME:
        {resume_text}
        ---
        JOB DESCRIPTION:
        {job_description}
        ---

        Return ONLY a valid JSON object with the specified keys.
        """
        return prompt

    def calculate_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Calculates the score and generates feedback using the OpenAI API.
        """
        prompt = self._create_prompt(resume_data, job_data)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume analyst and career coach."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
            )
            
            # Extract the JSON content from the response
            feedback_json = response.choices[0].message.content
            feedback = json.loads(feedback_json)

            # Extract the overall score
            score = feedback.get("overall_score", 0)

            return score, feedback

        except Exception as e:
            print(f"An error occurred while calling OpenAI API: {e}")
            return 0, {"error": "Could not generate score due to an API error.", "details": str(e)}