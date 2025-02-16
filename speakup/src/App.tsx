import React, { useState } from 'react';
import { Box, styled } from '@mui/material';
import { Navbar } from './components/Navbar/Navbar';
import { Sidebar } from './components/Sidebar/Sidebar';
import { InterviewForm } from './components/InterviewForm/InterviewForm';
import { FileUpload } from './components/FileUpload/FileUpload';
import { JobDescription } from './components/JobDescription/JobDescription';
import { InterviewMode } from './components/InterviewMode/InterviewMode';

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

enum Screen {
  INTERVIEW_FORM,
  FILE_UPLOAD,
  JOB_DESCRIPTION,
  INTERVIEW_MODE
}

interface InterviewFormData {
  jobRole: string;
  interviewType: 'technical' | 'behavioral' | 'case study';
  duration: '5' | '15' | '30';
}

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.INTERVIEW_FORM);
  const [formData, setFormData] = useState<InterviewFormData>({
    jobRole: '',
    interviewType: 'technical',
    duration: '15'
  });

  const renderContent = () => {
    switch (currentScreen) {
      case Screen.INTERVIEW_FORM:
        return (
          <InterviewForm 
            onContinue={(data) => {
              setFormData(data);
              setCurrentScreen(Screen.FILE_UPLOAD);
            }}
          />
        );
      case Screen.FILE_UPLOAD:
        return (
          <FileUpload 
            onComplete={() => setCurrentScreen(Screen.JOB_DESCRIPTION)}
          />
        );
      case Screen.JOB_DESCRIPTION:
        return (
          <JobDescription 
            onContinue={() => setCurrentScreen(Screen.INTERVIEW_MODE)}
          />
        );
      case Screen.INTERVIEW_MODE:
        return (
          <InterviewMode 
            jobRole={formData.jobRole} 
            interviewType={formData.interviewType}
          />
        );
    }
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
