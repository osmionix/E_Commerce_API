from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    EMAIL_FROM: str = "noreply@example.com"
    
    class Config:
        env_file = ".env"

settings = Settings()