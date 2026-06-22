from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Config(BaseSettings):
    telegram_token: str
    dialect: str
    driver: str
    username: str
    password: str
    db_host: str
    port: int
    database: str
    log_level: str
    log_format: str
    api_token: str
    base_url: str
    client_max_retries: int
    rag_max_retries: int
    model_path: str

    # build DB URL from other fields at runtime
    @property
    def db_url(self) -> str:
        return f"{self.dialect}+{self.driver}://{self.username}:{self.password}@{self.db_host}:{self.port}/{self.database}"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


config = Config()
