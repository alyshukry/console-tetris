from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    access_secret: str
    refresh_secret: str
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
