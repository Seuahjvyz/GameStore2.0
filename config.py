import os
import re
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-para-flask'
    
    # Obtener y limpiar DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Limpiar comillas si existen
        DATABASE_URL = DATABASE_URL.strip('"\'')
        
        # Asegurar que use postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"✅ Usando PostgreSQL en Render: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Render PostgreSQL'}")
    else:
        # PostgreSQL local (fallback)
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/GameStore'
        print("⚠️  Usando PostgreSQL local")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}