from typing import List
import numpy as np

class Embedder:
    """
    文本嵌入生成器，封装 sentence-transformers。
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        生成文本嵌入，输出 float32 并归一化。

        Args:
            texts: 文本列表

        Returns:
            shape=(N, D) 的归一化嵌入矩阵
        """
        vectors = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.astype(np.float32)

