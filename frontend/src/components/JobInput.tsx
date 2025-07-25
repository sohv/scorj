import React from 'react';
import { Link, FileText } from 'lucide-react';

interface JobInputProps {
  jobInputMethod: 'url' | 'text';
  jobUrl: string;
  jobDescription: string;
  onMethodChange: (method: 'url' | 'text') => void;
  onUrlChange: (url: string) => void;
  onDescriptionChange: (description: string) => void;
}

const JobInput: React.FC<JobInputProps> = ({
  jobInputMethod,
  jobUrl,
  jobDescription,
  onMethodChange,
  onUrlChange,
  onDescriptionChange
}) => {
  return (
    <div className="job-input-section">
      <h2>💼 Job Details</h2>
      
      <div className="job-method-selector">
        <button
          className={`method-btn ${jobInputMethod === 'url' ? 'active' : ''}`}
          onClick={() => onMethodChange('url')}
        >
          <Link size={20} />
          LinkedIn URL
        </button>
        <button
          className={`method-btn ${jobInputMethod === 'text' ? 'active' : ''}`}
          onClick={() => onMethodChange('text')}
        >
          <FileText size={20} />
          Job Description
        </button>
      </div>

      {jobInputMethod === 'url' ? (
        <div className="input-group">
          <label htmlFor="job-url">LinkedIn Job URL</label>
          <input
            id="job-url"
            type="url"
            className="job-url-input"
            placeholder="https://www.linkedin.com/jobs/view/..."
            value={jobUrl}
            onChange={(e) => onUrlChange(e.target.value)}
          />
          <small className="input-help">
            Paste the LinkedIn job posting URL to automatically extract job details
          </small>
        </div>
      ) : (
        <div className="input-group">
          <label htmlFor="job-description">Job Description</label>
          <textarea
            id="job-description"
            className="job-description-input"
            placeholder="Paste the full job description here..."
            rows={8}
            value={jobDescription}
            onChange={(e) => onDescriptionChange(e.target.value)}
          />
          <small className="input-help">
            Include requirements, responsibilities, and desired qualifications
          </small>
        </div>
      )}
    </div>
  );
};

export default JobInput;
