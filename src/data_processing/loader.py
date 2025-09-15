import os
from typing import List, Union

class DataLoader:
    """A class to load and process different types of data files."""
    def load_pdf(self, file_path: str) -> str:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            text = ''.join(page.extract_text() for page in reader.pages)
        return text

    def load_word(self, file_path: str) -> str:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])

    def load_audio(self, file_path: str) -> str:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

    def load(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.pdf':
            return self.load_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.load_word(file_path)
        elif ext in ['.wav', '.mp3']:
            return self.load_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")