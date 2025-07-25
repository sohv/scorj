#!/usr/bin/env python3

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

try:
    from utils.job_parser import JobDescriptionParser
    from utils.scoring_engine_openai import ScoringEngine
    
    # Try to import resume parser, fallback if not available
    try:
        from utils.resume_parser import ResumeParser
        RESUME_PARSER_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Resume parser not available ({e}). Will use text-based resume input.")
        RESUME_PARSER_AVAILABLE = False
        ResumeParser = None
        
except ImportError as e:
    print(f"Error: Required modules not found: {e}")
    print("Please ensure you're in the correct directory and dependencies are installed.")
    sys.exit(1)

class ResumeEvaluationTester:
    def __init__(self):
        self.job_parser = JobDescriptionParser()
        if RESUME_PARSER_AVAILABLE:
            self.resume_parser = ResumeParser()
        else:
            self.resume_parser = None
        self.scoring_engine = ScoringEngine()
        
    def get_sample_resume_text(self) -> str:
        """Sample resume for testing purposes"""
        return """
JOHN SMITH
Software Engineer
Email: john.smith@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith

SUMMARY
Passionate software engineer with 3+ years of experience in full-stack development. 
Proficient in Python, JavaScript, React, and cloud technologies. Strong problem-solving 
skills and eager to learn new technologies.

EXPERIENCE

Software Developer | TechCorp Inc. | 2022 - Present
• Developed and maintained web applications using Python Django and React.js
• Collaborated with cross-functional teams to deliver features on time
• Implemented RESTful APIs and integrated with third-party services
• Optimized database queries resulting in 30% performance improvement
• Participated in code reviews and agile development processes

Junior Developer | StartupXYZ | 2021 - 2022
• Built responsive web interfaces using HTML, CSS, and JavaScript
• Worked with senior developers to learn best practices
• Assisted in debugging and testing applications
• Gained experience with Git version control and CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science | State University | 2017 - 2021
• Relevant Coursework: Data Structures, Algorithms, Software Engineering
• GPA: 3.7/4.0

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, Java, SQL
• Frameworks: Django, React.js, Node.js, Flask
• Databases: PostgreSQL, MySQL, MongoDB
• Tools: Git, Docker, AWS, Jenkins
• Other: RESTful APIs, Agile methodologies, Unit testing

PROJECTS
E-Commerce Platform (2023)
• Built a full-stack e-commerce application using Django and React
• Implemented user authentication, payment processing, and inventory management
• Deployed on AWS with Docker containerization

Personal Finance Tracker (2022)
• Developed a web app to track personal expenses and budgets
• Used Python for backend API and JavaScript for frontend
• Integrated with bank APIs for automatic transaction import
"""

    def parse_job_from_input(self) -> dict:
        """Get job data from user input (LinkedIn URL or text)"""
        print("\nChoose job input method:")
        print("1. LinkedIn URL")
        print("2. Job description text")
        print("3. Use sample job description")
        
        choice = input("\nEnter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            url = input("Enter LinkedIn job URL: ").strip()
            if url:
                print("Parsing LinkedIn job...")
                return self.job_parser.parse_linkedin_job(url)
            else:
                return self._get_sample_job()
                
        elif choice == "2":
            print("\nPaste job description (press Enter twice when done):")
            lines = []
            empty_count = 0
            while empty_count < 2:
                line = input()
                if line == "":
                    empty_count += 1
                else:
                    empty_count = 0
                lines.append(line)
            
            job_text = "\n".join(lines).strip()
            if job_text:
                print("Parsing job description...")
                return self.job_parser.parse_job_description_text(job_text)
            else:
                return self._get_sample_job()
        else:
            return self._get_sample_job()
    
    def _get_sample_job(self) -> dict:
        """Sample job description for testing"""
        sample_job_text = """
Senior Python Developer - Remote Opportunity
Company: TechInnovate Solutions
Location: Remote (US)

We're seeking an experienced Python developer to join our growing team!

Job Description:
We are looking for a skilled Python developer with 3-5 years of experience to work on exciting projects involving web development, API design, and data processing. This is a fully remote position with opportunities for professional growth.

Requirements:
- 3+ years of Python development experience
- Experience with Django or Flask frameworks
- Knowledge of React.js for frontend development
- Familiarity with Docker and AWS cloud services
- Strong problem-solving skills and attention to detail
- Experience with RESTful API development
- Understanding of database design (PostgreSQL preferred)
- Experience with Git and CI/CD pipelines

Responsibilities:
- Develop and maintain Python web applications
- Design and implement RESTful APIs
- Collaborate with frontend developers on React.js integration
- Work with cloud infrastructure on AWS
- Participate in code reviews and agile development
- Mentor junior developers

Benefits:
- Competitive salary ($80,000 - $120,000)
- Fully remote work environment
- Health insurance and 401k
- Professional development budget
- Flexible work hours
"""
        print("Using sample job description...")
        return self.job_parser.parse_job_description_text(sample_job_text)

    def get_resume_data(self) -> dict:
        """Get resume data from input or use sample"""
        print("\nResume Input:")
        if RESUME_PARSER_AVAILABLE:
            print("1. Upload resume file (PDF/DOCX)")
            print("2. Enter resume text")
            print("3. Use sample resume")
        else:
            print("1. Enter resume text")
            print("2. Use sample resume")
        
        choice = input(f"\nEnter choice: ").strip()
        
        if choice == "1" and RESUME_PARSER_AVAILABLE:
            file_path = input("Enter path to resume file: ").strip()
            if file_path and os.path.exists(file_path):
                print("Parsing resume file...")
                # Handle different file types
                if file_path.lower().endswith('.pdf'):
                    with open(file_path, 'rb') as f:
                        parsed_data = self.resume_parser.parse_pdf(f)
                elif file_path.lower().endswith('.docx'):
                    parsed_data = self.resume_parser.parse_docx(file_path)
                else:
                    print("Unsupported file type. Using sample resume...")
                    return self._get_sample_resume_data()
                
                # Convert parsed data to expected format
                return self._convert_parsed_resume_data(parsed_data)
            else:
                print("File not found. Using sample resume...")
                return self._get_sample_resume_data()
        elif choice == "1" and not RESUME_PARSER_AVAILABLE:
            return self._get_resume_text_input()
        elif choice == "2" and RESUME_PARSER_AVAILABLE:
            return self._get_resume_text_input()
        else:
            print("Using sample resume...")
            return self._get_sample_resume_data()

    def _get_resume_text_input(self) -> dict:
        """Get resume text from user input"""
        print("\nPaste resume text (press Enter twice when done):")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
            lines.append(line)
        
        resume_text = "\n".join(lines).strip()
        if resume_text:
            # Basic parsing of pasted text - create minimal structure
            return {
                'full_text': resume_text,  # Required for scoring engine
                'name': 'User Resume',
                'email': '',
                'phone': '',
                'experience': [],  # Empty list for user input - will be parsed from full_text
                'skills': [],     # Empty list for user input - will be parsed from full_text  
                'education': [],  # Empty list for user input - will be parsed from full_text
                'summary': resume_text[:200] + "..." if len(resume_text) > 200 else resume_text
            }
        else:
            print("No text provided. Using sample resume...")
            return self._get_sample_resume_data()

    def _convert_parsed_resume_data(self, parsed_data: dict) -> dict:
        """Convert resume parser output to expected format"""
        contact_info = parsed_data.get('contact_info', {})
        sections = parsed_data.get('sections', {})
        
        return {
            'full_text': parsed_data.get('full_text', ''),
            'name': contact_info.get('name', 'Unknown'),
            'email': contact_info.get('email', ''),
            'phone': contact_info.get('phone', ''),
            'experience': sections.get('experience', ''),
            'skills': parsed_data.get('extracted_skills', []),
            'education': sections.get('education', ''),
            'summary': sections.get('summary', '')
        }

    def _get_sample_resume_data(self) -> dict:
        """Parse sample resume text"""
        sample_text = self.get_sample_resume_text()
        # Simulate resume parsing output with proper structure
        return {
            'full_text': sample_text,  # This is required for the scoring engine
            'name': 'John Smith',
            'email': 'john.smith@email.com',
            'phone': '(555) 123-4567',
            'experience': [
                {
                    'title': 'Software Developer',
                    'company': 'TechCorp Inc.',
                    'duration': '2022 - Present',
                    'description': 'Developed and maintained web applications using Python Django and React.js. Collaborated with cross-functional teams to deliver features on time. Implemented RESTful APIs and integrated with third-party services.',
                    'technologies': ['Python', 'Django', 'React.js', 'RESTful APIs']
                },
                {
                    'title': 'Junior Developer',
                    'company': 'StartupXYZ',
                    'duration': '2021 - 2022',
                    'description': 'Built responsive web interfaces using HTML, CSS, and JavaScript. Worked with senior developers to learn best practices. Assisted in debugging and testing applications.',
                    'technologies': ['HTML', 'CSS', 'JavaScript', 'Git']
                }
            ],
            'skills': ['Python', 'JavaScript', 'React.js', 'Django', 'AWS', 'PostgreSQL', 'Docker', 'Node.js', 'Flask', 'Git'],
            'education': [
                {
                    'degree': 'Bachelor of Science',
                    'field': 'Computer Science',
                    'institution': 'State University',
                    'graduation_year': '2021',
                    'gpa': '3.7'
                }
            ],
            'summary': 'Passionate software engineer with 3+ years of experience in full-stack development. Proficient in Python, JavaScript, React, and cloud technologies.'
        }

    def run_evaluation(self) -> dict:
        """Run complete resume evaluation"""
        print("=" * 60)
        print("RESUME EVALUATION TESTER")
        print("=" * 60)
        
        # Get inputs
        job_data = self.parse_job_from_input()
        resume_data = self.get_resume_data()
        
        print("\n" + "=" * 60)
        print("RUNNING EVALUATION...")
        print("=" * 60)
        
        # Run scoring evaluation
        print("Evaluating resume against job requirements...")
        
        evaluation_result = self.scoring_engine.calculate_score(
            resume_data=resume_data,
            job_data=job_data
        )
        
        # Compile complete results
        complete_results = {
            "evaluation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "job_title": job_data.get('title', 'Unknown'),
                "candidate_name": resume_data.get('name', 'Unknown'),
                "evaluation_type": "test_run"
            },
            "job_data": job_data,
            "resume_data": {
                "name": resume_data.get('name'),
                "email": resume_data.get('email'),
                "skills_count": len(resume_data.get('skills', [])),
                "experience_count": len(resume_data.get('experience', [])),
                "has_summary": bool(resume_data.get('summary'))
            },
            "evaluation_results": evaluation_result,
            "summary": {
                "overall_score": evaluation_result.get('overall_score', 0),
                "key_strengths": evaluation_result.get('strengths', []),
                "improvement_areas": evaluation_result.get('weaknesses', [])
            }
        }
        
        return complete_results

    def save_results(self, results: dict) -> str:
        """Save results to JSON file"""
        # Create results directory if it doesn't exist
        results_dir = Path("evaluation_results")
        results_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_title_safe = results["evaluation_metadata"]["job_title"].replace(" ", "_").replace("/", "_")[:30]
        filename = f"resume_eval_{job_title_safe}_{timestamp}.json"
        filepath = results_dir / filename
        
        # Save results
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

    def display_summary(self, results: dict):
        """Display evaluation summary"""
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        
        summary = results["summary"]
        metadata = results["evaluation_metadata"]
        
        print(f"Job Title: {metadata['job_title']}")
        print(f"Candidate: {metadata['candidate_name']}")
        print(f"Evaluation Time: {metadata['timestamp']}")
        print("-" * 40)
        print(f"Overall Score: {summary['overall_score']:.1f}/100")
        print("-" * 40)
        
        if summary.get('key_strengths'):
            print("Key Strengths:")
            for strength in summary['key_strengths'][:3]:
                print(f"  • {strength}")
        
        if summary.get('improvement_areas'):
            print("\nImprovement Areas:")
            for area in summary['improvement_areas'][:3]:
                print(f"  • {area}")

def main():
    tester = ResumeEvaluationTester()
    results = tester.run_evaluation()
    
    # Display summary
    tester.display_summary(results)
    
    # Save results
    filepath = tester.save_results(results)
    print(f"\n✅ Results saved to: {filepath}")
    
    # Ask if user wants to view full JSON
    view_json = input("\nView full JSON results? (y/n): ").strip().lower()
    if view_json in ['y', 'yes']:
        print("\n" + "=" * 60)
        print("FULL RESULTS (JSON)")
        print("=" * 60)
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
