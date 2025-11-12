import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).parent.parent
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/students.db'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


def create_config_with_db(config_name='default', db_path=None):
    """Create a config object with optional custom database path."""
    config_class = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }.get(config_name, DevelopmentConfig)
    
    # Create a new config class with the custom database path
    if db_path:
        class CustomConfig(config_class):
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        return CustomConfig
    else:
        return config_class


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
