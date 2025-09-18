import os
from typing import Any

class DataLoader:
    """
    加载并解析多种类型的数据文件，输出原始文本字符串。
    支持 PDF、Word、音频（wav/mp3）。
    """

    SUPPORTED_EXTS = {'.pdf', '.docx', '.doc', '.wav', '.mp3'}

    def _load_pdf(self, file_path: str) -> str:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            text = ''.join(page.extract_text() for page in reader.pages)
        return text

    def _load_word(self, file_path: str) -> str:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join(para.text for para in doc.paragraphs)

    def _load_audio(self, file_path: str) -> str:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)  # type: ignore[attr-defined]

    def load(self, file_path: str) -> str:
        """
                加载文件并返回原始文本。

                Args:
                    file_path: 文件路径

                Returns:
                    原始文本字符串

                Raises:
                    ValueError: 不支持的文件类型
                """
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.pdf':
            return self._load_pdf(file_path)
        elif ext in {'.docx', '.doc'}:
            return self._load_word(file_path)
        elif ext in {'.wav', '.mp3'}:
            return self._load_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")