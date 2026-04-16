from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = ""
    env: str = "development"

    # RAG settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k_results: int = 5

    #ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()