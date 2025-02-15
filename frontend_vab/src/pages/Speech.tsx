import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { wsService } from '../services/websocket'

function Speech() {
  const [isRecording, setIsRecording] = useState(false)
  const [isAiSpeaking, setIsAiSpeaking] = useState(false)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [timer, setTimer] = useState(0)
  const timerRef = useRef<number>()
  const navigate = useNavigate()

  useEffect(() => {
    // Connect to WebSocket when component mounts
    const speechId = 'new' // You might want to generate this or get from URL
    wsService.connect(speechId)

    wsService.setMessageCallback((event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'response.created':
            setIsAiSpeaking(true)
            break
            
          case 'response.done':
            setIsAiSpeaking(false)
            if (data.response.status === 'completed') {
              // Handle completion, maybe move to next question
              handleResponseComplete(data.response)
            }
            break
            
          case 'session.question':
            setCurrentQuestion(data.question)
            break
        }
      } catch (error) {
        console.error('Error handling message:', error)
      }
    })

    return () => {
      wsService.disconnect()
    }
  }, [])

  const handleResponseComplete = (response: any) => {
    if (response.is_final) {
      navigate('/results', { state: { analysis: response.analysis } })
    }
  }

  const startRecording = async () => {
    try {
      await wsService.startRecording()
      setIsRecording(true)
      
      timerRef.current = window.setInterval(() => {
        setTimer(t => t + 1)
      }, 1000)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    wsService.stopRecording()
    setIsRecording(false)
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="glass-panel p-8 w-full max-w-2xl relative">
        <button
          onClick={() => navigate('/')}
          className="absolute top-4 right-4 text-gray-400 hover:text-primary-400 transition-colors"
          title="Exit to Dashboard"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {isRecording || isAiSpeaking ? (
          <>
            <div className="text-center mb-8">
              {isRecording && (
                <div className="text-5xl font-bold mb-6 text-primary-400">
                  {formatTime(timer)}
                </div>
              )}
              <div className="relative w-24 h-24 mx-auto mb-8">
                <div className="pulse-ring" />
                <div className={`absolute inset-0 rounded-full animate-pulse ${isRecording ? 'bg-red-500' : 'bg-primary-500'}`} />
                <div className={`absolute inset-2 rounded-full ${isRecording ? 'bg-red-600' : 'bg-primary-600'}`} />
              </div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-300">
                {isAiSpeaking ? 'AI is speaking...' : 'Current Question:'}
              </h2>
              <p className="text-lg text-gray-400">{currentQuestion}</p>
            </div>
            {!isAiSpeaking && (
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={isRecording ? 'btn-danger w-full' : 'btn-primary w-full'}
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </button>
            )}
          </>
        ) : (
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-primary-300 text-transparent bg-clip-text">
              Ready to Start
            </h1>
            <button
              onClick={startRecording}
              className="btn-primary w-full"
            >
              Begin Interview
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Speech 