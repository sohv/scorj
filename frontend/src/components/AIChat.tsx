import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, Bot, User, Sparkles } from 'lucide-react';
import { ScoringResult, ChatMessage } from '../types';

interface AIChatProps {
  scoringResult: ScoringResult;
}

const AIChat: React.FC<AIChatProps> = ({ scoringResult }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!currentQuestion.trim() || isLoading) return;

    const question = currentQuestion.trim();
    setCurrentQuestion('');
    setIsLoading(true);

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      question,
      answer: '',
      timestamp: new Date().toLocaleTimeString(),
      model: 'user'
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Create context from scoring results
      const context = `
        Recent resume scoring results:
        - Overall Score: ${scoringResult.feedback.final_score}/100
        - Job Title: ${scoringResult.job_title}
        - Company: ${scoringResult.company}
        - Key Strengths: ${scoringResult.feedback.strengths?.slice(0, 3).join(', ')}
        - Main Concerns: ${scoringResult.feedback.concerns?.slice(0, 3).join(', ')}
        - Missing Skills: ${scoringResult.feedback.missing_skills?.slice(0, 3).join(', ')}
      `;

      const formData = new FormData();
      formData.append('question', question);
      formData.append('context', context);

      const response = await fetch('http://localhost:8000/ai/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const result = await response.json();

      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        question,
        answer: result.response,
        timestamp: new Date().toLocaleTimeString(),
        model: result.model_used || 'openai'
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        question,
        answer: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date().toLocaleTimeString(),
        model: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const suggestedQuestions = [
    "Why did I get this score?",
    "How can I improve my resume?",
    "What skills should I focus on learning?",
    "Is my experience relevant for this role?",
    "What are my strongest selling points?"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="glass-card rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <MessageCircle className="w-5 h-5 mr-2 text-tech-600" />
          Ask AI About Your Score
        </h3>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Chat Messages */}
      <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-2"
            >
              {/* User Question */}
              <div className="flex justify-end">
                <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                  <div className="bg-tech-600 text-white p-3 rounded-2xl rounded-tr-md">
                    <p className="text-sm">{message.question}</p>
                  </div>
                  <div className="w-8 h-8 bg-tech-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-tech-600" />
                  </div>
                </div>
              </div>

              {/* AI Answer */}
              {message.answer && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                    <div className="w-8 h-8 bg-gradient-to-r from-tech-500 to-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-gray-100 p-3 rounded-2xl rounded-tl-md">
                      <p className="text-sm text-gray-800 leading-relaxed">{message.answer}</p>
                      <p className="text-xs text-gray-500 mt-2">{message.timestamp}</p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-tech-500 to-primary-500 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-100 p-3 rounded-2xl rounded-tl-md">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Suggested Questions */}
      {messages.length === 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-3">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <motion.button
                key={index}
                onClick={() => setCurrentQuestion(question)}
                className="px-3 py-1 bg-tech-100 text-tech-700 rounded-full text-xs hover:bg-tech-200 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {question}
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Input */}
      <div className="flex space-x-3">
        <div className="flex-1 relative">
          <textarea
            value={currentQuestion}
            onChange={(e) => setCurrentQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your score, get career advice, or request specific feedback..."
            rows={2}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-tech-500 focus:border-transparent transition-all duration-200 resize-none"
            disabled={isLoading}
          />
          <Sparkles className="absolute top-3 right-3 w-4 h-4 text-tech-400" />
        </div>
        
        <motion.button
          onClick={handleSendMessage}
          disabled={!currentQuestion.trim() || isLoading}
          className={`
            px-4 py-3 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2
            ${currentQuestion.trim() && !isLoading
              ? 'tech-gradient text-white hover:shadow-tech'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
          whileHover={currentQuestion.trim() && !isLoading ? { scale: 1.05 } : {}}
          whileTap={currentQuestion.trim() && !isLoading ? { scale: 0.95 } : {}}
        >
          <Send className="w-4 h-4" />
        </motion.button>
      </div>
    </motion.div>
  );
};

export default AIChat;