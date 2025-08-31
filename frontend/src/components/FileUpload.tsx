import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, X } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File | null) => void;
  uploadedFile: File | null;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, uploadedFile }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    multiple: false
  });

  const removeFile = () => {
    onFileUpload(null);
  };

  return (
    <div className="glass-card rounded-2xl p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <Upload className="w-5 h-5 mr-2 text-tech-600" />
        Upload Resume
      </h2>

      {!uploadedFile ? (
        <motion.div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
            ${isDragActive 
              ? 'border-tech-400 bg-tech-50' 
              : 'border-gray-300 hover:border-tech-400 hover:bg-tech-25'
            }
          `}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <input {...getInputProps()} />
          <motion.div
            animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            <FileText className="w-12 h-12 text-tech-400 mx-auto mb-4" />
          </motion.div>
          
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
          </h3>
          <p className="text-gray-500 mb-4">
            Drag & drop or click to select your PDF or DOCX file
          </p>
          <div className="flex justify-center space-x-4 text-sm text-gray-400">
            <span className="px-3 py-1 bg-gray-100 rounded-full">PDF</span>
            <span className="px-3 py-1 bg-gray-100 rounded-full">DOCX</span>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-xl"
        >
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-medium text-green-800">{uploadedFile.name}</p>
              <p className="text-sm text-green-600">
                {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <motion.button
            onClick={removeFile}
            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <X className="w-5 h-5 text-red-500" />
          </motion.button>
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload;