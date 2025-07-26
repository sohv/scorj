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

      {/* Strengths and Concerns Table */}
      {((result.strengths && result.strengths.length > 0) || (result.concerns && result.concerns.length > 0)) && (
        <div className="analysis-table-section">
          <h3>Analysis Overview</h3>
          <div className="analysis-table-container">
            <table className="analysis-table">
              <thead>
                <tr>
                  <th className="strengths-header">
                    <CheckCircle size={20} />
                    Strengths
                  </th>
                  <th className="concerns-header">
                    <AlertCircle size={20} />
                    Areas for Improvement
                  </th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: Math.max(
                  result.strengths?.length || 0, 
                  result.concerns?.length || 0
                ) }).map((_, index) => (
                  <tr key={index}>
                    <td className="strength-cell">
                      {result.strengths?.[index] && (
                        <div className="table-item strength-item">
                          {result.strengths[index]}
                        </div>
                      )}
                    </td>
                    <td className="concern-cell">
                      {result.concerns?.[index] && (
                        <div className="table-item concern-item">
                          {result.concerns[index]}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
            {/* Additional feedback details in a structured format */}
            {result.feedback.detailed_breakdown && (
              <div className="detailed-breakdown">
                <h4>Detailed Breakdown</h4>
                <div className="breakdown-content">
                  {Object.entries(result.feedback.detailed_breakdown).map(([key, value]) => (
                    <div key={key} className="breakdown-item">
                      <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {value as string}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {result.feedback.recommendations && result.feedback.recommendations.length > 0 && (
              <div className="recommendations">
                <h4>Recommendations</h4>
                <ul className="recommendations-list">
                  {result.feedback.recommendations.map((rec: string, index: number) => (
                    <li key={index} className="recommendation-item">{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
