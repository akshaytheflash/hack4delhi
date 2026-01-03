from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/waterlogging"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    
    RATE_LIMIT_REPORTS_PER_HOUR: int = 10
    RATE_LIMIT_COMMENTS_PER_HOUR: int = 30
    
    DIGILOCKER_CLIENT_ID: Optional[str] = None
    DIGILOCKER_CLIENT_SECRET: Optional[str] = None
    DIGILOCKER_ENABLED: bool = False
    
    DATA_DIR: str = "data"
    SRTM_DATA_DIR: str = "data/srtm"
    WARD_GEOJSON_PATH: str = "data/delhi_wards.geojson"
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ORIGIN: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_cors_aliases(cls, data: dict) -> dict:
        if isinstance(data, dict):
            if "CORS_ORIGIN" in data and ("CORS_ORIGINS" not in data or not data["CORS_ORIGINS"]):
                data["CORS_ORIGINS"] = data["CORS_ORIGIN"]
        return data

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
