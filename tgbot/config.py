from pydantic import SecretStr, BaseModel
from pydantic_settings import BaseSettings as _BaseSettings, SettingsConfigDict


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


class CommonConfig(BaseSettings, env_prefix="COMMON_"):
    bot_token: SecretStr
    admins: list[int]
    use_mongo_storage: bool = False


class DbConfig(BaseSettings, env_prefix="DB_"):
    host: str
    port: int
    name: str


class YoomoneyConfig(BaseSettings, env_prefix="YOOMONEY_"):
    token: SecretStr
    wallet: str


class Config(BaseModel):
    common: CommonConfig
    db: DbConfig
    yoomoney: YoomoneyConfig


def create_app_config() -> Config:
    return Config(
        common=CommonConfig(),
        db=DbConfig(),
        yoomoney=YoomoneyConfig(),
    )


config = create_app_config()
