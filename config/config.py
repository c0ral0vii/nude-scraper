from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    S3_ENDPOINT: str
    ACCESS_KEY: str
    SECRET_KEY: str
    BUCKET_NAME: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

options = Settings()
PATH_TO_SAVE = 'temp'