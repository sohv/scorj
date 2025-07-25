import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="loading-container">
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
      <div className="loading-text">
        <h3>🤖 AI is analyzing your resume...</h3>
        <p>This usually takes 10-30 seconds</p>
        <div className="loading-steps">
          <div className="step">📄 Parsing resume content</div>
          <div className="step">🎯 Analyzing job requirements</div>
          <div className="step">🧠 Calculating match score</div>
          <div className="step">📊 Generating insights</div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
