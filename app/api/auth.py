from flask import Blueprint, jsonify
from flask_login import current_user

bp = Blueprint('auth', __name__)

@bp.route('/api/usuario/actual', methods=['GET'])
def usuario_actual():
    try:
        if current_user.is_authenticated:
            return jsonify({
                'id_usuario': current_user.id_usuario,
                'nombre': current_user.nombre,
                'nombre_usuario': current_user.nombre_usuario,
                'correo': current_user.correo
            })
        else:
            return jsonify(None)
    except Exception as e:
        print(f"Error en usuario_actual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500