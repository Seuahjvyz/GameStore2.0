from flask import Blueprint, redirect, url_for, flash, request, jsonify
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app.models.usuario import Usuario
from app import db, mail
import os

verification_bp = Blueprint('verification', __name__)

#------------------------------------------ token diferente por cada usuario -------------------------
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=expiration)
        return email
    except:
        return None

#------------------------------------------ Cuerpo del correo -------------------------------------

def send_verification_email(user_email, username, token):
    
    base_url = "http://localhost:5000"
    
    if os.getenv('RENDER_EXTERNAL_URL'):
        base_url = os.getenv('RENDER_EXTERNAL_URL')
    elif os.getenv('RAILWAY_PUBLIC_DOMAIN'):
        base_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}"
    elif os.getenv('PRODUCTION_URL'):
        base_url = os.getenv('PRODUCTION_URL')
    
    verification_url = f"{base_url}/verify-email/{token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .button {{
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <h2>🎮 GameStore </h2>
        <p>Hola <strong>{username}</strong>,</p>
        <p>Gracias por registrarte. Verifica tu cuenta:</p>
        <a href="{verification_url}" class="button">Verificar mi cuenta</a>
        <p>O copia: {verification_url}</p>
        <p> Este enlace expira en 1 hora.</p>
    </body>
    </html>
    """
    
    msg = Message(
        subject="Verifica tu cuenta - GameStore ",
        recipients=[user_email],
        html=html_content
    )
    
    try:
        mail.send(msg)
        print(f" Email enviado a {user_email}")
        return True
    except Exception as e:
        print(f" Error enviando email: {e}")
        return False

#-------------------------------Verificación ----------------------------------
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
        flash('Tu cuenta ya estaba verificada. ¡Puedes iniciar sesión!', 'info')
    else:
        usuario.verificacion = True
        usuario.email_verification_token = None
        db.session.commit()
        flash('¡Cuenta verificada exitosamente! Ahora puedes iniciar sesión.', 'success')
    
    return redirect(url_for('web.login'))

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
            return jsonify({'error': 'Esta cuenta ya está verificada'}), 400
        
        token = generate_verification_token(email)
        usuario.email_verification_token = token
        db.session.commit()
        
        if send_verification_email(email, usuario.nombre_usuario, token):
            return jsonify({
                'success': True,
                'message': 'Correo de verificación reenviado. Revisa tu bandeja de entrada.'
            })
        else:
            return jsonify({'error': 'Error al enviar el correo. Intenta más tarde.'}), 500
            
    except Exception as e:
        print(f"Error reenviando verificación: {e}")
        return jsonify({'error': 'Error interno'}), 500