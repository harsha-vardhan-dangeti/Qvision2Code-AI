import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Figma API Configuration
    FIGMA_ACCESS_TOKEN: Optional[str] = os.getenv("FIGMA_ACCESS_TOKEN")
    FIGMA_BASE_URL: str = os.getenv("FIGMA_BASE_URL", "https://api.figma.com/v1")
    FIGMA_TIMEOUT: int = int(os.getenv("FIGMA_TIMEOUT", "30"))
    FIGMA_MAX_RETRIES: int = int(os.getenv("FIGMA_MAX_RETRIES", "3"))
    
    # Backend Configuration
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Analysis Configuration
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT", "300"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "2"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.FIGMA_ACCESS_TOKEN:
            print("Warning: FIGMA_ACCESS_TOKEN not set. Figma integration will not work.")
            return False
        return True
    
    @classmethod
    def get_figma_config(cls):
        """Get Figma configuration"""
        from app.figma_service import FigmaConfig
        
        return FigmaConfig(
            access_token=cls.FIGMA_ACCESS_TOKEN,
            base_url=cls.FIGMA_BASE_URL,
            timeout=cls.FIGMA_TIMEOUT,
            max_retries=cls.FIGMA_MAX_RETRIES
        )
