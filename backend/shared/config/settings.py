import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Application
    APP_NAME: str = 'Chariot Security Platform'
    APP_VERSION: str = '1.0.0'
    DEBUG: bool = Field(default=False, env='DEBUG')
    ENVIRONMENT: str = Field(default='development', env='ENVIRONMENT')
    
    # Security
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    JWT_SECRET_KEY: str = Field(..., env='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = Field(..., env='ENCRYPTION_KEY')
    
    # Database
    DATABASE_URL: str = Field(..., env='DATABASE_URL')
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_HOST: str = Field(default='localhost', env='REDIS_HOST')
    REDIS_PORT: int = Field(default=6379, env='REDIS_PORT')
    REDIS_PASSWORD: Optional[str] = Field(default=None, env='REDIS_PASSWORD')
    REDIS_DB: int = 0
    REDIS_QUEUE_DB: int = 1
    REDIS_CACHE_DB: int = 2
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env='OPENAI_API_KEY')
    ALCHEMY_API_KEY: Optional[str] = Field(default=None, env='ALCHEMY_API_KEY')
    INFURA_API_KEY: Optional[str] = Field(default=None, env='INFURA_API_KEY')
    ETHERSCAN_API_KEY: Optional[str] = Field(default=None, env='ETHERSCAN_API_KEY')
    
    # Payment Services
    PAYSTACK_SECRET_KEY: str = Field(..., env='PAYSTACK_SECRET_KEY')
    PAYSTACK_PUBLIC_KEY: str = Field(..., env='PAYSTACK_PUBLIC_KEY')
    
    # USDT Contract Addresses
    USDT_ETHEREUM: str = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
    USDT_POLYGON: str = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
    USDT_BSC: str = '0x55d398326f99059fF775485246999027B3197955'
    
    # Blockchain RPC URLs
    ETHEREUM_RPC_URL: str = Field(..., env='ETHEREUM_RPC_URL')
    POLYGON_RPC_URL: str = Field(..., env='POLYGON_RPC_URL')
    BSC_RPC_URL: str = Field(..., env='BSC_RPC_URL')
    
    # ML Model Paths
    MODEL_FRAUD_DETECTION: str = 'ml-models/fraud-detection/model.pkl'
    MODEL_ANOMALY_DETECTION: str = 'ml-models/anomaly-detection/model.pkl'
    MODEL_RISK_SCORING: str = 'ml-models/risk-scoring/model.pkl'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS
    CORS_ORIGINS: list = ['http://localhost:3000', 'http://localhost:5173']
    
    # Logging
    LOG_LEVEL: str = Field(default='INFO', env='LOG_LEVEL')
    
    # Email (for alerts)
    SMTP_HOST: Optional[str] = Field(default=None, env='SMTP_HOST')
    SMTP_PORT: int = Field(default=587, env='SMTP_PORT')
    SMTP_USER: Optional[str] = Field(default=None, env='SMTP_USER')
    SMTP_PASSWORD: Optional[str] = Field(default=None, env='SMTP_PASSWORD')
    
    # Webhook URLs
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env='SLACK_WEBHOOK_URL')
    DISCORD_WEBHOOK_URL: Optional[str] = Field(default=None, env='DISCORD_WEBHOOK_URL')
    
    class Config:
        env_file = '.env'
        case_sensitive = True

settings = Settings()
