import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "E-Commerce Intelligence Engine"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce_intelligence.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days
    
    # External APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SIMILARWEB_API_KEY: str = os.getenv("SIMILARWEB_API_KEY", "")
    
    # Scraping Settings
    SCRAPER_TIMEOUT: int = 15
    MAX_CONCURRENT_SCRAPES: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()