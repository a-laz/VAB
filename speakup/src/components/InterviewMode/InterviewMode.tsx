import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  IconButton,
  styled,
  Paper,
  CircularProgress
} from '@mui/material';
import { Mic, Stop } from '@mui/icons-material';

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

interface InterviewModeProps {
  jobRole: string;
  interviewType: string;
}

export const InterviewMode = ({ jobRole, interviewType }: InterviewModeProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState('');
  const [questionCount, setQuestionCount] = useState(0);
  
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const audioRef = useRef<HTMLAudioElement>(document.createElement('audio'));
  const isConnectingRef = useRef(false);

  const getPromptForCount = (count: number) => {
    switch (count) {
      case 0:
        return `I am interviewing for a Fullstack engineer position. This is a technical interview. 
                You are an experienced technical interviewer. Start with a brief introduction and ask your first question.`;
      case 1:
        return `Based on my previous answer, ask a follow-up question that goes deeper into technical details. 
                If I mentioned any specific technology, ask about its internals or best practices.`;
      case 2:
        return `Now ask a challenging problem-solving question related to movie actor role. 
                Make it a practical scenario that tests both technical knowledge and problem-solving ability.`;
      default:
        return `Continue the interview naturally, focusing on advanced concepts and real-world scenarios. 
                If I show expertise in a particular area, explore that further.`;
    }
  };

  const initializeConnection = async () => {
    if (isConnectingRef.current || dcRef.current?.readyState === 'open') return;
    isConnectingRef.current = true;

    try {
      const tokenResponse = await fetch('https://api.openai.com/v1/realtime/sessions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer `,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'gpt-4o-realtime-preview-2024-12-17',
          voice: 'verse',
        })
      });
      const data = await tokenResponse.json();
      const EPHEMERAL_KEY = data.client_secret.value;

      pcRef.current = new RTCPeerConnection();
      pcRef.current.ontrack = (e) => {
        audioRef.current.srcObject = e.streams[0];
        audioRef.current.autoplay = true;
      };

      const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
      pcRef.current.addTrack(ms.getTracks()[0]);

      dcRef.current = pcRef.current.createDataChannel('oai-events');
      
      dcRef.current.onopen = () => isConnectingRef.current = false;
      dcRef.current.onclose = () => {
        setIsRecording(false);
        setIsProcessing(false);
      };
      dcRef.current.onerror = () => {
        setIsProcessing(false);
        setIsRecording(false);
      };

      dcRef.current.addEventListener('message', (e) => {
        try {
          const message = JSON.parse(e.data);
          if (message.type === 'text.data') {
            setResponse(message.text.content);
            setIsProcessing(false);
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      });

      const offer = await pcRef.current.createOffer();
      await pcRef.current.setLocalDescription(offer);

      const sdpResponse = await fetch(`https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17`, {
        method: 'POST',
        body: offer.sdp,
        headers: {
          'Authorization': `Bearer ${EPHEMERAL_KEY}`,
          'Content-Type': 'application/sdp'
        },
      });

      await pcRef.current.setRemoteDescription({
        type: 'answer',
        sdp: await sdpResponse.text(),
      });

    } catch (error) {
      isConnectingRef.current = false;
      setIsProcessing(false);
      setIsRecording(false);
      console.error('Connection error:', error);
    }
  };

  const startRecording = async () => {
    try {
      await initializeConnection();

      if (dcRef.current?.readyState === 'open') {
        const prompt = getPromptForCount(questionCount);
        console.log('Using prompt:', prompt);

        const message = {
          type: 'response.create',
          response: {
            modalities: ['text'],
            instructions: prompt
          }
        };
        dcRef.current.send(JSON.stringify(message));
      }

      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setQuestionCount(prev => prev + 1);

    if (pcRef.current?.getSenders) {
      pcRef.current.getSenders().forEach(sender => sender.track?.stop());
    }

    if (dcRef.current) {
      dcRef.current.close();
      dcRef.current = null;
    }

    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }

    if (audioRef.current.srcObject instanceof MediaStream) {
      audioRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    audioRef.current.srcObject = null;
    isConnectingRef.current = false;
  };

  const toggleRecording = () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  };

  useEffect(() => {
    return () => {
      stopRecording();
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
          disabled={isProcessing}
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
    </Container>
  );
}; 