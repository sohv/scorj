import React, { useState } from 'react';
import axios from 'axios';
import { FileUpload, JobInput, ResultsDisplay, LoadingSpinner, AIChat } from './components';
import './App.css';
import './components/AIChat.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ScoringResult {
  score: number;
  overall_score: number;
  confidence_level: string;
  summary: string;
  strengths: string[];
  concerns: string[];
  missing_skills: string[];
  matching_skills: string[];
  feedback: any;
  final_score: number;
}

function App() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobInputMethod, setJobInputMethod] = useState<'url' | 'text'>('url');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScoringResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScoreResume = async () => {
    if (!resumeFile || (!jobUrl && !jobDescription)) {
      setError('Please upload a resume and provide either a job URL or description');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      
      if (jobInputMethod === 'url' && jobUrl) {
        formData.append('job_url', jobUrl.trim());
      } else if (jobInputMethod === 'text' && jobDescription) {
        formData.append('job_description', jobDescription.trim());
      }

      const response = await axios.post(`${API_BASE_URL}/resume/score`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err: any) {
      console.error('Error scoring resume:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to analyze resume. Please check your inputs and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const canSubmit = resumeFile && (
    (jobInputMethod === 'url' && jobUrl.trim()) ||
    (jobInputMethod === 'text' && jobDescription.trim())
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>ResumeRoast</h1>
        <p>Analyze your resume against LinkedIn jobs</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <FileUpload 
            resumeFile={resumeFile}
            onFileSelect={setResumeFile}
          />
        </div>

        <div className="job-section">
          <JobInput
            jobInputMethod={jobInputMethod}
            jobUrl={jobUrl}
            jobDescription={jobDescription}
            onMethodChange={setJobInputMethod}
            onUrlChange={setJobUrl}
            onDescriptionChange={setJobDescription}
          />
        </div>

        <div className="submit-section">
          <button
            className={`score-button ${canSubmit ? 'enabled' : 'disabled'}`}
            onClick={handleScoreResume}
            disabled={!canSubmit || loading}
          >
            {loading ? 'Analyzing Resume...' : 'Score Resume'}
          </button>
        </div>

        {loading && <LoadingSpinner />}

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && <ResultsDisplay result={result} />}
        {result && <AIChat apiBaseUrl={API_BASE_URL} context={JSON.stringify(result)} />}
      </main>

      <footer className="App-footer">
        <p>Built with React + FastAPI | AI-powered resume analysis</p>
      </footer>
    </div>
  );
}

export default App;
