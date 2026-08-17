from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    data_dir: str = "geospatial/outputs/lst"
    max_optimization_hotspots: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()
