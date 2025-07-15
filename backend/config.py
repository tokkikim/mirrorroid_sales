import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://mirat_admin:mirat_password@localhost:5432/mirat_studio"
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379"
    
    # API 키 설정
    OPENAPI_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    NAVER_MAP_API_KEY: Optional[str] = None
    
    # 공공데이터 API 키
    DATA_GO_KR_API_KEY: Optional[str] = None
    SEOUL_OPEN_DATA_API_KEY: Optional[str] = None
    
    # JWT 설정
    SECRET_KEY: str = "mirat_studio_secret_key_2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 애플리케이션 설정
    APP_NAME: str = "미라트 스튜디오 가맹 추천 시스템"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS 설정
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # 데이터 수집 설정
    DATA_COLLECTION_INTERVAL: int = 3600  # 1시간
    MAX_API_REQUESTS_PER_MINUTE: int = 60
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "uploads"
    
    # 보고서 설정
    REPORT_FOLDER: str = "reports"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()