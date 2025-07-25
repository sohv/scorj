import PyPDF2
from docx import Document
from typing import Dict, List, Optional
import re
import os
import json
from openai import OpenAI

class ResumeParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.sections = {
            'education': r'(?i)(education|academic|qualification)',
            'experience': r'(?i)(experience|work|employment)',
            'skills': r'(?i)(skills|technical|competencies)',
            'projects': r'(?i)(projects|portfolio)',
            'certifications': r'(?i)(certifications|certificates)'
        }

    def parse_pdf(self, file) -> Dict[str, str]:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return self._structure_text(text)

    def parse_docx(self, file) -> Dict[str, str]:
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return self._structure_text(text)

    def _structure_text(self, text: str) -> Dict[str, str]:
        try:
            prompt = f"""
            Analyze the following resume text and extract structured information. Return a JSON object with the following structure:
            {{
                "sections": {{
                    "education": "education section content",
                    "experience": "work experience section content", 
                    "skills": "skills section content",
                    "projects": "projects section content",
                    "certifications": "certifications section content"
                }},
                "skills": ["skill1", "skill2", "skill3"],
                "experience": [
                    {{
                        "title": "job title",
                        "company": "company name",
                        "date": "employment period",
                        "description": "job description"
                    }}
                ],
                "education": [
                    {{
                        "degree": "degree name",
                        "institution": "school name",
                        "date": "graduation date",
                        "description": "additional details"
                    }}
                ]
            }}
            
            Extract all relevant skills, including technical skills, programming languages, frameworks, tools, methodologies, and soft skills.
            For experience, extract job titles, companies, employment periods, and detailed descriptions.
            For education, extract degrees, institutions, graduation dates, and any relevant details.
            
            Resume text:
            {text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser that extracts structured information from resumes. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            
            structured_text = {
                'full_text': text,
                'sections': parsed_data.get('sections', {}),
                'skills': parsed_data.get('skills', []),
                'experience': parsed_data.get('experience', []),
                'education': parsed_data.get('education', [])
            }
            
            return structured_text
            
        except Exception as e:
            print(f"OpenAI parsing failed, falling back to regex: {e}")
            return self._structure_text_regex(text)

    def _structure_text_regex(self, text: str) -> Dict[str, str]:
        structured_text = {
            'full_text': text,
            'sections': {},
            'skills': [],
            'experience': [],
            'education': []
        }

        # split text into lines
        lines = text.split('\n')
        current_section = 'other'
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            section_found = False
            for section, pattern in self.sections.items():
                if re.search(pattern, line):
                    if current_section != 'other':
                        structured_text['sections'][current_section] = '\n'.join(current_content)
                    current_section = section
                    current_content = []
                    section_found = True
                    break

            if not section_found:
                current_content.append(line)

        if current_content:
            structured_text['sections'][current_section] = '\n'.join(current_content)

        return structured_text

    def extract_skills(self, text: str) -> List[str]:
        try:
            prompt = f"""
            Extract all skills from the following resume text. Include:
            - Programming languages
            - Frameworks and libraries
            - Tools and software
            - Technical skills
            - Methodologies (Agile, Scrum, etc.)
            - Certifications
            - Soft skills
            - Industry-specific skills
            
            Return a JSON array of skills as strings.
            
            Resume text:
            {text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting skills from resumes. Return only a JSON array of skill strings."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('skills', [])
            
        except Exception as e:
            print(f"OpenAI skill extraction failed, falling back to regex: {e}")
            return self._extract_skills_regex(text)

    def _extract_skills_regex(self, text: str) -> List[str]:
        skill_patterns = [
            r'(?i)(python|java|javascript|typescript|react|angular|vue|node\.js|express|django|flask|fastapi)',
            r'(?i)(aws|azure|gcp|cloud|docker|kubernetes|terraform)',
            r'(?i)(sql|mysql|postgresql|mongodb|redis|elasticsearch)',
            r'(?i)(machine learning|deep learning|ai|nlp|computer vision)',
            r'(?i)(agile|scrum|kanban|ci/cd|devops)'
        ]

        skills = set()
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                skills.add(match.group().lower())

        return list(skills)

    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        try:
            prompt = f"""
            Extract work experience from the following resume text. Return a JSON object with an "experience" array containing work experience entries.
            Each entry should have:
            - title: job title/position
            - company: company name
            - date: employment period (e.g., "2020-2023" or "Jan 2020 - Present")
            - description: job responsibilities and achievements
            
            Resume text:
            {text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting work experience from resumes. Return structured JSON data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('experience', [])
            
        except Exception as e:
            print(f"OpenAI experience extraction failed, falling back to regex: {e}")
            return self._extract_experience_regex(text)

    def _extract_experience_regex(self, text: str) -> List[Dict[str, str]]:
        experience_entries = []
        lines = text.split('\n')
        
        current_entry = {}
        for line in lines:
            if re.search(r'(?i)(20\d{2}|19\d{2})', line):
                if current_entry:
                    experience_entries.append(current_entry)
                current_entry = {'date': line.strip()}
            elif current_entry:
                if 'title' not in current_entry:
                    current_entry['title'] = line.strip()
                elif 'company' not in current_entry:
                    current_entry['company'] = line.strip()
                else:
                    if 'description' not in current_entry:
                        current_entry['description'] = []
                    current_entry['description'].append(line.strip())

        if current_entry:
            experience_entries.append(current_entry)

        return experience_entries