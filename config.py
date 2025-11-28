import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv


class Config:
    
    # PayPal Configuration - SIN CREDENCIALES HARDCODEADAS
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET') 
    PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
    
    
    # Validar que existan las variables de entorno
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("ERROR: PayPal credentials not configured. Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET environment variables.")
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-para-flask'
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("ERROR: Error de conexion con BD.")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
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