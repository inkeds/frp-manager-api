from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "FRP Manager API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]  # 替换为实际的前端域名
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # 在生产环境中必须更改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./frp_manager.db")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # WHMCS配置
    WHMCS_URL: Optional[str] = os.getenv("WHMCS_URL")
    WHMCS_API_IDENTIFIER: Optional[str] = os.getenv("WHMCS_API_IDENTIFIER")
    WHMCS_API_SECRET: Optional[str] = os.getenv("WHMCS_API_SECRET")
    
    # Sentry配置
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # 速率限制配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
