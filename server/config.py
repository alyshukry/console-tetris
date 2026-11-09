from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    access_secret: str
    refresh_secret: str
    database_url: str
    min_players_to_start: int = 2
    ready_countdown_seconds: int = 5
    gravity_in_seconds: float = .5

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
