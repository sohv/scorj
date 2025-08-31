import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import JobInput from './components/JobInput';
import UserComments from './components/UserComments';
import ScoringProgress from './components/ScoringProgress';
import ResultsDisplay from './components/ResultsDisplay';
import AIChat from './components/AIChat';
import type { ScoringResult, ScoringState, JobInput as JobInputType } from './types';

function App() {
  const [scoringState, setScoringState] = useState<ScoringState>('idle');
  const [scoringResult, setScoringResult] = useState<ScoringResult | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [jobInput, setJobInput] = useState<JobInputType>({ type: 'url' as const, value: '' });
  const [userComments, setUserComments] = useState('');
  const [progress, setProgress] = useState(0);

  const handleScoring = async () => {
    if (!uploadedFile || !jobInput.value) return;

    setScoringState('analyzing');
    setProgress(0);
    setScoringResult(null);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 15;
        });
      }, 500);

      const formData = new FormData();
      formData.append('resume', uploadedFile);
      
      if (jobInput.type === 'url') {
        formData.append('job_url', jobInput.value);
      } else {
        formData.append('job_description', jobInput.value);
      }
      
      if (userComments.trim()) {
        formData.append('user_comments', userComments);
      }

      const response = await fetch('http://localhost:8000/resume/score', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Scoring failed');
      }

      const result = await response.json();
      console.log('Scoring result received:', result);
      setScoringResult(result);
      setScoringState('completed');
      
    } catch (error) {
      console.error('Scoring error:', error);
      setScoringState('error');
      setProgress(0);
    }
  };

  const resetScoring = () => {
    setScoringState('idle');
    setScoringResult(null);
    setProgress(0);
  };

  const canScore = uploadedFile && jobInput.value && scoringState === 'idle';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <AnimatePresence mode="wait">
          {scoringState === 'idle' && (
            <motion.div
              key="input-form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              <div className="text-center mb-12">
                <motion.h1 
                  className="text-4xl md:text-5xl font-bold tech-gradient-text mb-4"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  Score Your Resume
                </motion.h1>
                <motion.p 
                  className="text-xl text-gray-600 max-w-2xl mx-auto"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  Get AI-powered insights on how well your resume matches job requirements
                </motion.p>
              </div>

              <div className="grid lg:grid-cols-2 gap-8">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <FileUpload 
                    onFileUpload={setUploadedFile}
                    uploadedFile={uploadedFile}
                  />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <JobInput 
                    jobInput={jobInput}
                    onJobInputChange={setJobInput}
                  />
                </motion.div>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <UserComments 
                  comments={userComments}
                  onCommentsChange={setUserComments}
                />
              </motion.div>

              <motion.div 
                className="flex justify-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                <button
                  onClick={handleScoring}
                  disabled={!canScore}
                  className={`
                    px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform
                    ${canScore 
                      ? 'tech-gradient text-white hover:scale-105 hover:shadow-tech-lg' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }
                  `}
                >
                  {canScore ? 'Analyze Resume' : 'Complete All Fields'}
                </button>
              </motion.div>
            </motion.div>
          )}

          {(scoringState === 'analyzing' || scoringState === 'error') && (
            <motion.div
              key="scoring-progress"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <ScoringProgress 
                progress={progress}
                state={scoringState}
                onReset={resetScoring}
              />
            </motion.div>
          )}

          {scoringState === 'completed' && scoringResult && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              <ResultsDisplay 
                result={scoringResult}
                onReset={resetScoring}
              />
              <AIChat 
                scoringResult={scoringResult}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;