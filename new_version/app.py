from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import base64
import os
from pathlib import Path
import tempfile
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio data to text using OpenAI Whisper"""
    audio_data = request.json.get('audio')
    
    if not audio_data:
        return jsonify({'error': 'No audio data received'}), 400
    
    # Convert base64 to audio file
    audio_bytes = base64.b64decode(audio_data.split(',')[1])
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        with open(temp_audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        os.unlink(temp_audio_path)
        return jsonify({'text': transcript.text})
    except Exception as e:
        os.unlink(temp_audio_path)
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Get response from ChatGPT and convert it to speech"""
    message = request.json.get('message')
    
    if not message:
        return jsonify({'error': 'No message received'}), 400

    try:
        # Get ChatGPT response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        
        response_text = response.choices[0].message.content

        # Convert response to speech
        tts = gTTS(text=response_text, lang='en')
        
        # Save audio to temporary file and convert to base64
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            tts.save(temp_audio.name)
            with open(temp_audio.name, 'rb') as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            os.unlink(temp_audio.name)

        return jsonify({
            'text': response_text,
            'audio': f'data:audio/mp3;base64,{audio_base64}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 