from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    model_name: str = "claude-haiku-4-5"
    max_tokens: int = 500
    top_k: int = 2
    similarity_threshold: float = 0.05
    docs_path: str = "data/docs.txt"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()