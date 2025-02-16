import React, { useState, useCallback } from 'react';
import { Box, Typography, Button, Paper, styled } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const UploadContainer = styled(Paper)`
  max-width: 600px;
  width: 100%;
  padding: 32px;
  border-radius: 16px;
  background-color: white;
`;

const DropZone = styled(Box)`
  border: 2px dashed #2196f3;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  background-color: #f8f8f8;
  cursor: pointer;
  margin: 24px 0;
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

const ContinueButton = styled(Button)`
  background-color: #2196f3;
  color: white;
  padding: 12px 32px;
  font-size: 1.1rem;
  border-radius: 24px;
  text-transform: none;
  margin-top: 16px;
  
  &:hover {
    background-color: #1976d2;
  }
`;

const FileInput = styled('input')`
  display: none;
`;

interface ResumeUploadProps {
  onContinue: () => void;
}

export const ResumeUpload = ({ onContinue }: ResumeUploadProps) => {
  const [file, setFile] = useState<File | null>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <UploadContainer elevation={2}>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        Upload Your Resume
      </Typography>
      
      <DropZone
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <FileInput
          type="file"
          accept=".pdf,.doc,.docx"
          id="resume-upload"
          onChange={handleFileSelect}
        />
        <label htmlFor="resume-upload">
          <CloudUpload sx={{ fontSize: 48, color: '#2196f3', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Drag and drop your resume here
          </Typography>
          <Typography color="textSecondary">
            or click to browse files (PDF, DOC, DOCX)
          </Typography>
          {file && (
            <Typography sx={{ mt: 2, color: 'success.main' }}>
              Selected file: {file.name}
            </Typography>
          )}
        </label>
      </DropZone>

      <ContinueButton
        variant="contained"
        fullWidth
        onClick={onContinue}
        disabled={!file}
      >
        Continue
      </ContinueButton>
    </UploadContainer>
  );
}; 