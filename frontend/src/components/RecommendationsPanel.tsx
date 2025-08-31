import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, ArrowRight } from 'lucide-react';

interface RecommendationsPanelProps {
  recommendations: string[];
}

const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="glass-card rounded-2xl p-6"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center">
        <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
        Improvement Recommendations
      </h3>

      <div className="space-y-4">
        {recommendations.slice(0, 6).map((recommendation, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index }}
            className="group flex items-start space-x-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl hover:from-yellow-100 hover:to-orange-100 transition-all duration-300 cursor-pointer"
          >
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
              {index + 1}
            </div>
            <div className="flex-1">
              <p className="text-gray-800 leading-relaxed">{recommendation}</p>
            </div>
            <ArrowRight className="w-5 h-5 text-yellow-600 opacity-0 group-hover:opacity-100 transition-opacity" />
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-6 p-4 bg-tech-50 rounded-xl border border-tech-200"
      >
        <p className="text-sm text-tech-700 font-medium mb-2">💡 Pro Tip:</p>
        <p className="text-sm text-tech-600">
          Focus on the top 3 recommendations for maximum impact on your next application. 
          Consider updating your resume and re-analyzing to track improvements.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default RecommendationsPanel;