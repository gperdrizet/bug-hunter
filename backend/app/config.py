from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env in the backend dir first, then the project root
_here = Path(__file__).parent.parent  # backend/
_env_file = _here / ".env" if (_here / ".env").exists() else _here.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_env_file), env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://bughunter:bughunter@db:5432/bughunter"
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # LLM
    llm_provider: str = "openai"  # openai | anthropic | ollama
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    # Set to your llama.cpp / local OpenAI-compatible server URL, e.g. http://localhost:8080/v1
    openai_base_url: str | None = None
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-5"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codellama"

    # App URL used for links in emails
    app_url: str = "http://localhost:5173"

    # SMTP (leave empty for console logging in dev)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "admin@bug-hunter.perdrizet.org"


settings = Settings()
