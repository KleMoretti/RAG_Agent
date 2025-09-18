from pydantic import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str | None = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_index_path: str = "./data/index/faiss.index"
    data_dir: str = "./data/raw"
    log_level: str = "INFO"
    top_k: int = 5
    max_chunk_tokens: int = 350
    chunk_overlap: int = 40

    # LLM configuration
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 30.0

    # Pydantic v2 style config (replaces inner Config class)
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    Path(s.data_dir).mkdir(parents=True, exist_ok=True)
    Path(s.vector_index_path).parent.mkdir(parents=True, exist_ok=True)
    return s