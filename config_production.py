"""
Production Configuration for Vercel Deployment
Override config.py settings for production environment
"""
import os
from config import Config


class ProductionConfig(Config):
    """Production-specific configuration"""
    
    # Security
    DEBUG = False
    TESTING = False
    
    # Database - use environment variable (PostgreSQL for production)
    # SQLite won't work on Vercel due to ephemeral filesystem
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/quiz')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Test connections before using
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 3600,  # Recycle connections every hour
    }
    
    # Files & Uploads
    # Only /tmp is writable on Vercel
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    TEMPORARY_FOLDER = '/tmp'
    
    # Ensure temp upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Session & Security
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS - Set your production domain
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Vector Store - ChromaDB may not persist, consider alternatives
    CHROMA_DB_DIRECTORY = '/tmp/chroma_db'  # Temporary storage
    
    # Logging
    LOG_TO_STDOUT = True
    
    # API Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', None)  # Optional: Redis for distributed rate limiting
    
    # Static files
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    
    # Caching
    CACHE_TYPE = 'simple'  # Use Redis in production: 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', None)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Load appropriate config based on environment
config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get appropriate config based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
