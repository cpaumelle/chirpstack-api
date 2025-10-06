from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    chirpstack_url: str = "http://10.44.1.110:8080"
    chirpstack_api_key: str
    chirpstack_tenant_id: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
