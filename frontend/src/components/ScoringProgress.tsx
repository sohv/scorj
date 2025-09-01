import React from 'react';
import { motion } from 'framer-motion';
import { Brain, AlertCircle, RotateCcw, CheckCircle, Clock } from 'lucide-react';
import type { ScoringState } from '../types';

interface ScoringProgressProps {
  progress: number;
  state: ScoringState;
  onReset: () => void;
}

const ScoringProgress: React.FC<ScoringProgressProps> = ({ progress, state, onReset }) => {
  const stages = [
    { name: 'Resume Parsing', threshold: 20 },
    { name: 'Job Analysis', threshold: 40 },
    { name: 'Skills Matching', threshold: 60 },
    { name: 'AI Evaluation', threshold: 80 },
    { name: 'Final Scoring', threshold: 100 }
  ];

  const getStageStatus = (threshold: number) => {
    if (progress >= threshold) return 'complete';
    if (progress >= threshold - 20) return 'active';
    return 'pending';
  };

  const getStageIcon = (status: string) => {
    if (status === 'complete') return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (status === 'active') return <Clock className="w-4 h-4 text-blue-500" />;
    return <div className="w-4 h-4 rounded-full bg-gray-300" />;
  };

  const getStageText = (status: string) => {
    if (status === 'complete') return 'Complete';
    if (status === 'active') return 'Processing...';
    return 'Pending';
  };

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card rounded-2xl p-8 text-center"
      >
        <div className="mb-6">
          <Brain className="w-8 h-8 text-tech-500 mx-auto" />
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-8">
          {state === 'error' ? 'Analysis Error' : 'AI Analysis in Progress'}
        </h2>

        {state === 'analyzing' && (
          <div className="space-y-4">
            {stages.map((stage, index) => {
              const status = getStageStatus(stage.threshold);
              const stageProgress = Math.max(0, Math.min(100, (progress - (stage.threshold - 20)) * 5));
              
              return (
                <div key={index} className="flex items-center space-x-4 text-left">
                  <div className="flex-shrink-0">
                    {getStageIcon(status)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{stage.name}</span>
                      <span className="text-xs text-gray-500">{getStageText(status)}</span>
                    </div>
                    
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${
                          status === 'complete' 
                            ? 'bg-green-500' 
                            : status === 'active' 
                              ? 'bg-blue-500' 
                              : 'bg-gray-300'
                        }`}
                        initial={{ width: 0 }}
                        animate={{ 
                          width: status === 'complete' 
                            ? '100%' 
                            : status === 'active' 
                              ? `${stageProgress}%` 
                              : '0%' 
                        }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {state === 'error' && (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2 text-red-600">
              <AlertCircle className="w-6 h-6" />
              <span>Something went wrong during the analysis</span>
            </div>
            
            <motion.button
              onClick={onReset}
              className="flex items-center space-x-2 mx-auto px-6 py-3 bg-tech-600 text-white rounded-lg hover:bg-tech-700 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RotateCcw className="w-4 h-4" />
              <span>Try Again</span>
            </motion.button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ScoringProgress;