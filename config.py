from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port:int
    database_name: str
    database_username: str
    database_password:str
    secret_key:str
    algorithm:str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()