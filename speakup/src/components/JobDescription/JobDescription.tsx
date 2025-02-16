import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button,
  styled,
  Paper
} from '@mui/material';
import { Description } from '@mui/icons-material';

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

const IconWrapper = styled(Box)`
  display: flex;
  justify-content: center;
  margin: 24px 0;
`;

const StyledIcon = styled(Description)`
  font-size: 64px;
  color: #2196f3;
`;

const ActionButton = styled(Button)`
  background-color: #2196f3;
  color: white;
  padding: 12px 32px;
  font-size: 1.1rem;
  border-radius: 24px;
  text-transform: none;
  margin-top: 24px;
  width: 100%;
  
  &:hover {
    background-color: #1976d2;
  }

  @media (max-width: 600px) {
    padding: 8px 24px;
    font-size: 1rem;
  }
`;

interface JobDescriptionProps {
  onContinue: (description: string) => void;
}

export const JobDescription = ({ onContinue }: JobDescriptionProps) => {
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onContinue(description);
  };

  return (
    <Container elevation={2}>
      <form onSubmit={handleSubmit}>
        <Typography variant="h5" align="center" gutterBottom fontWeight="bold">
          Job Description
        </Typography>
        
        <IconWrapper>
          <StyledIcon />
        </IconWrapper>

        <Typography variant="body1" gutterBottom align="center">
          Adding a job description helps tailor the interview to your specific role (optional)
        </Typography>

        <TextField
          multiline
          rows={6}
          fullWidth
          placeholder="Paste your job description here..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          sx={{ marginTop: 2 }}
        />

        <ActionButton 
          type="submit"
          variant="contained"
        >
          Start Interview
        </ActionButton>
      </form>
    </Container>
  );
}; 