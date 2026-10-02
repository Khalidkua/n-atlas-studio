from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "N-ATLAS Studio"
    app_version: str = "0.1.0"

    # N-ATLaS provider configuration
    provider: str = "mock"
    model_name: str = "NCAIR1/N-ATLaS"

    # Remote inference configuration
    remote_api_url: str = ""
    remote_api_key: str = ""
    remote_chat_url: str = ""
    remote_generate_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
