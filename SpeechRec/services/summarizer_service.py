import requests
import re
from typing import Protocol

class Summarizer(Protocol):
    def summarize(self, text: str) -> str:
        ...

class SimpleSummarizer:
    def summarize(self, text: str) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if not sentences or sentences == ['']:
            return "No text to summarize."
        return ' '.join(sentences[:2])

class OllamaSummarizer:
    def __init__(self, model_name: str, host: str):
        self.model_name = model_name
        self.host = host
        print(f"🔄 OllamaSummarizer initialized (model: {self.model_name}, host: {self.host})")

    def summarize(self, text: str) -> str:
        prompt = f"Summarize the following text in 2 short sentences:\n\n{text}"
        try:
            response = requests.post(f"{self.host}/api/generate", json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }, timeout=10)
            response.raise_for_status()
            result = response.json()
            return self._parse_response(result)
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama server not reachable or request failed at {self.host}: {e}.")
            raise

    def _parse_response(self, result: dict) -> str:
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

        return str(result).strip()

def get_summarizer(model_name: str, host: str) -> Summarizer:
    try:
        summarizer = OllamaSummarizer(model_name, host)
        # Test the connection
        summarizer.summarize("Test")
        print(f"✅ Ollama Summarizer ({model_name}) configured successfully.")
        return summarizer
    except Exception as e:
        print(f"Ollama ({model_name}) not available or failed: {e}. Falling back to SimpleSummarizer.")
        print("🔄 Falling back to SimpleSummarizer.")
        return SimpleSummarizer()
