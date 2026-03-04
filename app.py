#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from config import Config
from services.transcript_service import TranscriptService
from services.summarizer_service import get_summarizer

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Services
transcript_service = TranscriptService(app.config['TRANSCRIPT_FOLDER'])
summarizer = get_summarizer(app.config['OLLAMA_MODEL'], app.config['OLLAMA_HOST'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_transcript', methods=['POST'])
def save_transcript():
    data = request.get_json()
    transcript_text = data.get('transcript', '')
    week = data.get('week', 'W1')
    course = data.get('course', 'Course-1')

    if not transcript_text:
        return jsonify({'status': 'error', 'message': 'No text provided'}), 400

    try:
        result = transcript_service.save_transcript(transcript_text, week, course)
        print(f"Transcript saved: {result['folder']}/{result['file']}")
        return jsonify({'status': 'success', 'file': result['file'], 'folder': result['folder']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'status':'error', 'message':'No text provided'}), 400
    try:
        summary = summarizer.summarize(text)
        if not summary:
            return jsonify({'status':'error', 'message':'Summarization failed'}), 500
        return jsonify({'status':'success', 'summary': summary})
    except Exception as e:
        return jsonify({'status':'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])