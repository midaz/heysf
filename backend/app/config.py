"""
Configuration settings for the SF Government Document Analysis application.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


def get_custom_prompt() -> str:
    """Load the custom prompt from prompts.txt file."""
    prompts_file = Path(__file__).parent.parent / "prompts.txt"
    
    if prompts_file.exists():
        try:
            content = prompts_file.read_text().strip()
            # Return the first non-comment, non-empty line as the prompt
            lines = content.split('\n')
            prompt_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    prompt_lines.append(line)
            
            if prompt_lines:
                return '\n'.join(prompt_lines)
        except Exception as e:
            print(f"Error reading prompts.txt: {e}")
    
    # Fallback default prompt
    return """
Please analyze this SF Board of Supervisors meeting minutes and provide:

1. **Executive Summary**: Brief overview of key outcomes
2. **Key Decisions**: List votes, resolutions, ordinances  
3. **Budget Impact**: Financial implications and costs
4. **Action Items**: Follow-up tasks and deadlines
5. **Policy Changes**: New or modified policies
6. **Community Impact**: How this affects SF residents
"""


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
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings() 