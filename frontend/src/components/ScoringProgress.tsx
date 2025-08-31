import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, AlertCircle, RotateCcw } from 'lucide-react';
import { ScoringState } from '../types';

interface ScoringProgressProps {
  progress: number;
  state: ScoringState;
  onReset: () => void;
}

const ScoringProgress: React.FC<ScoringProgressProps> = ({ progress, state, onReset }) => {
  const getProgressMessage = () => {
    if (state === 'error') return 'Analysis failed';
    if (progress < 20) return 'Parsing resume...';
    if (progress < 40) return 'Analyzing job requirements...';
    if (progress < 60) return 'Matching skills and experience...';
    if (progress < 80) return 'AI evaluation in progress...';
    if (progress < 95) return 'Generating insights...';
    return 'Finalizing results...';
  };

  const getIcon = () => {
    if (state === 'error') return <AlertCircle className="w-8 h-8 text-red-500" />;
    return <Brain className="w-8 h-8 text-tech-500" />;
  };

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card rounded-2xl p-8 text-center"
      >
        <motion.div
          animate={state === 'analyzing' ? { rotate: 360 } : {}}
          transition={{ duration: 2, repeat: state === 'analyzing' ? Infinity : 0, ease: "linear" }}
          className="mb-6"
        >
          {getIcon()}
        </motion.div>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          {state === 'error' ? 'Analysis Error' : 'AI Analysis in Progress'}
        </h2>
        
        <p className="text-gray-600 mb-6">
          {state === 'error' 
            ? 'Something went wrong during the analysis. Please try again.'
            : getProgressMessage()
          }
        </p>

        {state === 'analyzing' && (
          <div className="space-y-4">
            <div className="progress-bar h-3">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>
            
            <div className="flex justify-between text-sm text-gray-500">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>

            <div className="flex justify-center space-x-6 mt-6">
              <motion.div
                animate={{ opacity: progress > 20 ? 1 : 0.3 }}
                className="flex items-center space-x-2"
              >
                <div className={`w-3 h-3 rounded-full ${progress > 20 ? 'bg-tech-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-600">Parse</span>
              </motion.div>
              
              <motion.div
                animate={{ opacity: progress > 50 ? 1 : 0.3 }}
                className="flex items-center space-x-2"
              >
                <div className={`w-3 h-3 rounded-full ${progress > 50 ? 'bg-tech-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-600">Match</span>
              </motion.div>
              
              <motion.div
                animate={{ opacity: progress > 80 ? 1 : 0.3 }}
                className="flex items-center space-x-2"
              >
                <div className={`w-3 h-3 rounded-full ${progress > 80 ? 'bg-tech-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-600">Score</span>
              </motion.div>
            </div>
          </div>
        )}

        {state === 'error' && (
          <motion.button
            onClick={onReset}
            className="flex items-center space-x-2 mx-auto px-6 py-3 bg-tech-600 text-white rounded-lg hover:bg-tech-700 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RotateCcw className="w-4 h-4" />
            <span>Try Again</span>
          </motion.button>
        )}
      </motion.div>
    </div>
  );
};

export default ScoringProgress;