from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Mock database
speeches = {}
metrics = {
    'filler_words': [
        {'date': '2024-03-01', 'count': 15},
        {'date': '2024-03-05', 'count': 12},
        {'date': '2024-03-10', 'count': 8},
    ],
    'pace': [
        {'date': '2024-03-01', 'value': 135},
        {'date': '2024-03-05', 'value': 128},
        {'date': '2024-03-10', 'value': 122},
    ]
}

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics)

@app.route('/api/speech/analyze', methods=['POST'])
def analyze_speech():
    audio_data = request.files.get('audio')
    # Mock analysis
    analysis = {
        "speech_details": {
            "title": "Mock Speech",
            "duration": 3.5,
            "words_per_minute": 125,
            "clarity_score": 0.85
        },
        "transcript": "This is a mock transcript of the speech...",
        "analysis": {
            "pacing": {"assessment": "Good pace with room for improvement"},
            "pause_count": 4,
            "filler_words": {"total_count": 8},
            "clarity": {"assessment": "Clear and well-articulated"}
        },
        "evaluation": {
            "strengths": [
                "Consistent pace throughout",
                "Clear articulation",
                "Effective use of pauses"
            ],
            "improvements": [
                "Reduce filler words",
                "Vary pace for emphasis",
                "Extend pause duration"
            ],
            "recommendations": [
                "Practice removing common filler words",
                "Record and review speeches regularly",
                "Work on dramatic pauses"
            ],
            "overall_assessment": "Strong foundation with clear areas for improvement"
        }
    }
    return jsonify(analysis)

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = [
        "What is the main point you want to convey?",
        "Who is your target audience?",
        "What inspired you to speak about this topic?"
    ]
    return jsonify(questions)

if __name__ == '__main__':
    app.run(debug=True) 