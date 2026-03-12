import os
from typing import List


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "瞳骋轨道机器人远程诊断与维护管理系统")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.database_url: str = os.getenv(
            "DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/tongcheng"
        )
        self.jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret")
        self.jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "720"))
        self.cors_allow_origins: List[str] = _split_csv(os.getenv("CORS_ALLOW_ORIGINS", ""))


settings = Settings()
