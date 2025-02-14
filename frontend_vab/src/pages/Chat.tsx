import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ChatSidebar from '../components/ChatSidebar'

interface Message {
  id: string
  content: string
  sender: 'user' | 'other'
  timestamp: Date
}

function Chat() {
  const [messages, setMessages] = useState<{ [key: string]: Message[] }>({
    '1': [
      {
        id: '1',
        content: 'Hello! This is a test message with markdown:\n\n```javascript\nconsole.log("Hello World!");\n```',
        sender: 'other',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      },
    ],
    '2': [
      {
        id: '2',
        content: 'You can also use **bold** and *italic* text',
        sender: 'user',
        timestamp: new Date(),
      },
    ],
  })
  const [activeChat, setActiveChat] = useState('1')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [newMessage, setNewMessage] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const formatMessageDate = (date: Date) => {
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    }
    return date.toLocaleDateString()
  }

  const formatMessageTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const groupMessagesByDate = (msgs: Message[]) => {
    const groups: { [key: string]: Message[] } = {}
    msgs.forEach((message) => {
      const dateStr = formatMessageDate(message.timestamp)
      if (!groups[dateStr]) {
        groups[dateStr] = []
      }
      groups[dateStr].push(message)
    })
    return groups
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const audioChunks: Blob[] = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        const formData = new FormData()
        formData.append('audio', audioBlob)

        try {
          const response = await fetch('/api/upload-audio', {
            method: 'POST',
            body: formData,
          })
          if (response.ok) {
            const { audioUrl } = await response.json()
            const newMsg: Message = {
              id: Date.now().toString(),
              content: `🎤 [Voice Message](${audioUrl})`,
              sender: 'user',
              timestamp: new Date(),
            }
            setMessages(prev => ({
              ...prev,
              [activeChat]: [...(prev[activeChat] || []), newMsg],
            }))
          }
        } catch (error) {
          console.error('Audio upload failed:', error)
        }
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
  }

  const toggleTextToSpeech = () => {
    setIsListening(!isListening)
    if (!isListening) {
      const utterance = new SpeechSynthesisUtterance(
        messages[activeChat][messages[activeChat].length - 1].content
      )
      speechSynthesis.speak(utterance)
    } else {
      speechSynthesis.cancel()
    }
  }

  const startSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result) => result.transcript)
          .join('')

        setNewMessage(transcript)
      }

      recognition.onend = () => {
        setIsRecording(false)
      }

      recognition.start()
      setIsRecording(true)
    } else {
      alert('Speech recognition is not supported in this browser.')
    }
  }

  const speakMessage = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onend = () => setIsSpeaking(false)
      setIsSpeaking(true)
      speechSynthesis.speak(utterance)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() && !imageFile) return

    let messageContent = newMessage
    if (imageFile) {
      const formData = new FormData()
      formData.append('image', imageFile)
      try {
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        })
        if (response.ok) {
          const { imageUrl } = await response.json()
          messageContent += `\n![Uploaded Image](${imageUrl})`
        }
      } catch (error) {
        console.error('Image upload failed:', error)
      }
    }

    const newMsg: Message = {
      id: Date.now().toString(),
      content: messageContent,
      sender: 'user',
      timestamp: new Date(),
    }

    setMessages(prev => ({
      ...prev,
      [activeChat]: [...(prev[activeChat] || []), newMsg],
    }))
    setNewMessage('')
    setImageFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0])
    }
  }

  return (
    <div className="flex h-screen">
      <ChatSidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        activeChat={activeChat}
        onChatSelect={setActiveChat}
      />
      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b border-gray-200 p-4">
          <h1 className="text-xl font-semibold">Support Chat</h1>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {Object.entries(groupMessagesByDate(messages[activeChat] || [])).map(([date, msgs]) => (
            <div key={date}>
              <div className="flex justify-center mb-4">
                <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                  {date}
                </span>
              </div>
              {msgs.map((message) => (
                <div
                  key={message.id}
                  className={`chat-message ${
                    message.sender === 'user' ? 'chat-message-user' : 'chat-message-other'
                  }`}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '')
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={tomorrow}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        )
                      },
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatMessageTime(message.timestamp)}
                  </div>
                </div>
              ))}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
          <div className="flex space-x-4">
            <div className="flex-1 flex items-center space-x-2 bg-white rounded-lg border border-gray-300">
              <button
                type="button"
                onClick={startSpeechRecognition}
                className={`p-2 rounded-l-lg hover:bg-gray-100 ${isRecording ? 'text-primary-600' : ''}`}
                title="Start voice input"
              >
                {isRecording ? '🎤' : '🎙️'}
              </button>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                className="flex-1 p-2 focus:outline-none"
                placeholder="Type your message..."
              />
              <button
                type="button"
                onClick={() => speakMessage(messages[activeChat]?.[messages[activeChat].length - 1]?.content)}
                className={`p-2 hover:bg-gray-100 ${isSpeaking ? 'text-primary-600' : ''}`}
                title="Listen to last message"
              >
                {isSpeaking ? '🔊' : '🔈'}
              </button>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              ref={fileInputRef}
              className="hidden"
              id="image-upload"
            />
            <label
              htmlFor="image-upload"
              className="btn-primary flex items-center justify-center"
              title="Attach file"
            >
              📎
            </label>
            <button 
              type="submit" 
              className="btn-primary"
              title="Send message"
            >
              ↗️
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Chat 