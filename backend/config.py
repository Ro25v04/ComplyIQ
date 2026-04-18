# Loads environment variables from .env into a settings object that any file can import and use


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    groq_api_key: str = ""
    cohere_api_key: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
