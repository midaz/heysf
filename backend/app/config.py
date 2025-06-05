"""
Configuration settings for the SF Government Document Analysis application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/sf_docs"
    
    # OpenAI
    openai_api_key: str
    
    # AWS S3
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket: str
    aws_region: str = "us-west-2"
    
    # Application
    app_name: str = "SF Document Analysis"
    debug: bool = False
    
    # Scraping
    scraping_interval_hours: int = 24
    base_url: str = "https://sfbos.org"
    
    # Analysis
    analysis_prompt: str = ""
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings() 