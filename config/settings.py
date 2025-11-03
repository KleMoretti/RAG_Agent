from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str | None = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_index_path: str = "./data/index/faiss.index"
    data_dir: str = "./data/knowledge/raw"  # 统一到 data/knowledge/ 目录
    log_level: str = "INFO"
    top_k: int = 10  # 增加检索数量，提高召回率
    max_chunk_tokens: int = 350
    chunk_overlap: int = 40

    # 知识库文件存储（统一到 data/knowledge/ 目录下）
    knowledge_base_raw_dir: str = "./data/knowledge/raw"
    knowledge_base_processed_dir: str = "./data/knowledge/processed"
    knowledge_base_index_path: str = "./data/embeddings/knowledge_base.faiss"

    # 用户上传文件存储（临时、个人文件）
    user_uploads_raw_dir: str = "./data/user_uploads/raw"
    user_uploads_processed_dir: str = "./data/user_uploads/processed"
    user_uploads_index_path: str = "./data/embeddings/user_uploads.faiss"

    # 检索优先级配置
    user_upload_score_threshold: float = 0.7  # 用户上传文件相似度阈值
    enable_priority_search: bool = True  # 是否启用优先检索

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
    # 创建知识库目录（统一到 data/knowledge/ 下）
    Path(s.data_dir).mkdir(parents=True, exist_ok=True)
    Path(s.vector_index_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 创建知识库目录（raw 和 processed）
    Path(s.knowledge_base_raw_dir).mkdir(parents=True, exist_ok=True)
    Path(s.knowledge_base_processed_dir).mkdir(parents=True, exist_ok=True)
    Path(s.knowledge_base_index_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 创建用户上传目录
    Path(s.user_uploads_raw_dir).mkdir(parents=True, exist_ok=True)
    Path(s.user_uploads_processed_dir).mkdir(parents=True, exist_ok=True)
    Path(s.user_uploads_index_path).parent.mkdir(parents=True, exist_ok=True)
    
    return s