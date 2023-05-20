from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    name: str
    port: int = 27017


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_mongo_storage: bool


@dataclass
class Miscellaneous:
    yoomoney_token: str
    yoomoney_wallet: str


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous = None
    db: DbConfig = None


def load_config(path: str = '.env') -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=env.list('ADMINS', subcast=int),
            use_mongo_storage=env.bool("USE_MONGO_STORAGE"),

        ),
        db=DbConfig(host=env.str('DB_HOST'),
                    port=env.int('DB_PORT'),
                    name=env.str('DB_NAME')),

        misc=Miscellaneous(yoomoney_token=env.str('YOOMONEY_TOKEN'),
                           yoomoney_wallet=env.str('YOOMONEY_WALLET'))
    )


config = load_config('.env')
