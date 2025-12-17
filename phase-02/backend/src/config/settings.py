from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False,  # Allow case-insensitive matching
        extra="ignore",
    )

    # Database settings
    database_url: str 

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

# Create a single instance of settings
settings = Settings()
