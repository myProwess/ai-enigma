"""
Configuration module for the NewsAPI Flask backend.
Loads environment variables and exposes application settings.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Config:
    """Application configuration sourced from environment variables."""

    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    DEFAULT_COUNTRY: str = os.getenv("DEFAULT_COUNTRY", "us")
    MAX_PAGE_SIZE: int = 100
    DAILY_REQUEST_LIMIT: int = int(os.getenv("DAILY_REQUEST_LIMIT", "100"))
    DATA_FILE_PATH: str = os.getenv(
        "DATA_FILE_PATH",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "news_data.json"),
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv(
        "LOG_FILE",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "app.log"),
    )

    @classmethod
    def validate(cls) -> bool:
        """Check that all required configuration values are present."""
        if not cls.NEWS_API_KEY:
            raise ValueError(
                "NEWS_API_KEY is not set. "
                "Please create a .env file with NEWS_API_KEY=your_key_here"
            )
        return True
