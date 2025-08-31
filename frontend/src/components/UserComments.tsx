import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';

interface UserCommentsProps {
  comments: string;
  onCommentsChange: (comments: string) => void;
}

const UserComments: React.FC<UserCommentsProps> = ({ comments, onCommentsChange }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const exampleComments = [
    "I'm passionate about machine learning and excited to contribute to AI innovation",
    "I thrive in remote environments and have a proven track record of self-management",
    "Ready to start immediately and looking to grow my technical leadership skills",
    "Willing to relocate to San Francisco for the right growth opportunity",
    "I love collaborative problem-solving and mentoring junior developers"
  ];

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800 flex items-center">
          <MessageSquare className="w-5 h-5 mr-2 text-tech-600" />
          Additional Context
          <span className="ml-2 px-2 py-1 bg-tech-100 text-tech-700 text-xs rounded-full font-medium">
            +15 pts possible
          </span>
        </h2>
        
        <motion.button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-1 text-tech-600 hover:text-tech-700 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Lightbulb className="w-4 h-4" />
          <span className="text-sm font-medium">Tips</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </motion.button>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-4 p-4 bg-tech-50 rounded-xl border border-tech-100"
          >
            <h3 className="font-medium text-tech-800 mb-2">How AI analyzes your intentions:</h3>
            <div className="space-y-2 text-sm text-tech-700">
              <p><strong>Work Style:</strong> "I thrive in remote environments" → remote preference bonus</p>
              <p><strong>Availability:</strong> "I'm excited to start immediately" → urgency alignment bonus</p>
              <p><strong>Technical Confidence:</strong> "I have extensive experience with Python" → skill confidence boost</p>
              <p><strong>Career Goals:</strong> "Looking to grow in AI/ML" → motivation and learning bonus</p>
            </div>
            
            <div className="mt-3 pt-3 border-t border-tech-200">
              <p className="text-xs text-tech-600 font-medium">Example comments:</p>
              <div className="mt-2 space-y-1">
                {exampleComments.slice(0, 3).map((example, index) => (
                  <p key={index} className="text-xs text-tech-600 italic">• {example}</p>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Describe your motivations, preferences, and career goals
        </label>
        <textarea
          value={comments}
          onChange={(e) => onCommentsChange(e.target.value)}
          placeholder="Share your genuine motivations and preferences to get personalized bonus points..."
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-tech-500 focus:border-transparent transition-all duration-200 resize-none"
        />
        <div className="flex justify-between items-center">
          <p className="text-xs text-gray-500">
            Our AI analyzes genuine intent and motivation for context-aware scoring
          </p>
          <span className={`text-xs ${comments.length > 50 ? 'text-green-600' : 'text-gray-400'}`}>
            {comments.length} characters
          </span>
        </div>
      </div>
    </div>
  );
};

export default UserComments;