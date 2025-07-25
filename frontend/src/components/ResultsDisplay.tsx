import React from 'react';
import { CheckCircle, AlertCircle, XCircle, TrendingUp } from 'lucide-react';

interface ScoringResult {
  score: number;
  overall_score: number;
  confidence_level: string;
  summary: string;
  strengths: string[];
  concerns: string[];
  missing_skills: string[];
  matching_skills: string[];
  feedback: any;
  final_score: number;
  skill_score?: number;
  education_score?: number;
  domain_score?: number;
  experience_score?: number;
}

interface ResultsDisplayProps {
  result: ScoringResult;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  const finalScore = result.final_score || result.overall_score || result.score || 0;
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return <CheckCircle size={24} />;
    if (score >= 60) return <TrendingUp size={24} />;
    if (score >= 40) return <AlertCircle size={24} />;
    return <XCircle size={24} />;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Needs Improvement';
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Analysis Results</h2>
      </div>

      {/* Score Display */}
      <div className={`score-display ${getScoreColor(finalScore)}`}>
        <div className="score-icon">
          {getScoreIcon(finalScore)}
        </div>
        <div className="score-details">
          <div className="score-number">{Math.round(finalScore)}/100</div>
          <div className="score-label">{getScoreLabel(finalScore)}</div>
        </div>
      </div>

      {/* Summary */}
      {result.summary && (
        <div className="summary-section">
          <h3>Summary</h3>
          <p>{result.summary}</p>
        </div>
      )}

      {/* Strengths */}
      {result.strengths && result.strengths.length > 0 && (
        <div className="strengths-section">
          <h3>Strengths</h3>
          <ul className="strengths-list">
            {result.strengths.slice(0, 5).map((strength, index) => (
              <li key={index} className="strength-item">
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement */}
      {result.concerns && result.concerns.length > 0 && (
        <div className="concerns-section">
          <h3>Areas for Improvement</h3>
          <ul className="concerns-list">
            {result.concerns.slice(0, 5).map((concern, index) => (
              <li key={index} className="concern-item">
                {concern}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Skills Analysis */}
      <div className="skills-analysis">
        <div className="skills-grid">
          {result.matching_skills && result.matching_skills.length > 0 && (
            <div className="matching-skills">
              <h3>Matching Skills</h3>
              <div className="skills-tags">
                {result.matching_skills.slice(0, 10).map((skill, index) => (
                  <span key={index} className="skill-tag matching">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.missing_skills && result.missing_skills.length > 0 && (
            <div className="missing-skills">
              <h3>Missing Skills</h3>
              <div className="skills-tags">
                {result.missing_skills.slice(0, 10).map((skill, index) => (
                  <span key={index} className="skill-tag missing">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Confidence Level */}
      {result.confidence_level && (
        <div className="confidence-section">
          <h3>Confidence Level</h3>
          <div className={`confidence-badge ${result.confidence_level.toLowerCase()}`}>
            {result.confidence_level}
          </div>
        </div>
      )}

      {/* Individual Scores (Top-level) */}
      {(result.skill_score !== undefined || result.education_score !== undefined || result.domain_score !== undefined || result.experience_score !== undefined) && (
        <div className="individual-scores">
          {result.skill_score !== undefined && (
            <div><strong>Skill Score:</strong> {result.skill_score}/100</div>
          )}
          {result.education_score !== undefined && (
            <div><strong>Education Score:</strong> {result.education_score}/100</div>
          )}
          {result.domain_score !== undefined && (
            <div><strong>Domain Score:</strong> {result.domain_score}/100</div>
          )}
          {result.experience_score !== undefined && (
            <div><strong>Experience Score:</strong> {result.experience_score}/100</div>
          )}
        </div>
      )}

      {/* Additional Feedback */}
      {result.feedback && typeof result.feedback === 'object' && (
        <div className="additional-feedback">
          <h3>Detailed Analysis</h3>
          <div className="feedback-content">
            {result.feedback.summary && (
              <div><strong>Summary:</strong> {result.feedback.summary}</div>
            )}
            {result.feedback.strengths && result.feedback.strengths.length > 0 && (
              <div><strong>Strengths:</strong> {result.feedback.strengths.join(', ')}</div>
            )}
            {result.feedback.concerns && result.feedback.concerns.length > 0 && (
              <div><strong>Concerns:</strong> {result.feedback.concerns.join(', ')}</div>
            )}
            {result.feedback.matching_skills && result.feedback.matching_skills.length > 0 && (
              <div><strong>Matching Skills:</strong> {result.feedback.matching_skills.join(', ')}</div>
            )}
            {result.feedback.missing_skills && result.feedback.missing_skills.length > 0 && (
              <div><strong>Missing Skills:</strong> {result.feedback.missing_skills.join(', ')}</div>
            )}
            {/* Individual Scores */}
            {result.feedback.skill_score !== undefined && (
              <div><strong>Skill Score:</strong> {result.feedback.skill_score}/100</div>
            )}
            {result.feedback.education_score !== undefined && (
              <div><strong>Education Score:</strong> {result.feedback.education_score}/100</div>
            )}
            {result.feedback.domain_score !== undefined && (
              <div><strong>Domain Score:</strong> {result.feedback.domain_score}/100</div>
            )}
            {result.feedback.experience_score !== undefined && (
              <div><strong>Experience Score:</strong> {result.feedback.experience_score}/100</div>
            )}
            {/* Show any other fields in feedback as JSON for debugging */}
            {Object.keys(result.feedback).filter(k => !['summary','strengths','concerns','matching_skills','missing_skills'].includes(k)).length > 0 && (
              <details>
                <summary>Other Details (debug)</summary>
                <pre>{JSON.stringify(Object.fromEntries(Object.entries(result.feedback).filter(([k]) => !['summary','strengths','concerns','matching_skills','missing_skills'].includes(k))), null, 2)}</pre>
              </details>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
