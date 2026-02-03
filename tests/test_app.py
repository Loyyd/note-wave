import unittest
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the path so we can import SpeechRec
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SpeechRec.app import app

class SpeechRecTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('SpeechRec.app.transcript_service')
    def test_save_transcript(self, mock_transcript_service):
        mock_transcript_service.save_transcript.return_value = {
            'file': 'test_file.txt',
            'folder': 'test_folder',
            'path': '/path/to/test_file.txt'
        }

        payload = {
            'transcript': 'This is a test transcript.',
            'week': 'W1',
            'course': 'TestCourse'
        }
        response = self.app.post('/save_transcript', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['file'], 'test_file.txt')
        
        mock_transcript_service.save_transcript.assert_called_once_with(
            'This is a test transcript.', 'W1', 'TestCourse'
        )

    @patch('SpeechRec.app.summarizer')
    def test_summarize(self, mock_summarizer):
        mock_summarizer.summarize.return_value = 'This is a summary.'

        payload = {'text': 'This is a long text to summarize.'}
        response = self.app.post('/summarize', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['summary'], 'This is a summary.')
        
        mock_summarizer.summarize.assert_called_once_with('This is a long text to summarize.')

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
