from pydantic_settings import BaseSettings, SettingsConfigDict
from openai import AsyncOpenAI

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False,  # Allow case-insensitive matching
        extra="ignore",
    )

    # Neon Database settings
    database_url: str

    # MCP server settings
    mcp_server_url: str = "http://localhost:8080"

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
    gemini_api_key: str
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Kafka settings
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "taskflow-backend"
    kafka_group_id: str = "taskflow-group"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str
    kafka_sasl_username: str
    kafka_sasl_password: str
    kafka_auto_offset_reset: str = "earliest"
    kafka_enable_auto_commit: bool = True

    def configure_llm_provider(self):
        """Configure the global LLM provider for all agents"""
        # Placeholder for LLM provider configuration
        # In a real implementation, this would configure the LLM provider
        pass

# Create a single instance of settings
settings = Settings()
