import os
import re
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-para-flask'
    
    # Obtener y limpiar DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI')
    
    if DATABASE_URL:
        # Limpiar comillas si existen
        DATABASE_URL = DATABASE_URL.strip('"\'')
        
        # Asegurar que use postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"✅ Usando Neon: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Neon'}")
    else:
        # PostgreSQL local (fallback)
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/GameStore'
        print("⚠️  Usando PostgreSQL local")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # ✅ Verifica que la conexión esté viva
        'pool_recycle': 300,    # ✅ Recicla conexiones cada 5 minutos
        'connect_args': {
            'sslmode': 'require',
            'sslrootcert': None,
            'connect_timeout': 10,  # ✅ Timeout de conexión de 10 segundos
            'keepalives': 1,        # ✅ Mantener conexión viva
            'keepalives_idle': 30,  # ✅ Verificar cada 30 segundos
            'keepalives_interval': 10,
            'keepalives_count': 5
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