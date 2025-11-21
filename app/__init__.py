from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuración según entorno
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
        # Configuración importante para producción
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
        )
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Asegurar la clave secreta
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key-for-dev')
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    
    # Registrar blueprints
    from app.routes.web import web_bp
    from app.carrito.routes import carrito_bp
    
    # Registrar nuevos blueprints para API
    from app.api.productos import bp as productos_bp
    from app.api.carrito import bp as carrito_api_bp
    from app.api.auth import bp as auth_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(carrito_api_bp)
    app.register_blueprint(auth_bp)
    
    print("✅ Blueprints registrados: Web, Carrito, Productos, Auth")
    
    # Configurar user_loader para Flask-Login
    from app.models.usuario import Usuario 
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Solo crear tablas si no existen (sin insertar datos)
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas de base de datos verificadas")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
    
    return app