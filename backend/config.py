from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM provider: anthropic | openai | gemini
    LLM_PROVIDER: str = "anthropic"

    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Swap to real Beefree MCP URL when you have credentials
    BEEFREE_MCP_URL: str = "http://localhost:8001"
    BEEFREE_CLIENT_ID: str = ""
    BEEFREE_CLIENT_SECRET: str = ""

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
