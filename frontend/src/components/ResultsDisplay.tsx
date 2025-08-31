import React from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, Award, TrendingUp, AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react';
import type { ScoringResult } from '../types';
import ScoreVisualization from './ScoreVisualization';
import SkillsAnalysis from './SkillsAnalysis';
import RecommendationsPanel from './RecommendationsPanel';

interface ResultsDisplayProps {
  result: ScoringResult;
  onReset: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result, onReset }) => {
  const { feedback } = result;
  const finalScore = feedback.final_score || result.score;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    return 'Needs Improvement';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header with Score */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>
            <p className="text-gray-600">{result.job_title} at {result.company}</p>
          </div>
          <motion.button
            onClick={onReset}
            className="flex items-center space-x-2 px-4 py-2 text-tech-600 hover:bg-tech-50 rounded-lg transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RotateCcw className="w-4 h-4" />
            <span>New Analysis</span>
          </motion.button>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className={`p-6 rounded-xl border-2 ${getScoreBgColor(finalScore)}`}>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${getScoreColor(finalScore)} bg-white shadow-lg`}>
                  <span className="text-2xl font-bold">{finalScore}</span>
                </div>
                <div className="absolute -top-1 -right-1">
                  <Award className="w-6 h-6 text-yellow-500" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">{getScoreLabel(finalScore)}</h3>
                <p className="text-gray-600">Overall Score: {finalScore}/100</p>
                <p className="text-sm text-gray-500">Confidence: {feedback.confidence_level}</p>
              </div>
            </div>
          </div>

          {/* Intent Analysis */}
          {feedback.structured_comments?.total_bonus && feedback.structured_comments.total_bonus > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl"
            >
              <div className="flex items-center space-x-3">
                <Zap className="w-8 h-8 text-green-600" />
                <div>
                  <h3 className="font-bold text-green-800">Intent Bonus Applied</h3>
                  <p className="text-green-700">+{feedback.structured_comments.total_bonus.toFixed(1)} points</p>
                  <p className="text-sm text-green-600 mt-1">
                    {feedback.structured_comments.structured_feedback}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Processing Info */}
          {feedback.transparency && (
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Analysis Details</span>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <p>Processing Time: {feedback.transparency.processing_time_seconds}s</p>
                <p>Model: OpenAI GPT-4o-mini</p>
                <p>Method: {feedback.transparency.methodology}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Score Breakdown Visualization */}
      <ScoreVisualization result={result} />

      {/* Skills Analysis */}
      <SkillsAnalysis result={result} />

      {/* Key Insights */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Strengths */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
            Key Strengths
          </h3>
          <div className="space-y-3">
            {feedback.strengths?.slice(0, 5).map((strength, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg"
              >
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-green-800">{strength}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Concerns */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600" />
            Areas of Concern
          </h3>
          <div className="space-y-3">
            {feedback.concerns?.slice(0, 5).map((concern, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg"
              >
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-yellow-800">{concern}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Summary */}
      {feedback.summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-tech-600" />
            Executive Summary
          </h3>
          <p className="text-gray-700 leading-relaxed">{feedback.summary}</p>
        </motion.div>
      )}

      {/* Recommendations */}
      <RecommendationsPanel recommendations={feedback.recommendations || []} />
    </motion.div>
  );
};

export default ResultsDisplay;