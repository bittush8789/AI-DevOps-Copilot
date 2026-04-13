from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    VERSION: str = "1.0.0"
    APP_NAME: str = "AI DevOps Copilot"
    
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_API_KEY: str = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    )
    BEDROCK_MAX_TOKENS: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
    BEDROCK_TEMPERATURE: float = float(os.getenv("BEDROCK_TEMPERATURE", "0.7"))
    
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "opensearch")
    
    OPENSEARCH_ENDPOINT: str = os.getenv("OPENSEARCH_ENDPOINT", "")
    OPENSEARCH_USERNAME: str = os.getenv("OPENSEARCH_USERNAME", "admin")
    OPENSEARCH_PASSWORD: str = os.getenv("OPENSEARCH_PASSWORD", "")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "devops-knowledge")
    
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "devops-copilot")
    
    CLOUDWATCH_LOG_GROUP: str = os.getenv(
        "CLOUDWATCH_LOG_GROUP", 
        "/aws/eks/ai-devops-copilot"
    )
    
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
