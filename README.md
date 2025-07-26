# ResumeRoast

A resume scoring and analysis tool that evaluates resumes against job descriptions using OpenAI GPT models.

## Features

- Resume parsing from PDF and DOCX formats
- Job description analysis and skill extraction
- Intelligent resume scoring with detailed feedback
- Skills matching with fuzzy logic
- Web interface via Streamlit
- REST API backend with FastAPI

## Project Structure

```
resumeroast/
├── backend/           # FastAPI REST API server
├── streamlit_app/     # Streamlit web interface
├── utils/             # Core parsing and scoring modules
├── tests/             # Test suite
├── config.py          # Configuration management
└── requirements.txt   # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sohv/resumeroast.git
cd resumeroast
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
# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Start the FastAPI backend:
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at http://localhost:8000

### Start the Streamlit interface:
```bash
streamlit run streamlit_app/app.py
```
The web interface will be available at http://localhost:8501

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
- **Skills Matcher**: Fuzzy matching for technical skills
- **Scoring Engine**: OpenAI-powered resume evaluation
- **Base Scoring Engine**: Structured analysis and scoring logic

## Workflow

1. **Resume Upload**: User uploads resume in PDF or DOCX format
2. **Resume Parsing**: Extract structured data including:
   - Contact information
   - Work experience with dates and descriptions
   - Education details
   - Skills and technologies
3. **Job Description Input**: User provides job description text
4. **Job Analysis**: Parse job requirements including:
   - Required skills and technologies
   - Experience level expectations
   - Company and role information
5. **Skills Matching**: Compare resume skills against job requirements using fuzzy matching
6. **Scoring Analysis**: Generate comprehensive score using OpenAI GPT model
7. **Results Display**: Present detailed feedback with:
   - Overall score and breakdown
   - Matching and missing skills
   - Strengths and areas for improvement
   - Actionable recommendations

## Demo

Below is a demo of ResumeRoast in action:

![ResumeRoast Demo](/media/resumeroast.mp4)

## Scoring Methodology

The scoring system uses a hybrid approach combining structured analysis with AI evaluation:

### Structured Analysis (Base Scoring Engine)
- **Skills Matching**: Fuzzy string matching with 75% similarity threshold
- **Experience Evaluation**: Years of experience vs job requirements
- **Education Assessment**: Degree level scoring (Bachelor's: 60, Master's: 80, PhD: 100)
- **Relevance Calculation**: Domain-specific experience weighting

### AI-Powered Evaluation (OpenAI Scoring Engine)
- **Contextual Analysis**: GPT-4o-mini evaluates resume content against job description
- **Qualitative Assessment**: Analyzes writing quality, achievements, and cultural fit
- **Comprehensive Scoring**: Generates scores across four dimensions:
  - Skills Score (35% weight)
  - Experience Score (30% weight)
  - Education Score (15% weight)
  - Domain Score (20% weight)

### Score Calculation
- Final score combines structured analysis with AI evaluation
- Results include confidence level and detailed breakdown
- Recommendations provided for skill gaps and improvements
- Transparency metrics show processing time and token usage

## What Makes ResumeRoast Different

Unlike traditional resume reviewers that rely on keyword matching or basic templates, ResumeRoast offers several unique advantages:

### Advanced AI Analysis
- **Contextual Understanding**: Uses OpenAI GPT-4o-mini for deep content analysis beyond simple keyword matching
- **Job-Specific Evaluation**: Scores resumes specifically against provided job descriptions rather than generic criteria
- **Qualitative Assessment**: Evaluates writing quality, achievement presentation, and cultural fit indicators

### Hybrid Scoring Approach
- **Structured + AI Evaluation**: Combines rule-based scoring with AI insights for balanced assessment
- **Transparent Methodology**: Clear breakdown of scoring weights and confidence levels
- **Fuzzy Skills Matching**: 75% similarity threshold catches skill variations (e.g., "JavaScript" matches "JS")

### Technical Architecture
- **Open Source**: Full transparency with customizable scoring logic
- **API-First Design**: REST API backend enables integration with other tools
- **Modern Stack**: FastAPI backend with Streamlit frontend for performance and usability
- **Comprehensive Testing**: 28 test cases ensure reliability and accuracy

### User-Centric Features
- **Actionable Feedback**: Specific recommendations for improvement rather than just scores
- **Skills Gap Analysis**: Identifies missing skills with suggestions for development
- **Processing Transparency**: Shows analysis time and token usage for trust and debugging
- **Multiple Formats**: Supports both PDF and DOCX resume formats

### Smart Context Analysis
- **Structured Comments**: Automatically extracts work preferences, availability, and goals from user input
- **Bonus Scoring**: Up to 15+ bonus points for relevant context alignment
- **Preference Matching**: Work location, availability, and experience level matching
- **Learning Motivation**: Additional points for demonstrated learning goals and career growth mindset

## Requirements

- OpenAI API key
- Dependencies listed in requirements.txt
