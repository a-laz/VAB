import React, { useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Button,
  styled,
  Paper,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { CloudUpload, CheckCircle } from '@mui/icons-material';

const Container = styled(Paper)`
  max-width: 600px;
  width: 90%;
  padding: 24px;
  border-radius: 16px;
  background-color: white;
  margin: 16px;

  @media (max-width: 600px) {
    width: 95%;
    padding: 16px;
    margin: 8px;
  }
`;

const UploadArea = styled(Box)`
  border: 2px dashed #2196f3;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  background-color: #f8f8f8;
  cursor: pointer;
  margin: 24px 0;
  transition: background-color 0.3s;
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

const StyledIcon = styled(CloudUpload)`
  font-size: 64px;
  color: #2196f3;
  margin-bottom: 16px;
`;

const SuccessIcon = styled(CheckCircle)`
  font-size: 64px;
  color: #4caf50;
  margin-bottom: 16px;
`;

const FileInput = styled('input')`
  display: none;
`;

const ActionButton = styled(Button)`
  background-color: #2196f3;
  color: white;
  padding: 12px 32px;
  font-size: 1.1rem;
  border-radius: 24px;
  text-transform: none;
  margin-top: 16px;
  width: 100%;
  
  &:hover {
    background-color: #1976d2;
  }

  @media (max-width: 600px) {
    padding: 8px 24px;
    font-size: 1rem;
  }
`;

interface FileUploadProps {
  onComplete: () => void;
}

export const FileUpload = ({ onComplete }: FileUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF or Word document');
      return;
    }
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      setError('File size should be less than 5MB');
      return;
    }
    setFile(file);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      // Simulate upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      setUploadSuccess(true);
      setTimeout(onComplete, 1000);
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container elevation={2}>
      <Typography variant="h5" align="center" gutterBottom fontWeight="bold">
        Upload Your File
      </Typography>

      <UploadArea
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <FileInput
          type="file"
          accept=".pdf,.doc,.docx"
          id="file-upload"
          onChange={handleFileSelect}
        />
        <label htmlFor="file-upload">
          {uploadSuccess ? (
            <SuccessIcon />
          ) : (
            <StyledIcon />
          )}
          <Typography variant="h6" gutterBottom>
            {file ? file.name : 'Drag and drop your file here'}
          </Typography>
          <Typography color="textSecondary">
            or click to browse (PDF, DOC, DOCX)
          </Typography>
        </label>
      </UploadArea>

      <ActionButton
        variant="contained"
        onClick={handleUpload}
        disabled={!file || uploading || uploadSuccess}
      >
        {uploading ? (
          <CircularProgress size={24} color="inherit" />
        ) : uploadSuccess ? (
          'Upload Complete!'
        ) : (
          'Upload File'
        )}
      </ActionButton>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
}; 