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
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas de base de datos verificadas/creadas")
            
            # Insertar datos iniciales si no existen
            inicializar_datos()
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
    
    return app

def inicializar_datos():
    """Insertar datos iniciales en la base de datos"""
    from app.models.models import Categoria, Producto
    from app.models.role import Role
    
    # Insertar roles si no existen
    if not Role.query.first():
        roles = [
            Role(nombre='Administrador'),
            Role(nombre='Cliente')
        ]
        db.session.add_all(roles)
        db.session.commit()
        print("✅ Roles insertados")
    
    # Insertar categorías si no existen
    if not Categoria.query.first():
        categorias = [
            Categoria(nombre='Consolas', descripcion='Consolas de videojuegos'),
            Categoria(nombre='Juegos', descripcion='Videojuegos físicos y digitales'),
            Categoria(nombre='Controles', descripcion='Controles y mandos'),
            Categoria(nombre='Accesorios', descripcion='Accesorios gaming')
        ]
        db.session.add_all(categorias)
        db.session.commit()
        print("✅ Categorías insertadas")
    
    # Insertar productos de ejemplo si no existen
    if not Producto.query.first():
        # Obtener categorías
        consolas = Categoria.query.filter_by(nombre='Consolas').first()
        juegos = Categoria.query.filter_by(nombre='Juegos').first()
        controles = Categoria.query.filter_by(nombre='Controles').first()
        accesorios = Categoria.query.filter_by(nombre='Accesorios').first()
        
        productos = [
            # Consolas
            Producto(
                nombre='XBOX SERIES X 2TB GALAXY BLACK LIMITED EDITION',
                descripcion='Consola Xbox Series X edición especial Galaxy Black',
                precio=17000.00,
                stock=10,
                imagen='/static/img/Imagenes/series x especial.png',
                categoria_id=consolas.id_categoria,
                activo=True
            ),
            Producto(
                nombre='CONSOLA XBOX SERIES X 1TB DIGITAL',
                descripcion='Consola Xbox Series X 1TB versión digital',
                precio=896.99,
                stock=15,
                imagen='/static/img/Imagenes/consolaseries.png',
                categoria_id=consolas.id_categoria,
                activo=True
            ),
            Producto(
                nombre='PLAY STATION 5 1TB',
                descripcion='Consola PlayStation 5 1TB',
                precio=11996.99,
                stock=8,
                imagen='/static/img/Imagenes/play5.png',
                categoria_id=consolas.id_categoria,
                activo=True
            ),
            
            # Juegos
            Producto(
                nombre='CALL OF DUTY BLACK OPS 6',
                descripcion='Juego Call of Duty Black Ops 6 para Xbox',
                precio=1200.00,
                stock=50,
                imagen='/static/img/Imagenes/CODBO6.png',
                categoria_id=juegos.id_categoria,
                activo=True
            ),
            Producto(
                nombre='HOGWARTS LEGACY',
                descripcion='Juego Hogwarts Legacy para Xbox',
                precio=1000.34,
                stock=30,
                imagen='/static/img/Imagenes/howards.png',
                categoria_id=juegos.id_categoria,
                activo=True
            ),
            Producto(
                nombre='MORTAL KOMBAT 1',
                descripcion='Juego Mortal Kombat 1 para Xbox',
                precio=651.00,
                stock=25,
                imagen='/static/img/Imagenes/mk1_xbox.png',
                categoria_id=juegos.id_categoria,
                activo=True
            ),
            
            # Controles
            Producto(
                nombre='CONTROL XBOX INALÁMBRICO CARBON BLACK',
                descripcion='Control Xbox inalámbrico color negro carbón',
                precio=1096.99,
                stock=20,
                imagen='/static/img/Imagenes/controlxboxblack.png',
                categoria_id=controles.id_categoria,
                activo=True
            ),
            Producto(
                nombre='CONTROL PLAYSTATION 5 DUALSENSE WHITE',
                descripcion='Control PlayStation 5 DualSense color blanco',
                precio=1699.99,
                stock=15,
                imagen='/static/img/Imagenes/controlplay5.png',
                categoria_id=controles.id_categoria,
                activo=True
            ),
            
            # Accesorios
            Producto(
                nombre='AUDÍFONOS GAMER PROFESIONALES',
                descripcion='Audífonos gaming con sonido surround 7.1',
                precio=760.00,
                stock=25,
                imagen='/static/img/Audifonos_Gamer.jpg',
                categoria_id=accesorios.id_categoria,
                activo=True
            )
        ]
        
        db.session.add_all(productos)
        db.session.commit()
        print("✅ Productos de ejemplo insertados")