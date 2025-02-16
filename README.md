# VocalAnalysisBuddy

An AI-powered public speaking coach that provides real-time feedback and analysis to help users improve their presentation skills.

## Project Description

VocalAnalysisBuddy leverages AI to analyze public speaking performances by:
- Providing real-time voice interaction and feedback
- Analyzing speech patterns, tone, and pacing
- Comparing against exemplary speeches
- Tracking progress over time
- Offering personalized improvement suggestions
- Generating intelligent feedback using GPT-4
- Real-time speech transcription and analysis

### Key Features
- Real-time speech analysis
- Live feedback during presentations
- Vector similarity search for speech comparison
- Performance metrics tracking (WPM, filler words, clarity)
- Database of exemplary speeches
- AI-powered feedback system
- Personalized improvement recommendations

## Backend Setup

### Prerequisites
- Python 3.x
- PostgreSQL
- AssemblyAI API key
- OpenAI API key


### Database Setup
1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Start PostgreSQL server:
   - Windows: PostgreSQL server runs as a service automatically
   - macOS/Linux: `sudo service postgresql start`
3. Create database:
```sql
CREATE DATABASE speech_coach_db;
```

### Django Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install django djangorestframework psycopg2-binary
```

3. Configure database:
   - Update database credentials in `speech_coach/settings.py`

4. Run migrations:
```bash
python manage.py migrate
```

5. Start Django server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### API Endpoints
Speech Management:
- `GET/POST /api/speeches/` - List/Create user speeches
- `GET/PUT/DELETE /api/speeches/<id>/` - Manage specific speeches
- `GET /api/exemplary-speeches/` - List exemplary speeches

Analysis & Status:
- `GET /api/speeches/<id>/analysis/` - Get detailed speech analysis
- `GET /api/speeches/<id>/status/` - Check processing status
- `POST /api/speeches/<id>/retry/` - Retry failed processing
- `GET /api/user/statistics/` - Get user's speaking statistics

WebSocket Endpoints:
- Real-time Transcription:
  - `ws://localhost:8000/ws/speeches/<id>/live/` - Live transcription and analysis

Each speech analysis includes:
- Real-time transcription
- Live performance metrics:
  - Words per minute (WPM)
  - Pause detection
  - Filler word tracking
  - Clarity scoring
- Similarity comparison with exemplary speeches
- AI-generated feedback:
  - Key strengths
  - Areas for improvement
  - Actionable recommendations
  - Overall assessment

### Real-time Features
1. Live Transcription:
   - Instant speech-to-text conversion
   - Word-level timestamps
   - Confidence scores

2. Real-time Analysis:
   - Live WPM calculation
   - Immediate filler word detection
   - Dynamic pause analysis
   - Continuous clarity assessment

3. Live Feedback:
   - Instant metric updates
   - Real-time suggestions
   - Performance indicators

### Authentication
- All endpoints require user authentication
- WebSocket connections are authenticated
- Responses include processing status and error messages

### Admin Interface
1. Admin credentials:
   - Username: vab
   - Password: Vvaabb123

2. Access the admin interface:
   - Go to `http://localhost:8000/admin`
   - Log in with the credentials above
   - Navigate to "Exemplary speeches" to add/edit speeches
   - Required fields:
     - Speaker name
     - Title
     - Audio file (mp3/wav format)
   - Optional fields:
     - Transcript
     - Date delivered
     - Occasion
     - Category

Note: These credentials are for development purposes only. Change them in production.

### WebSocket Connection Examples

1. JavaScript WebSocket Client:
```javascript
// Initialize WebSocket connection
const speechId = 123; // Your speech ID
const socket = new WebSocket(`ws://localhost:8000/ws/speeches/${speechId}/live/`);

// Handle connection open
socket.onopen = () => {
    console.log('WebSocket connection established');
};

// Handle incoming messages
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'transcription') {
        // Update UI with transcription
        console.log('Live transcription:', data.text);
        console.log('Confidence:', data.confidence);
        
        // Handle real-time analysis
        if (data.analysis) {
            console.log('Current WPM:', data.analysis.pacing.words_per_minute);
            console.log('Filler Words:', data.analysis.filler_words.total_count);
            console.log('Clarity Score:', data.analysis.clarity.score);
        }
    }
};

// Handle errors
socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Handle connection close
socket.onclose = () => {
    console.log('WebSocket connection closed');
};

// Send audio data (example using MediaRecorder)
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
            // Send audio chunk to WebSocket
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(event.data);
            }
        };

        // Start recording
        mediaRecorder.start(100); // Capture audio in 100ms chunks
    })
    .catch(error => console.error('Error accessing microphone:', error));
```

2. Python WebSocket Client (for testing):
```python
import asyncio
import websockets
import json
import pyaudio
import wave

async def connect_websocket(speech_id):
    uri = f"ws://localhost:8000/ws/speeches/{speech_id}/live/"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Set up audio capture
        CHUNK = 1024
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        try:
            while True:
                # Capture audio
                data = stream.read(CHUNK)
                
                # Send audio data
                await websocket.send(data)
                
                # Receive transcription
                response = await websocket.recv()
                result = json.loads(response)
                
                if result['type'] == 'transcription':
                    print(f"Transcription: {result['text']}")
                    if result['analysis']:
                        print(f"WPM: {result['analysis']['pacing']['words_per_minute']}")
                        print(f"Clarity: {result['analysis']['clarity']['score']}")
        
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

# Run the client
asyncio.get_event_loop().run_until_complete(
    connect_websocket(speech_id=123)
)
```

3. React Component Example:
```jsx
import React, { useEffect, useState } from 'react';

const LiveTranscription = ({ speechId }) => {
    const [transcript, setTranscript] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [socket, setSocket] = useState(null);
    
    useEffect(() => {
        // Initialize WebSocket
        const ws = new WebSocket(`ws://localhost:8000/ws/speeches/${speechId}/live/`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'transcription') {
                setTranscript(prev => prev + ' ' + data.text);
                if (data.analysis) {
                    setAnalysis(data.analysis);
                }
            }
        };
        
        setSocket(ws);
        
        // Cleanup on unmount
        return () => {
            if (ws) ws.close();
        };
    }, [speechId]);
    
    return (
        <div>
            <h2>Live Transcription</h2>
            <div className="transcript">{transcript}</div>
            
            {analysis && (
                <div className="analysis">
                    <h3>Real-time Analysis</h3>
                    <p>Words per minute: {analysis.pacing.words_per_minute}</p>
                    <p>Clarity score: {analysis.clarity.score}</p>
                    <p>Filler words: {analysis.filler_words.total_count}</p>
                </div>
            )}
        </div>
    );
};

export default LiveTranscription;
```

These examples demonstrate:
1. WebSocket connection setup
2. Audio capture and streaming
3. Handling real-time transcription results
4. Processing live analysis updates
5. Error handling and cleanup


## Frontend Setup

[Frontend setup instructions to be added by Vlad]

```

This README provides essential information about the project and clear setup instructions for the backend. I've left space for frontend setup instructions to be added later.
