from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Currency Converter API"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    class Config:
        case_sensitive = True

settings = Settings()