import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Github, Star } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <motion.header 
      className="bg-white/80 backdrop-blur-md border-b border-white/20 sticky top-0 z-50"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <div className="relative">
              <div className="w-10 h-10 tech-gradient rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold tech-gradient-text">Scorj</h1>
              <p className="text-sm text-gray-500">AI Resume Analyzer</p>
            </div>
          </motion.div>

          <div className="flex items-center space-x-4">
            <motion.div 
              className="hidden md:flex items-center space-x-2 px-3 py-1 bg-tech-50 rounded-full"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
            >
              <Star className="w-4 h-4 text-tech-500" />
              <span className="text-sm font-medium text-tech-700">AI-Powered Analysis</span>
            </motion.div>
            
            <motion.a
              href="https://github.com/sohv/scorj"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <Github className="w-5 h-5 text-gray-600" />
            </motion.a>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;