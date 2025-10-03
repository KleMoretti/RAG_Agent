import os
import re
import hashlib
from typing import Any, List, Dict


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
        """
        提取 PDF 文本，优先使用 PyMuPDF（更好保留空格/连字），失败时回退到 PyPDF2。

        同时做一次轻量的后处理，修复英文被拆成单字母并以空格分隔的问题，
        以及常见的连字符换行拼接。
        """
        text = ""
        # 优先尝试 PyMuPDF（pymupdf）
        try:
            import fitz  # type: ignore
            with fitz.open(file_path) as doc:
                texts: list[str] = []
                for page in doc:
                    # 首选 "text" 模式
                    page_text = page.get_text("text")
                    if not page_text or not page_text.strip():
                        # 回退：尝试 blocks/raw
                        page_text = page.get_text("blocks") or page.get_text("raw") or ""
                    texts.append(page_text)
                text = "\n".join(texts)
        except Exception:
            # 回退到 PyPDF2
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                extracted = []
                for page in reader.pages:
                    try:
                        extracted.append(page.extract_text() or "")
                    except Exception:
                        extracted.append("")
                text = "\n".join(extracted)

        return self._postprocess_pdf_text(text)

    def _postprocess_pdf_text(self, text: str) -> str:
        """修复 PDF 常见文本问题：
        - 英文单词被拆成单字母并以空格分隔，例如 "D e v e l o p" -> "Develop"
        - 行尾连字符导致的错误断词："hyphen-\n ated" -> "hyphenated"
        - 统一空白

        Args:
            text: 原始提取文本

        Returns:
            规整后的文本
        """
        if not text:
            return ""

        # 修复连字符 + 换行的断词（包括 Windows/Unix 换行）
        # e.g. "infor-\nmation" -> "information"
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

        # 统一换行为空格，避免段内断行引入多余分词
        text = re.sub(r"\s*\n\s*", " ", text)

        # 合并被空格拆开的纯字母序列：
        # 将 "D e e p  L e a r n i n g" -> "Deep Learning"
        def _merge_spaced_letters(match: re.Match[str]) -> str:
            spaced = match.group(0)
            # 去除内部多余空格，仅保留一个单词内的字母
            return spaced.replace(" ", "")

        # 仅在纯字母单字母序列上合并，避免影响如 "A B 测试" 这类混合
        # 模式匹配：至少三个单字母被空格分开的序列，尽量避免缩写误伤
        text = re.sub(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b", _merge_spaced_letters, text)

        # 压缩多余空白
        text = re.sub(r"\s+", " ", text).strip()
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