from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
import os
import atexit
import datetime 
from flask_mail import Mail, Message
from app.routes.captcha import captcha_bp
from sqlalchemy import text

# IMPORTAR PAYPAL SDK
import paypalrestsdk

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

#------------------------------------ Scheduler para mantener la BD activa
scheduler = BackgroundScheduler()

def keep_db_alive(app):
    """Ejecuta una query simple cada 4 minutos para mantener activa la BD de Neon"""
    with app.app_context():
        try:
            # Forma correcta de ejecutar SQL simple
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            print("✅ Ping a BD ejecutado - Neon activa")
        except Exception as e:
            print(f"❌ Error en ping a BD: {e}")

def create_app():
    app = Flask(__name__)
    
    # Configuración según entorno
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            SESSION_COOKIE_NAME='session',
            SESSION_PERMANENT=False,
            PERMANENT_SESSION_LIFETIME=1800,
        )
    else:
        app.config.from_object('config.DevelopmentConfig')
        app.config.update(
            SESSION_PERMANENT=False,
            PERMANENT_SESSION_LIFETIME=1600,
            SESSION_REFRESH_EACH_REQUEST=True
        )
    
    # 🔥 IMPORTANTE: Verificar que las claves de reCAPTCHA estén cargadas
    print(f"🔑 reCAPTCHA Site Key configurada: {'✅ Sí' if app.config.get('RECAPTCHA_SITE_KEY') else '❌ No'}")
    print(f"🔑 reCAPTCHA Secret Key configurada: {'✅ Sí' if app.config.get('RECAPTCHA_SECRET_KEY') else '❌ No'}")
    
    # 🔥 Mover el context processor DESPUÉS de que app.config esté configurado
    @app.context_processor
    def utility_processor():
        return {
            'recaptcha_site_key': app.config.get('RECAPTCHA_SITE_KEY', '')
        }
    
    # Asegurar la clave secreta
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key-for-dev')
    
    # CONFIGURACIÓN DE PAYPAL
    app.config['PAYPAL_CLIENT_ID'] = os.environ.get('PAYPAL_CLIENT_ID')
    app.config['PAYPAL_CLIENT_SECRET'] = os.environ.get('PAYPAL_CLIENT_SECRET')
    app.config['PAYPAL_MODE'] = os.environ.get('PAYPAL_MODE', 'sandbox')
    
    # INICIALIZAR PAYPAL SDK
    paypalrestsdk.configure({
        "mode": app.config['PAYPAL_MODE'],
        "client_id": app.config['PAYPAL_CLIENT_ID'],
        "client_secret": app.config['PAYPAL_CLIENT_SECRET']
    })
    
    print(f"PayPal SDK configurado - Modo: {app.config['PAYPAL_MODE']}")
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    mail.init_app(app)

    #Manejador de Errores 
    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'success':False,
                'error': "Recurso no encontrado",
                'path': request.path,
                'code': 404
            }), 404
        return render_template('/errores/404.html'), 404
    
    @app.before_request
    def check_session_timeout():
        """Verificar tiempo de inactividad de la sesión"""
        # Excluir rutas públicas que no requieren sesión
        rutas_publicas = ['/login', '/api/login', '/registro', '/api/registro', '/', '/static']
        
        # Si la ruta actual es pública, permitir acceso sin verificar
        if any(request.path.startswith(ruta) for ruta in rutas_publicas):
            return None
        
        if 'user_id' in session:
            last_activity = session.get('last_activity')
            
            if last_activity:
                # Convertir string a datetime si está guardado como string
                if isinstance(last_activity, str):
                    try:
                        last_activity = datetime.datetime.fromisoformat(last_activity)
                    except:
                        last_activity = None
                
                if last_activity:
                    # Si pasaron más de 30 minutos sin actividad, cerrar sesión
                    tiempo_inactivo = (datetime.datetime.now() - last_activity).seconds
                    if tiempo_inactivo > 1800:  # 30 minutos
                        session.clear()
                        # Si es petición API, devolver JSON
                        if request.path.startswith('/api/'):
                            return jsonify({
                                'success': False, 
                                'error': 'Sesión expirada',
                                'redirect': '/login'
                            }), 401
                        # Si es página web, redirigir a login
                        return redirect(url_for('web.login'))
            
            # Actualizar última actividad (guardar como string ISO para evitar problemas de serialización)
            session['last_activity'] = datetime.datetime.now().isoformat()
    
    # Registrar blueprints
    from app.routes.web import web_bp
    from app.carrito.routes import carrito_bp    
    from app.api.productos import bp as productos_bp
    from app.api.carrito import bp as carrito_api_bp
    from app.api.auth import bp as auth_bp  
    from app.routes.chatbot import chatbot_bp
    from app.routes.verification import verification_bp
    
    # BLUEPRINT 
    app.register_blueprint(web_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(carrito_api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chatbot_bp) 
    app.register_blueprint(verification_bp) 
    app.register_blueprint(captcha_bp)
    
    print("Blueprints registrados: Web, Carrito, Productos, Auth, Chatbot")
    
    # Configurar user_loader para Flask-Login
    from app.models.usuario import Usuario 
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Solo crear tablas si no existen (sin insertar datos)
    with app.app_context():
        try:
            db.create_all()
            print(" Tablas de base de datos verificadas")
        except Exception as e:
            print(f" Error creando tablas: {e}")
    
    # Iniciar scheduler para mantener BD activa (solo si no está corriendo)
    if not scheduler.running:
        # Agregar job que se ejecuta cada 4 minutos
        scheduler.add_job(
            func=keep_db_alive,
            args=[app],
            trigger="interval",
            minutes=4,
            id='keep_neon_alive',
            name='Mantener BD Neon activa',
            replace_existing=True
        )
        scheduler.start()
        print("✅ Scheduler iniciado - BD Neon se mantendrá activa")
        
        # Asegurar que el scheduler se detenga cuando la app se cierre
        atexit.register(lambda: scheduler.shutdown())
    
    return app