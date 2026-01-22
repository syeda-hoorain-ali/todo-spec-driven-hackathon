from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Kafka Configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "todo-chatbot-backend"
    kafka_group_id: str = "todo-chatbot-group"
    kafka_security_protocol: str = "SASL_SSL"
    kafka_sasl_mechanism: str = "SCRAM-SHA-256"
    kafka_sasl_username: Optional[str] = None
    kafka_sasl_password: Optional[str] = None
    kafka_auto_offset_reset: str = "earliest"
    kafka_enable_auto_commit: bool = True

    # Application Configuration
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()