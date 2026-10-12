from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash-lite"
    chroma_persist_dir: str = "./chroma_data"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    max_file_size_mb: int = 50
    max_question_length: int = 2000
    gemini_max_retries: int = 3
    gemini_retry_delay: float = 1.0
    supported_languages: list[str] = ["en"]
    adaptive_chunking: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
