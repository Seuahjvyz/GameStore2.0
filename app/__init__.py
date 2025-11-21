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
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    
    # Registrar blueprints
    from app.routes.web import web_bp
    from app.carrito.routes import carrito_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(carrito_bp)
    
    print("✅ Blueprints registrados: Web y Carrito")
    
    # Configurar user_loader para Flask-Login
    from app.models.usuario import Usuario 
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas de base de datos verificadas/creadas")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
    
    return app