from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data_quality.db"
    cors_origins: str = "http://localhost:5173"
    demo_mode: bool = True
    collibra_base_url: str = ""
    collibra_client_id: str = ""
    collibra_client_secret: str = ""
    soda_api_url: str = ""
    soda_api_key: str = ""
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_database: str = ""
    snowflake_schema: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
