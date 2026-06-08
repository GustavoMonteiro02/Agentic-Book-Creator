from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic Book Creator"
    database_url: str = "sqlite:///./agentic_book_creator.db"
    langsmith_tracing: bool = False
    langsmith_project: str = "agentic-book-creator"
    pinecone_index_name: str = "agentic-book-creator"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
