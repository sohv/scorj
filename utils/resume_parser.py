import PyPDF2
from docx import Document
from typing import Dict, List, Optional
import re

class ResumeParser:
    def __init__(self):
        self.sections = {
            'education': r'(?i)(education|academic|qualification)',
            'experience': r'(?i)(experience|work|employment)',
            'skills': r'(?i)(skills|technical|competencies)',
            'projects': r'(?i)(projects|portfolio)',
            'certifications': r'(?i)(certifications|certificates)'
        }

    def parse_pdf(self, file) -> Dict[str, str]:
        """Extract text from PDF file and structure it into sections."""
        text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return self._structure_text(text)

    def parse_docx(self, file) -> Dict[str, str]:
        """Extract text from DOCX file and structure it into sections."""
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return self._structure_text(text)

    def _structure_text(self, text: str) -> Dict[str, str]:
        """Structure the extracted text into sections."""
        structured_text = {
            'full_text': text,
            'sections': {}
        }

        # Split text into lines
        lines = text.split('\n')
        current_section = 'other'
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line matches any section header
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

        # Add the last section
        if current_content:
            structured_text['sections'][current_section] = '\n'.join(current_content)

        return structured_text

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from the text using common patterns."""
        # Common skill patterns
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
        """Extract work experience entries from the text."""
        # This is a basic implementation. You might want to enhance it with more sophisticated parsing
        experience_entries = []
        lines = text.split('\n')
        
        current_entry = {}
        for line in lines:
            if re.search(r'(?i)(20\d{2}|19\d{2})', line):  # Year pattern
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