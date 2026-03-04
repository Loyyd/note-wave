import os
import re
from datetime import datetime
from typing import Dict, Any

class TranscriptService:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def save_transcript(self, text: str, week: str, course: str) -> Dict[str, Any]:
        """
        Saves the transcript text to a file.
        Returns a dictionary with file information.
        """
        # Build the folder name prefix: W#-CourseName-HHMM (sanitize course/week for filesystem)
        time_str = datetime.now().strftime('%H%M')
        week_safe = re.sub(r'[^A-Za-z0-9_-]', '_', week)
        course_safe = re.sub(r'[^A-Za-z0-9_-]', '_', course)
        
        # collapse multiple underscores and trim
        week_safe = re.sub(r'_+', '_', week_safe).strip('_')
        course_safe = re.sub(r'_+', '_', course_safe).strip('_')
        
        folder_name = f"{week_safe}-{course_safe}-{time_str}"
        folder_path = os.path.join(self.upload_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Create a unique filename based on the current time inside the folder
        filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(folder_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        return {
            'file': filename,
            'folder': folder_name,
            'path': filepath
        }
