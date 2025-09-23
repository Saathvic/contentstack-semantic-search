"""
Configuration management for Contentstack Semantic Search
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management"""

    # Contentstack Configuration
    CONTENTSTACK_STACK_API_KEY: str = os.getenv('CONTENTSTACK_STACK_API_KEY', '').strip()
    CONTENTSTACK_DELIVERY_TOKEN: str = os.getenv('CONTENTSTACK_DELIVERY_TOKEN', '').strip()
    CONTENTSTACK_ENVIRONMENT: str = os.getenv('CONTENTSTACK_ENVIRONMENT', 'development').strip()
    CONTENTSTACK_REGION: str = os.getenv('CONTENTSTACK_REGION', 'eu').strip()  # eu or us
    CONTENTSTACK_API_BASE_URL: str = os.getenv('CONTENTSTACK_API_BASE_URL', f"https://{CONTENTSTACK_REGION}-cdn.contentstack.com/v3").strip()

    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv('PINECONE_API_KEY', '').strip()
    PINECONE_INDEX_NAME: str = os.getenv('PINECONE_INDEX_NAME', 'contentstack-products').strip()

    # Gemini/LLM Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '').strip()

    # Ngrok Configuration
    NGROK_AUTH_TOKEN: str = os.getenv('NGROK_AUTH_TOKEN', '').strip()
    NGROK_DOMAIN: str = os.getenv('NGROK_DOMAIN', 'destined-mammoth-flowing.ngrok-free.app').strip()
    NGROK_FRONTEND_DOMAIN: str = os.getenv('NGROK_FRONTEND_DOMAIN', 'unlifted-sisterlike-melinda.ngrok-free.dev').strip()
    NGROK_FRONTEND_AUTH_TOKEN: str = os.getenv('NGROK_FRONTEND_AUTH_TOKEN', '').strip()
    NGROK_WEBHOOK_DOMAIN: str = os.getenv('NGROK_WEBHOOK_DOMAIN', 'destined-mammoth-flowing.ngrok-free.app').strip()

    # Flask Configuration
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Search Configuration
    DEFAULT_TOP_K: int = int(os.getenv('DEFAULT_TOP_K', '5'))
    MAX_TOP_K: int = int(os.getenv('MAX_TOP_K', '20'))

    @classmethod
    def validate_contentstack_config(cls) -> bool:
        """Validate Contentstack configuration"""
        required = [
            cls.CONTENTSTACK_STACK_API_KEY,
            cls.CONTENTSTACK_DELIVERY_TOKEN
        ]
        return all(required)

    @classmethod
    def validate_pinecone_config(cls) -> bool:
        """Validate Pinecone configuration"""
        return bool(cls.PINECONE_API_KEY)

    @classmethod
    def validate_gemini_config(cls) -> bool:
        """Validate Gemini configuration"""
        return bool(cls.GEMINI_API_KEY)

    @classmethod
    def get_contentstack_headers(cls) -> dict:
        """Get Contentstack API headers"""
        return {
            "api_key": cls.CONTENTSTACK_STACK_API_KEY,
            "access_token": cls.CONTENTSTACK_DELIVERY_TOKEN,
            "Content-Type": "application/json"
        }

    @classmethod
    def get_status(cls) -> dict:
        """Get configuration status"""
        return {
            "contentstack": {
                "configured": cls.validate_contentstack_config(),
                "region": cls.CONTENTSTACK_REGION,
                "environment": cls.CONTENTSTACK_ENVIRONMENT
            },
            "pinecone": {
                "configured": cls.validate_pinecone_config(),
                "index_name": cls.PINECONE_INDEX_NAME
            },
            "gemini": {
                "configured": cls.validate_gemini_config()
            },
            "ngrok": {
                "domain": cls.NGROK_DOMAIN
            }
        }

# Global config instance
config = Config()