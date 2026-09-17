from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = ""
    database_hostname: str = "localhost"
    database_port: int = 5432
    database_name: str = "diary_db"
    database_username: str = "postgres"
    database_password: str = ""
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    telegram_bot_token: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()