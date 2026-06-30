"""Single source of truth for environment configuration.

Every environment variable is read here once, validated, and exposed as typed
settings. No other module should touch os.environ directly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import DEFAULT_DB_PATH, DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI / OpenAI-compatible (e.g. OpenRouter) access
    openai_api_key: str
    openai_base_url: str | None = None
    openai_model: str = DEFAULT_MODEL_NAME
    openai_temperature: float = DEFAULT_TEMPERATURE

    # Database
    db_path: str = DEFAULT_DB_PATH

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
