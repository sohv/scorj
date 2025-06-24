# ResumeRoast

A smart resume scoring tool that evaluates your resume against LinkedIn job descriptions using advanced AI techniques. 

> WORK CURRENTLY IN PROGRESS

## Features

- Resume scoring against job descriptions
- Support for PDF and DOCX resume formats
- Detailed feedback and improvement suggestions
- Multiple job description comparison
- User authentication and profile management
- Multiple interfaces (Web, Streamlit, Gradio)

## Project Structure

```
resumeroast/
├── backend/
├── frontend/
├── streamlit_app/
├── gradio_app/
├── utils/
└── tests/
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start

# Streamlit
cd streamlit_app
streamlit run app.py

# Gradio
cd gradio_app
python app.py
```

## Architecture

The project uses a hybrid approach combining:
- Semantic Embedding with Cosine Similarity for primary matching
- Structured Rule-Based Matching for field-specific scoring
- Knowledge Graph for relationship mapping
- Gemini Pro for advanced analysis and suggestions

Create a `.env` file in the root directory:
```
API_URL=http://localhost:8000
OPENAI_API_KEY=your-openai-api-key-here
```

4. **Start the Backend Server**:
