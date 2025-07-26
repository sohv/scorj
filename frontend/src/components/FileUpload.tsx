import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';

interface FileUploadProps {
  resumeFile: File | null;
  onFileSelect: (file: File | null) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ resumeFile, onFileSelect }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFileSelect(null);
  };

  return (
    <div className="file-upload-section">
      <h2>Upload Your Resume</h2>
      
      {!resumeFile ? (
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload size={48} className="upload-icon" />
          <div className="upload-text">
            {isDragActive ? (
              <p>Drop your resume here...</p>
            ) : (
              <>
                <p><strong>Click here</strong> or drag & drop your resume</p>
                <p className="supported-formats">Supports PDF and DOCX files</p>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="file-selected">
          <div className="file-info">
            <File size={24} />
            <div className="file-details">
              <p className="file-name">{resumeFile.name}</p>
              <p className="file-size">
                {(resumeFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <button 
            className="remove-file-btn"
            onClick={removeFile}
            type="button"
          >
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
