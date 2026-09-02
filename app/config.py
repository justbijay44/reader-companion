from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    BATCH_SIZE: int = 32

    QDRANT_URL: str
    QDRANT_COLLECTION: str = "reading_companion"

settings = Settings()