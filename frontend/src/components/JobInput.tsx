import React from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Link, FileText } from 'lucide-react';
import type { JobInput as JobInputType } from '../types';

interface JobInputProps {
  jobInput: JobInputType;
  onJobInputChange: (input: JobInputType) => void;
}

const JobInput: React.FC<JobInputProps> = ({ jobInput, onJobInputChange }) => {
  return (
    <div className="glass-card rounded-2xl p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <Briefcase className="w-5 h-5 mr-2 text-tech-600" />
        Job Information
      </h2>

      <div className="space-y-4">
        <div className="flex space-x-2">
          <motion.button
            onClick={() => onJobInputChange({ ...jobInput, type: 'url' })}
            className={`
              flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2
              ${jobInput.type === 'url'
                ? 'tech-gradient text-white shadow-tech'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Link className="w-4 h-4" />
            <span>LinkedIn URL</span>
          </motion.button>
          
          <motion.button
            onClick={() => onJobInputChange({ ...jobInput, type: 'text' })}
            className={`
              flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2
              ${jobInput.type === 'text'
                ? 'tech-gradient text-white shadow-tech'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <FileText className="w-4 h-4" />
            <span>Job Description</span>
          </motion.button>
        </div>

        <motion.div
          key={jobInput.type}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {jobInput.type === 'url' ? (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                LinkedIn Job URL
              </label>
              <input
                type="url"
                value={jobInput.value}
                onChange={(e) => onJobInputChange({ ...jobInput, value: e.target.value })}
                placeholder="https://www.linkedin.com/jobs/view/..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-tech-500 focus:border-transparent transition-all duration-200"
              />
              <p className="text-xs text-gray-500">
                Paste the LinkedIn job URL to automatically extract job details
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Job Description
              </label>
              <textarea
                value={jobInput.value}
                onChange={(e) => onJobInputChange({ ...jobInput, value: e.target.value })}
                placeholder="Paste the complete job description here..."
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-tech-500 focus:border-transparent transition-all duration-200 resize-none"
              />
              <p className="text-xs text-gray-500">
                Include requirements, responsibilities, and company information
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default JobInput;