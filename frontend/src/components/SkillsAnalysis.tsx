import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Target, TrendingUp } from 'lucide-react';
import type { ScoringResult } from '../types';

interface SkillsAnalysisProps {
  result: ScoringResult;
}

const SkillsAnalysis: React.FC<SkillsAnalysisProps> = ({ result }) => {
  const { feedback } = result;
  const skillsAnalysis = feedback.structured_analysis?.skills_analysis;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass-card rounded-2xl p-6"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center">
        <Target className="w-5 h-5 mr-2 text-tech-600" />
        Skills Analysis
      </h3>

      {skillsAnalysis && (
        <div className="mb-6 p-4 bg-tech-50 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-tech-700">Skills Match Rate</span>
            <span className="text-lg font-bold text-tech-800">
              {skillsAnalysis.match_percentage.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar h-2">
            <motion.div
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${skillsAnalysis.match_percentage}%` }}
              transition={{ duration: 1, delay: 0.5 }}
            />
          </div>
          <p className="text-xs text-tech-600 mt-2">
            {skillsAnalysis.total_matched} of {skillsAnalysis.total_job_skills} required skills matched
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Matching Skills */}
        <div>
          <h4 className="font-medium text-gray-700 mb-3 flex items-center">
            <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
            Matching Skills ({feedback.matching_skills?.length || 0})
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {feedback.matching_skills?.slice(0, 12).map((skill, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index }}
                className="flex items-center space-x-2 p-2 bg-green-50 rounded-lg"
              >
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-sm text-green-800 font-medium">{skill}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Missing Skills */}
        <div>
          <h4 className="font-medium text-gray-700 mb-3 flex items-center">
            <XCircle className="w-4 h-4 mr-2 text-red-600" />
            Missing Skills ({feedback.missing_skills?.length || 0})
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {feedback.missing_skills?.slice(0, 12).map((skill, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index }}
                className="flex items-center space-x-2 p-2 bg-red-50 rounded-lg"
              >
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-sm text-red-800">{skill}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Experience Analysis */}
      {feedback.structured_analysis?.experience_analysis && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="font-medium text-gray-700 mb-3 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2 text-tech-600" />
            Experience Analysis
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="p-3 bg-tech-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-tech-700">
                {feedback.structured_analysis.experience_analysis.total_years}
              </p>
              <p className="text-xs text-tech-600">Total Years</p>
            </div>
            <div className="p-3 bg-tech-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-tech-700">
                {feedback.structured_analysis.experience_analysis.relevant_years.toFixed(1)}
              </p>
              <p className="text-xs text-tech-600">Relevant Years</p>
            </div>
            <div className="p-3 bg-tech-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-tech-700">
                {feedback.structured_analysis.experience_analysis.relevance_score.toFixed(0)}%
              </p>
              <p className="text-xs text-tech-600">Relevance Score</p>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default SkillsAnalysis;