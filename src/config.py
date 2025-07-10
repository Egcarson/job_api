import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import EmailStr

env = os.getenv("ENV", "local")

#this logic is to load environments for local, docker and ci - test
if env == "docker":
    env_file = ".env.docker"
elif env == "test":
    env_file = ".env.test"
else:
    env_file = ".env.local"

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: Optional[str] = None
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=env_file,
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()

Config = get_settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup =True