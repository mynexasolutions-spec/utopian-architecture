import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

# Load environment variables from .env
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_utopia_interior_2026')
    
    # SQLAlchemy Configuration
    # Fallback to local SQLite if DATABASE_URL is not set
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_default_path = os.path.join(basedir, 'instance', 'contacts.db')
    
    # The Supabase PostgreSQL URI (or SQLite for local fallback)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{db_default_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
    }
    
    # Cloudinary configuration
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Dictionary to easily select configuration
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
