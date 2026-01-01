from pydantic_settings import BaseSettings, SettingsConfigDict
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False,  # Allow case-insensitive matching
        extra="ignore",
    )

    # Neon Database settings
    neon_database_url: str
    neon_api_key: str

    # MCP server settings
    mcp_server_url: str = "http://localhost:8001"

    # Better Auth settings
    better_auth_secret: str
    jwt_algorithm: str = "EdDSA"

    # Application settings
    environment: str = "development"
    app_name: str = "Secured Todo API"
    version: str = "1.0.0"
    debug: bool = False

    # Token settings
    access_token_expire_minutes: int = 30

    frontend_base_url: str = "http://localhost:3000"

    # LLM settings
    google_api_key: str
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def configure_llm_provider(self):
        """Configure the global LLM provider for all agents"""
        set_tracing_disabled(True)
        set_default_openai_api("chat_completions")

        external_client = AsyncOpenAI(
            api_key=self.google_api_key,
            base_url=self.gemini_base_url,
        )
        set_default_openai_client(external_client)

# Create a single instance of settings
settings = Settings()
