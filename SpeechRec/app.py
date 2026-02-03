from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
import re

app = Flask(__name__)

# Folder to save transcripts
TRANSCRIPT_FOLDER = 'transcripts'
if not os.path.exists(TRANSCRIPT_FOLDER):
    os.makedirs(TRANSCRIPT_FOLDER)

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

    # Build the folder name prefix: W#-CourseName-HHMM (sanitize course/week for filesystem)
    time_str = datetime.now().strftime('%H%M')
    week_safe = re.sub(r'[^A-Za-z0-9_-]', '_', week)
    course_safe = re.sub(r'[^A-Za-z0-9_-]', '_', course)
    # collapse multiple underscores and trim
    week_safe = re.sub(r'_+', '_', week_safe).strip('_')
    course_safe = re.sub(r'_+', '_', course_safe).strip('_')
    folder_name = f"{week_safe}-{course_safe}-{time_str}"
    folder_path = os.path.join(TRANSCRIPT_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create a unique filename based on the current time inside the folder
    filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(folder_path, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(transcript_text)

    print(f"Transcript saved: {folder_name}/{filename}")
    return jsonify({'status': 'success', 'file': filename, 'folder': folder_name})

# --- Summarization support ---
import requests
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma3:4b') # Prefer gemma3:4b when available locally

class OllamaSummarizer:
    def __init__(self, model_name: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.model_name = model_name
        self.host = host
        print(f"🔄 OllamaSummarizer initialized (model: {self.model_name}, host: {self.host})")

    def _summarize(self, text: str) -> str:
        # Build a clear prompt and limit the request timeout for responsiveness
        prompt = f"Summarize the following text in 2 short sentences:\n\n{text}"
        try:
            response = requests.post(f"{self.host}/api/generate", json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }, timeout=10)
            response.raise_for_status()
            result = response.json()

            # Try several possible response shapes for robustness
            if isinstance(result, dict):
                if "response" in result and result["response"]:
                    return result["response"].strip()
                if "result" in result and isinstance(result["result"], dict):
                    r = result["result"]
                    if "text" in r and r["text"]:
                        return r["text"].strip()
                    if "output" in r and isinstance(r["output"], list):
                        parts = []
                        for o in r["output"]:
                            if isinstance(o, dict):
                                parts.append(o.get("content", ""))
                            else:
                                parts.append(str(o))
                        return " ".join(parts).strip()
                if "choices" in result and len(result["choices"]) > 0:
                    c = result["choices"][0]
                    if isinstance(c, dict) and "text" in c:
                        return c["text"].strip()

            # Fallback: return raw stringified response
            return str(result).strip()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama server not reachable or request failed at {self.host}: {e}. Falling back to SimpleSummarizer.")
            raise

SUMMARIZER = None
# Attempt to use Ollama Summarizer first
try:
    ollama_summarizer_instance = OllamaSummarizer()  # Uses OLLAMA_MODEL by default (gemma3:4b)
    test_summary = ollama_summarizer_instance._summarize("This is a quick local test to validate the model.")
    SUMMARIZER = ollama_summarizer_instance
    print(f"✅ Ollama Summarizer ({OLLAMA_MODEL}) configured successfully.")
except Exception as e:
    print(f"Ollama ({OLLAMA_MODEL}) not available or failed: {e}. Falling back to SimpleSummarizer.")

if SUMMARIZER is None:
    class SimpleSummarizer:
        def _summarize(self, text):
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            if not sentences or sentences == ['']:
                return "No text to summarize."
            return ' '.join(sentences[:2])
    SUMMARIZER = SimpleSummarizer()
    print("🔄 Falling back to SimpleSummarizer.")

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'status':'error', 'message':'No text provided'}), 400
    try:
        summary = SUMMARIZER._summarize(text)
        if not summary:
            return jsonify({'status':'error', 'message':'Summarization failed'}), 500
        return jsonify({'status':'success', 'summary': summary})
    except Exception as e:
        return jsonify({'status':'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
