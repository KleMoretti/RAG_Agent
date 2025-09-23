import os
import hashlib
from typing import Any, List, Tuple, Dict


class DataLoader:
    """
    加载并解析多种类型的数据文件，输出原始文本字符串。
    支持 PDF、Word、音频（wav/mp3）。
    """

    SUPPORTED_EXTS = {'.pdf', '.docx', '.doc', '.wav', '.mp3'}

    def load_and_split(self, file_path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        加载文件，分块并生成元数据。

        Args:
            file_path: 文件路径
            chunk_size: 分块大小（字符数）

        Returns:
            包含必要元数据的文本块列表
        """
        text = self.load(file_path)
        chunks = self._split_text(text, chunk_size)

        results = []
        for i, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            metadata = {
                "file": os.path.basename(file_path),
                "chunk_id": i,
                "hash": chunk_hash,
                "preview": chunk[:200] + ("..." if len(chunk) > 200 else "")
            }
            results.append(metadata)

        return results

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        将文本分割为指定大小的块。

        Args:
            text: 原始文本
            chunk_size: 分块大小

        Returns:
            文本块列表
        """
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in text.split('。'):
            sentence = sentence.strip() + '。'
            if current_size + len(sentence) > chunk_size and current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(sentence)
            current_size += len(sentence)

        if current_chunk:
            chunks.append(''.join(current_chunk))

        return chunks

    def _load_pdf(self, file_path: str) -> str:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
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