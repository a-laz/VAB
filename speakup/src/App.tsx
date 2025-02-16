import React, { useState } from 'react';
import { Box, Button, Typography, styled, useMediaQuery, useTheme } from '@mui/material';
import { Navbar } from './components/Navbar/Navbar';
import { Sidebar } from './components/Sidebar/Sidebar';
import { InterviewForm } from './components/InterviewForm/InterviewForm';
import { ResumeUpload } from './components/ResumeUpload/ResumeUpload';
import { JobDescription } from './components/JobDescription/JobDescription';
import { InterviewMode } from './components/InterviewMode/InterviewMode';
import { FileUpload } from './components/FileUpload/FileUpload';

const MainContainer = styled(Box)`
  display: flex;
  min-height: 100vh;
  background-color: white;
`;

const ContentArea = styled(Box)`
  flex-grow: 1;
  margin-left: 0;
  margin-top: 64px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  @media (max-width: 600px) {
    padding: 16px;
  }
`;

const WelcomeSection = styled(Box)`
  text-align: center;
  max-width: 600px;
  padding: ${({ theme }) => theme.spacing(2)};
  
  @media (max-width: 600px) {
    padding: ${({ theme }) => theme.spacing(1)};
  }
`;

const WelcomeImage = styled(Box)`
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, #2196f3, #673ab7);
  border-radius: 50%;
  margin: 48px auto;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ActionButton = styled(Button)`
  background-color: #2196f3;
  color: white;
  padding: 12px 32px;
  font-size: 1.1rem;
  border-radius: 24px;
  text-transform: none;
  
  &:hover {
    background-color: #1976d2;
  }
`;

enum Screen {
  INTERVIEW_MODE
}

interface InterviewFormData {
  jobRole: string;
  interviewType: 'technical' | 'behavioral' | 'case study';
  duration: '5' | '15' | '30';
}

function App() {
  const [currentScreen] = useState<Screen>(Screen.INTERVIEW_MODE);
  const [formData] = useState<InterviewFormData>({
    jobRole: 'Software Engineer',
    interviewType: 'technical',
    duration: '15'
  });

  const renderContent = () => {
    return (
      <InterviewMode 
        jobRole={formData.jobRole} 
        interviewType={formData.interviewType}
      />
    );
  };

  return (
    <MainContainer>
      <Navbar />
      <Sidebar />
      <ContentArea>
        {renderContent()}
      </ContentArea>
    </MainContainer>
  );
}

export default App;
