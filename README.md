# Scorj

A tool that scores resumes against job descriptions, providing detailed feedback and analytics on resume-job fit.

## Features

- Intelligent resume parsing from PDF and DOCX formats
- Advanced job description analysis and requirement extraction
- AI-powered resume scoring with comprehensive feedback
- Semantic skills matching using embeddings and fuzzy logic
- Modern React frontend with interactive user interface
- RESTful API backend built with FastAPI

## Project Structure

```
scorj/
├── backend/           
├── frontend/          
├── utils/             
├── tests/             
├── config.py         
├── requirements.txt  
└── Procfile           
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sohv/scorj.git
cd scorj
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Start the FastAPI backend:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at http://localhost:8000

### Start the React frontend:
```bash
cd frontend
npm install
npm start
```
The web interface will be available at http://localhost:3000

## Testing

Run the test suite:
```bash
python run_tests.py all
```

Available test commands:
- `unit` - Run unit tests only
- `integration` - Run integration tests
- `all` - Run all tests
- `coverage` - Run tests with coverage report

## Core Components

- **Resume Parser**: Extracts structured data from PDF/DOCX files
- **Job Parser**: Analyzes job descriptions and extracts requirements
- **Skills Matcher**: Uses embeddings and fuzzy matching for semantic skill analysis
- **Scoring Engine**: OpenAI-powered resume evaluation
- **Base Scoring Engine**: Structured analysis and scoring logic

## Workflow

1. **Resume Upload**: User uploads resume in PDF or DOCX format
2. **Resume Parsing**: Extract structured data including:
   - Contact information
   - Work experience with dates and descriptions
   - Education details
   - Skills and technologies
3. **Job Description Input**: User provides job description text or URL
4. **Job Analysis**: Parse job requirements including:
   - Required skills and technologies
   - Experience level expectations
   - Company and role information
5. **Skills Matching**: Compare resume skills against job requirements using semantic matching
6. **Scoring Analysis**: Generate comprehensive score using OpenAI GPT model
7. **Results Display**: Present detailed feedback with:
   - Overall score and dimension-specific scores
   - Matching and missing skills
   - Strengths and areas for improvement
   - Actionable recommendations

## Scoring Methodology

The scoring system uses a hybrid approach combining structured analysis with AI evaluation:

### Structured Analysis (Base Scoring Engine)
- **Skills Matching**: Semantic embedding comparison with fuzzy string matching
- **Experience Evaluation**: Years of experience vs job requirements
- **Education Assessment**: Degree level scoring (Bachelor's: 60, Master's: 80, PhD: 100)
- **Relevance Calculation**: Domain-specific experience weighting

### AI-Powered Evaluation (OpenAI Scoring Engine)
- **Contextual Analysis**: GPT-4o-mini evaluates resume content against job description
- **Qualitative Assessment**: Analyzes writing quality, achievements, and cultural fit
- **Comprehensive Scoring**: Generates scores across four dimensions:
  - Skills Score (40% weight)
  - Experience Score (25% weight)
  - Education Score (20% weight)
  - Domain Score (15% weight)

### Score Calculation
- Final score combines structured analysis with AI evaluation
- Results include confidence level and detailed breakdown
- Recommendations provided for skill gaps and improvements
- Transparency metrics show processing time and token usage

## What Makes Scorj Different

Unlike traditional resume reviewers that rely on keyword matching or basic templates, Scorj offers several unique advantages:

### Advanced AI Analysis
- **Contextual Understanding**: Uses OpenAI GPT-4o-mini for deep content analysis beyond simple keyword matching
- **Job-Specific Evaluation**: Scores resumes specifically against provided job descriptions rather than generic criteria
- **Qualitative Assessment**: Evaluates writing quality, achievement presentation, and cultural fit indicators

### Semantic Matching Technology
- **Embedding-Based Matching**: Uses sentence transformers to find semantically similar skills
- **Fuzzy String Matching**: Catches variations in skill names and terminology
- **Contextual Relevance**: Understands the importance of skills in the job context

### Technical Architecture
- **API-First Design**: REST API backend enables integration with other tools
- **Modern Stack**: FastAPI backend with React frontend for performance and usability
- **Comprehensive Testing**: Extensive test cases ensure reliability and accuracy

### User-Centric Features
- **Actionable Feedback**: Specific recommendations for improvement rather than just scores
- **Skills Gap Analysis**: Identifies missing skills with suggestions for development
- **Processing Transparency**: Shows analysis time and token usage for trust and debugging
- **Multiple Formats**: Supports both PDF and DOCX resume formats
- **Interactive Chat**: AI-powered chat assistant for resume and job-specific questions
