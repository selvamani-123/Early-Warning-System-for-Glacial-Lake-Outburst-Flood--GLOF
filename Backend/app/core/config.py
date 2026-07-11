from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "glof_sentinel")
    environment: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
