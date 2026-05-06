from flask import Blueprint, request, jsonify, current_app
import requests
import logging

captcha_bp = Blueprint('captcha', __name__, url_prefix='/api/captcha')
logger = logging.getLogger(__name__)

@captcha_bp.route('/verify', methods=['POST'])
def verify_captcha():
    """Endpoint para verificar reCAPTCHA v2"""
    try:
        data = request.get_json()
        captcha_response = data.get('captcha_response')
        
        if not captcha_response:
            return jsonify({
                'success': False,
                'error': 'Por favor completa el captcha "No soy un robot"'
            }), 400
        
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
        
        if not secret_key:
            logger.error("RECAPTCHA_SECRET_KEY no configurada")
            return jsonify({
                'success': False,
                'error': 'Error de configuración del servidor'
            }), 500
        
        verify_data = {
            'secret': secret_key,
            'response': captcha_response
        }
        
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=verify_data,
            timeout=5
        )
        
        result = response.json()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Captcha verificado correctamente'
            })
        else:
            error_codes = result.get('error-codes', [])
            error_message = _get_captcha_error_message(error_codes)
            
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con el servicio de verificación'
        }), 500
    except Exception as e:
        logger.error(f"Error in captcha verification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

def _get_captcha_error_message(error_codes):
    """Convierte códigos de error de Google en mensajes amigables"""
    if not error_codes:
        return "Verificación fallida"
    
    if 'missing-input-response' in error_codes:
        return "Por favor completa el captcha"
    elif 'invalid-input-response' in error_codes:
        return "El captcha es inválido, intenta nuevamente"
    elif 'timeout-or-duplicate' in error_codes:
        return "El captcha ha expirado, refresca la página"
    else:
        return "Error de verificación, intenta nuevamente"