import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_FOLDER', 'transcripts')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma3:4b')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
