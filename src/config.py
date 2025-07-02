from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class _Config(BaseSettings):
    homeserver: str = None
    username: str = None
    password: str = None


config = _Config()