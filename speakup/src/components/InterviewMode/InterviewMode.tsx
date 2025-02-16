import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  IconButton,
  styled,
  Paper,
  CircularProgress,
  Button
} from '@mui/material';
import { Mic, Stop } from '@mui/icons-material';
import { WebSocketService } from '../../services/websocket';

const Container = styled(Paper)`
  max-width: 800px;
  width: 90%;
  padding: 24px;
  border-radius: 16px;
  background-color: white;
  margin: 16px;
  min-height: 400px;
  display: flex;
  flex-direction: column;

  @media (max-width: 600px) {
    width: 95%;
    padding: 16px;
    margin: 8px;
  }
`;

const AnimationContainer = styled(Box)`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  position: relative;
`;

const WaveCircle = styled(Box)`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;

  &.active {
    background-color: #2196f3;
    
    &::after {
      content: '';
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background-color: #2196f3;
      opacity: 0.5;
      animation: pulse 1.5s infinite;
    }
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
      opacity: 0.5;
    }
    50% {
      transform: scale(1.5);
      opacity: 0;
    }
    100% {
      transform: scale(1);
      opacity: 0.5;
    }
  }
`;

const ResponseContainer = styled(Box)`
  margin-top: 24px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
  min-height: 100px;
`;

const INTERVIEW_PROMPTS = {
  technical: `You are an experienced technical interviewer. Ask relevant technical questions for the role, follow up on unclear answers, provide constructive feedback, stay professional and encouraging, adapt questions based on candidate's responses, and focus on specific examples.`,
  
  behavioral: `You are an experienced technical interviewer conducting a behavior interview for a product manager position.
        
Follow these guidelines:
1. Ask relevant questions for the role
2. Follow up on unclear or incomplete answers
3. Provide constructive feedback
4. Stay professional and encouraging
5. Adapt questions based on candidate's responses
6. Focus on specific examples and scenarios

Current interview type: behavior
Role: product manager`,
  
  'case study': `You are an experienced interviewer conducting a case study interview. Present relevant business cases for the role, guide the candidate through problem-solving, provide constructive feedback, stay professional and encouraging, and focus on analytical thinking and structured approach.`
};

interface InterviewModeProps {
  jobRole: string;
  interviewType: string;
}

export const InterviewMode = ({ jobRole, interviewType }: InterviewModeProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const wsRef = useRef<WebSocketService | null>(null);
  const isInitializedRef = useRef(false);

  const initializeWebSocket = async () => {
    if (isInitializedRef.current) return;
    isInitializedRef.current = true;

    const sessionId = Math.random().toString(36).substring(7);
    wsRef.current = new WebSocketService(sessionId);

    try {
      await wsRef.current.connect(
        (message) => {
          if (message.type === 'text.data') {
            setResponse(message.text.content);
            setIsProcessing(false);
            setIsInterviewStarted(true);
          }
        },
        () => {
          setIsProcessing(false);
          setIsConnected(false);
          setIsInterviewStarted(false);
        },
        () => {
          setIsRecording(false);
          setIsProcessing(false);
          setIsConnected(false);
          setIsInterviewStarted(false);
        }
      );
      setIsConnected(true);
      setIsProcessing(true);

      // Send the initial prompt and wait for the first question
      wsRef.current?.queueMessage(
        `${INTERVIEW_PROMPTS[interviewType as keyof typeof INTERVIEW_PROMPTS]}\n\nPlease start by introducing yourself as the interviewer and ask your first question.`
      );
    } catch (err) {
      setIsConnected(false);
      setIsProcessing(false);
      setIsInterviewStarted(false);
    }
  };

  const startRecording = async () => {
    try {
      if (!isConnected) {
        await initializeWebSocket();
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        wsRef.current?.sendAudio(audioBlob);
        setIsProcessing(true);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        stream.getTracks().forEach(track => track.stop());
      });
  };

  const toggleRecording = () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      isInitializedRef.current = false;
      setIsConnected(false);
      setResponse('');
    }
  };

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return (
    <Container elevation={2}>
      <Typography variant="h5" align="center" gutterBottom fontWeight="bold">
        Interview in Progress
      </Typography>

      <AnimationContainer>
        <IconButton 
          onClick={toggleRecording}
          disabled={isProcessing || !isInterviewStarted}
          sx={{ width: 120, height: 120 }}
        >
          <WaveCircle className={isRecording ? 'active' : ''}>
            {isRecording ? <Stop /> : <Mic />}
          </WaveCircle>
        </IconButton>
        
        {isProcessing && (
          <CircularProgress 
            size={140}
            thickness={2}
            sx={{ 
              position: 'absolute',
              color: '#2196f3'
            }}
          />
        )}
      </AnimationContainer>

      {(!isInterviewStarted && isConnected) && (
        <Typography align="center" color="textSecondary" sx={{ mt: 2 }}>
          Waiting for interviewer to start the session...
        </Typography>
      )}

      {(response || isProcessing) && (
        <ResponseContainer>
          {isProcessing ? (
            <Typography align="center" color="textSecondary">
              Processing your response...
            </Typography>
          ) : (
            <Typography>{response}</Typography>
          )}
        </ResponseContainer>
      )}

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          color={isConnected ? "error" : "primary"}
          onClick={isConnected ? disconnect : initializeWebSocket}
          sx={{ minWidth: 200 }}
        >
          {isConnected ? "End Interview" : "Start Interview"}
        </Button>
      </Box>
    </Container>
  );
}; 