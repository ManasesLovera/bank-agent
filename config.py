from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Define variables with types
    db_url: str = Field(default="sqlite:///./test.db", validation_alias="DATABASE_URL")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # This inner class tells Pydantic where to find the file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a singleton instance to use across your project
settings = Settings()
