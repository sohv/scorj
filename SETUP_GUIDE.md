# ResumeRoast Setup Guide

## Prerequisites

1. **OpenAI API Key** - for document parsing and scoring.

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to the project directory
cd /Users/sohan/Documents/GitHub/resumeroast

# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Your `.env` file is already configured with:
```
API_URL=http://localhost:8000
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

make sure these API keys are valid and active.

### 3. Running the Backend (FastAPI)

```bash
# From the project root directory
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

**API Endpoints:**
- `GET /` - Health check
- `GET /test` - Test endpoint
- `POST /resume/score` - Score single resume against job description
- `POST /resume/compare` - Compare resume against multiple jobs

### 4. Running the Streamlit Frontend

```bash
# From the project root directory
cd streamlit_app
streamlit run app.py
```

The Streamlit app will be available at: `http://localhost:8501`

### 5. Testing the Setup

```bash
# Test OpenAI extraction (from project root)
python test_openai_extraction.py

# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/test
```

## Usage

### Using the Streamlit Interface

1. Open `http://localhost:8501` in your browser
2. Upload a resume (PDF or DOCX format)
3. Either:
   - Enter a LinkedIn job URL, or
   - Paste a job description directly
4. Click "Score Resume" to get analysis

### Using the API Directly

```bash
# Example API call to score a resume
curl -X POST "http://localhost:8000/resume/score" \
  -F "resume=@/path/to/your/resume.pdf" \
  -F "job_description=Your job description text here"
```

## Project Structure

```
resumeroast/
├── backend/           # FastAPI backend
│   ├── main.py       # Main API endpoints
│   └── auth.py       # Authentication (not yet integrated)
├── streamlit_app/    # Streamlit web interface
│   └── app.py        # Streamlit application
├── utils/            # Core processing modules
│   ├── resume_parser.py      # Resume parsing (now with OpenAI)
│   ├── job_parser.py         # Job description parsing
│   ├── scoring_engine.py     # Original scoring engine
│   └── scoring_engine_openai.py  # OpenAI-based scoring
└── requirements.txt  # Python dependencies
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you're in the virtual environment: `source venv/bin/activate`
   - Install requirements: `pip install -r requirements.txt`

2. **OpenAI API errors**
   - Check your API key is valid and has credits
   - Verify the key is properly set in `.env`

3. **Port already in use**
   - Change the port: `uvicorn main:app --reload --port 8001`
   - Or kill the process using the port

4. **LinkedIn parsing issues**
   - LinkedIn frequently changes their HTML structure
   - Try using the "Paste Job Description" option instead

### Development Mode

For development, run both services:

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Streamlit Frontend
cd streamlit_app
streamlit run app.py
```

To run the services in a single command, you can create a script:

```bash
# Make the script executable (only needed once)
chmod +x start_services.sh

# Run the script
./start_services.sh
```

## Next Steps

1. **Test the OpenAI extraction**: Run `python test_openai_extraction.py`
2. **Try the Streamlit interface**: Upload a resume and test scoring
3. **API Integration**: Test the API endpoints directly
4. **Custom Frontend**: Consider building a React/Vue.js frontend for better UX

## Notes

- The current setup uses OpenAI for resume and job parsing
- Fallback regex methods are available if OpenAI fails
- Both scoring engines are available (choose one in `main.py`)
- Authentication is implemented but not yet integrated into the main endpoints
