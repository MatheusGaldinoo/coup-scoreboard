from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Conexão padrão para o postgres local do docker-compose
    DATABASE_URL: str = "postgresql+asyncpg://coup_user:coup_password@localhost:5433/coup_scoreboard"
    
    class Config:
        env_file = ".env"

settings = Settings()
