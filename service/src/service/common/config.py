from pydantic_settings import BaseSettings

class Config(BaseSettings):
    clickhouse_url: str = "clickhousedb://default:default@clickhouse:8123/gold"

settings = Config()
