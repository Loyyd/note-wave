# 🎙️ notewave

A simple, local AI-powered transcription and summarization tool. **notewave** uses the Web Speech API for real-time transcription and integrates with local LLMs (via Ollama) to generate concise summaries of your notes.

## ✨ Features

- **Live Transcription**: Real-time voice-to-text directly in your browser.
- **AI Summarization**: One-click summaries using local Ollama models (defaults to `gemma2:2b`).
- **Organized Storage**: Transcripts are automatically saved into dated folders categorized by Course and Week.
- **Dark Mode UI**: A clean, "paper-like" interface designed for focus.
- **Local First**: Your data stays on your machine.

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **Ollama** (Optional, for AI summaries): [Download Ollama](https://ollama.com/)
   - Pull the default model: `ollama pull gemma2:2b`
3. **Google Chrome**: (Required for Web Speech API support).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/konradkunkel/note-wave.git
   cd note-wave
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

1. Start the Flask server:
   ```bash
   ./app.py
   ```
2. Open your browser and navigate to `http://127.0.0.1:5000`.

## ⚙️ Configuration

You can customize the application by creating a `.env` file in the root directory:

```env
TRANSCRIPT_FOLDER=transcripts
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b
FLASK_DEBUG=True
```

## 🛠️ Project Structure

- `app.py`: Main Flask application and API endpoints.
- `services/`: Backend logic for file handling and AI integration.
- `templates/`: Frontend UI (HTML/CSS/JS).
- `transcripts/`: Default storage location for saved notes.

## 📝 License

MIT
