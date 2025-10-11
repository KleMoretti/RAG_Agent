import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer  # type: ignore

class Embedder:
    """
    文本向量化工具，使用预训练模型将文本转换为向量。
    支持向量归一化，适配 VectorStore。
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化文本向量化模型。

        Args:
            model_name: sentence-transformers 模型名称
        """
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """
        将文本列表转换为向量。

        Args:
            texts: 待向量化的文本列表
            normalize: 是否对向量进行 L2 归一化

        Returns:
            shape=(N,D) 的 float32 向量数组
        """
        vectors = self.model.encode(texts, convert_to_numpy=True)
        vectors = vectors.astype(np.float32)
        if normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
            vectors = vectors / norms
        return vectors

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        将文本列表转换为向量（encode 方法的别名，用于兼容 Searcher 接口）。

        Args:
            texts: 待向量化的文本列表

        Returns:
            shape=(N,D) 的归一化 float32 向量数组
        """
        return self.encode(texts, normalize=True)