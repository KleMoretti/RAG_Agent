import re
from typing import List, Optional


class Preprocessor:
    """
    文本预处理：清洗、分句、分段，支持不同语言和场景。
    用于向量化和检索前的标准化处理。
    """

    def __init__(self,
                 min_chars: int = 10,
                 keep_spaces: bool = True,
                 keep_numbers: bool = True):
        """
        初始化预处理器。

        Args:
            min_chars: 最小句子长度
            keep_spaces: 是否保留空格（英文分词需要）
            keep_numbers: 是否保留数字
        """
        self.min_chars = min_chars
        self.keep_spaces = keep_spaces
        self.keep_numbers = keep_numbers

    def clean_text(self, text: str) -> str:
        """
        清洗文本，标准化格式。

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        if not text:
            return ""

        # Fix space-separated characters (common PDF extraction issue)
        # Match patterns like "h e l l o" and convert to "hello"
        text = re.sub(r'\b(\w) (?=\w\b)', r'\1', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # 统一换行和空格 (normalize line breaks and spaces)
        text = re.sub(r'\s+', ' ', text)

        # 清理无效字符，保留中英文和标点
        pattern = r'[^\w\s\u4e00-\u9fff。！？，、；：""''（）《》\[\]【】]'
        if not self.keep_numbers:
            pattern = r'[^\w\s\u4e00-\u9fff。！？，、；：""''（）《》\[\]【】0-9]'

        text = re.sub(pattern, '', text)

        if not self.keep_spaces:
            text = re.sub(r'\s', '', text)

        return text.strip()

    def split_sentences(self, text: str) -> List[str]:
        """
        智能分句，处理常见标点和特殊情况。

        Args:
            text: 清洗后的文本

        Returns:
            有效句子列表
        """
        if not text:
            return []

        # 分句标记
        delimiters = r'([。！？])["\'\]]?[\s\n]*'
        sentences = re.split(delimiters, text)

        # 组合分句结果
        result = []
        buffer = []

        for s in sentences:
            if s in '。！？':
                buffer.append(s)
                if len(''.join(buffer)) >= self.min_chars:
                    result.append(''.join(buffer))
                buffer = []
            else:
                buffer.append(s)

        # 处理末尾句子
        if buffer and len(''.join(buffer)) >= self.min_chars:
            result.append(''.join(buffer))

        return [s.strip() for s in result if s.strip()]

    def split_paragraphs(self, text: str, min_para_chars: int = 50) -> List[str]:
        """
        按段落分割长文本。

        Args:
            text: 原始文本
            min_para_chars: 最小段落长度

        Returns:
            段落列表
        """
        if not text:
            return []

        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs
                if len(p.strip()) >= min_para_chars]

