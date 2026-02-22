import os
from datetime import timedelta

class Config:
    """Skill-Link Configuration"""
    
    # Secret key for JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skill-link-secret-key-2024')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'skill-link-jwt-secret-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///skilllink.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # CORS Configuration
    CORS_ORIGINS = ['*']
    
    # Platform Info
    PLATFORM_NAME = "Skill-Link"
    CHATBOT_NAME = "CareerBot"
    TEAM_NAME = "Team Arena"
    TEAM_MEMBERS = ["Soumy Chavhan", "Rudra Gupta", "Atharva Dongre", "Ishaan Ukey", "Avyesh Bhiwapurkar"]

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration Dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
