from flask import Blueprint, redirect, url_for, flash, request, jsonify, render_template, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app.models.usuario import Usuario
from app import db, mail
import os
import threading

verification_bp = Blueprint('verification', __name__)

# -------------------- TOKEN --------------------

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt='email-verification', max_age=expiration)
    except:
        return None

# -------------------- BASE URL AUTO --------------------

def get_base_url():
    if os.getenv('RENDER_EXTERNAL_URL'):
        return os.getenv('RENDER_EXTERNAL_URL')
    else:
        return "http://localhost:5000"

# -------------------- EMAIL --------------------

def send_verification_email(user_email, username, token):
    
    base_url = get_base_url()
    verification_url = f"{base_url}/verify-email/{token}"
    
    html_content = render_template(
        'correos/verificacion.html', 
        username=username,
        verification_url=verification_url
    )

    msg = Message(
        subject="Verifica tu cuenta - GameStore",
        recipients=[user_email],
        html=html_content
    )

    try:
        mail.send(msg)
        print(f"[EMAIL OK] {user_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

# -------------------- THREAD --------------------

def enviar_correo_async(app, email, username, token):
    with app.app_context():
        try:
            print(f"[EMAIL] Enviando a {email}")
            send_verification_email(email, username, token)
        except Exception as e:
            print(f"[ERROR HILO EMAIL] {e}")

def lanzar_hilo_correo(email, username, token):
    app = current_app._get_current_object()

    hilo = threading.Thread(
        target=enviar_correo_async,
        args=(app, email, username, token)
    )

    hilo.daemon = True
    hilo.start()

# -------------------- VERIFICAR --------------------

@verification_bp.route('/verify-email/<token>')
def verify_email(token):
    email = verify_verification_token(token)
    
    if not email:
        flash('El enlace de verificación ha expirado o es inválido.', 'danger')
        return redirect(url_for('web.login'))
    
    usuario = Usuario.query.filter_by(correo=email).first()
    
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('web.login'))
    
    if usuario.verificacion:
        flash('Tu cuenta ya estaba verificada.', 'info')
    else:
        usuario.verificacion = True
        usuario.email_verification_token = None
        db.session.commit()
        flash('Cuenta verificada exitosamente.', 'success')
    
    return redirect(url_for('web.login'))

# -------------------- REENVÍO --------------------

@verification_bp.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        usuario = Usuario.query.filter_by(correo=email).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if usuario.verificacion:
            return jsonify({'error': 'Cuenta ya verificada'}), 400
        
        token = generate_verification_token(email)
        usuario.email_verification_token = token
        db.session.commit()
        
        lanzar_hilo_correo(email, usuario.nombre_usuario, token)

        return jsonify({
            'success': True,
            'message': 'Correo reenviado correctamente'
        })
            
    except Exception as e:
        print(f"Error reenviando verificación: {e}")
        return jsonify({'error': 'Error interno'}), 500