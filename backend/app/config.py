from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://immo:immo@localhost:5432/immo"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
