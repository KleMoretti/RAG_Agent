from pydantic_settings import BaseSettings, SettingsConfigDict
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
    
    # RAG timeout configuration (seconds)
    # 如果RAG检索+LLM调用超过此时间，将降级为直接使用LLM（不带RAG上下文）
    rag_timeout_seconds: int = 25

    # Database (MySQL) configuration
    # Example: mysql+pymysql://user:password@localhost:3306/rag_agent?charset=utf8mb4
    database_url: str = (
        "mysql+pymysql://root:123456@127.0.0.1:3306/rag_agent?charset=utf8mb4"
    )

    # Security / JWT
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 2  # 2小时
    # Pydantic v2 + pydantic-settings
    model_config = SettingsConfigDict(
           env_file = ".env",
           case_sensitive = False,
    )
@lru_cache
def get_settings() -> Settings:
    s = Settings()
    Path(s.data_dir).mkdir(parents=True, exist_ok=True)
    Path(s.vector_index_path).parent.mkdir(parents=True, exist_ok=True)
    return s