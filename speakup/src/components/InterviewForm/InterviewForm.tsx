import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  RadioGroup,
  Radio,
  FormControlLabel,
  Button,
  styled,
  Paper,
  Alert,
  Snackbar
} from '@mui/material';
import axios from 'axios';

const FormContainer = styled(Paper)`
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

const FormSection = styled(Box)`
  margin-bottom: 24px;

  @media (max-width: 600px) {
    margin-bottom: 16px;
  }
`;

const SubmitButton = styled(Button)`
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

const DurationGroup = styled(Box)`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;

  @media (max-width: 600px) {
    gap: 4px;
  }
`;

const DurationOption = styled(FormControlLabel)`
  flex: 1;
  min-width: 100px;
  margin: 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  & .MuiRadio-root {
    padding: 4px;
  }

  @media (max-width: 600px) {
    min-width: 80px;
    padding: 4px;
  }
`;

interface InterviewFormData {
  jobRole: string;
  interviewType: 'technical' | 'behavioral' | 'case study';
  duration: '5' | '15' | '30';
}

interface InterviewRequestPayload {
  job_role: string;
  interview_type: string;
  duration_minutes: number;
  timezone: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

interface InterviewFormProps {
  onContinue: (data: InterviewFormData) => void;
}

interface ApiError {
  message: string;
  response?: {
    data?: {
      message?: string;
    };
  };
}

export const InterviewForm = ({ onContinue }: InterviewFormProps) => {
  const [formData, setFormData] = useState<InterviewFormData>({
    jobRole: '',
    interviewType: 'technical',
    duration: '15'
  });

  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.jobRole.trim()) {
      onContinue(formData);
    }
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <>
      <FormContainer elevation={2}>
        <form onSubmit={handleSubmit}>
          <FormSection>
            <Typography variant="h6" gutterBottom>
              Job Role
            </Typography>
            <TextField
              fullWidth
              placeholder="Enter your job role"
              value={formData.jobRole}
              onChange={(e) => setFormData({ ...formData, jobRole: e.target.value })}
              required
            />
          </FormSection>

          <FormSection>
            <Typography variant="h6" gutterBottom>
              Interview Type
            </Typography>
            <RadioGroup
              value={formData.interviewType}
              onChange={(e) => setFormData({ 
                ...formData, 
                interviewType: e.target.value as InterviewFormData['interviewType'] 
              })}
            >
              <DurationGroup>
                <DurationOption value="technical" control={<Radio />} label="Technical" />
                <DurationOption value="behavioral" control={<Radio />} label="Behavioral" />
                <DurationOption value="case study" control={<Radio />} label="Case Study" />
              </DurationGroup>
            </RadioGroup>
          </FormSection>

          <FormSection>
            <Typography variant="h6" gutterBottom>
              Duration (minutes)
            </Typography>
            <RadioGroup
              value={formData.duration}
              onChange={(e) => setFormData({ 
                ...formData, 
                duration: e.target.value as InterviewFormData['duration'] 
              })}
            >
              <DurationGroup>
                <DurationOption value="5" control={<Radio />} label="5 min" />
                <DurationOption value="15" control={<Radio />} label="15 min" />
                <DurationOption value="30" control={<Radio />} label="30 min" />
              </DurationGroup>
            </RadioGroup>
          </FormSection>

          <SubmitButton 
            type="submit" 
            variant="contained"
            disabled={!formData.jobRole.trim()}
          >
            Continue
          </SubmitButton>
        </form>
      </FormContainer>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </>
  );
}; 