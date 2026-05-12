from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


def parse_size(value: str | int) -> int:
    if isinstance(value, int):
        return value
    value = value.strip().upper()
    units = {"TB": 1024**4, "GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}
    for suffix, multiplier in units.items():
        if value.endswith(suffix):
            return int(float(value[: -len(suffix)]) * multiplier)
    return int(value)


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    UPLOAD_DIR: str = "uploads"
    STORAGE_LIMIT: str = "10GB"

    @property
    def storage_limit_bytes(self) -> int:
        return parse_size(self.STORAGE_LIMIT)

    model_config = {"env_file": str(BASE_DIR / ".env")}


settings = Settings()
