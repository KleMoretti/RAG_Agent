import re
from typing import List

class Preprocessor:
    """
    文本预处理：清洗、分句。
    """

    def clean_text(self, text: str) -> str:
        """
        清洗文本，去除多余空白和标点。

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text.strip()

    def split_sentences(self, text: str) -> List[str]:
        """
        按中文句号、问号、感叹号分句。

        Args:
            text: 清洗后的文本

        Returns:
            句子列表
        """
        sentences = re.split(r'[。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
