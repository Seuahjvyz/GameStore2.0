from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Contexto del sistema para el chatbot
CONTEXTO_SISTEMA = """
Eres un asistente virtual amigable y servicial para GAME STORE, una tienda en línea especializada en videojuegos, consolas, accesorios y controles.

INFORMACIÓN DE LA TIENDA:
- Nombre: Game Store
- Productos: Videojuegos, Consolas, Accesorios, Controles
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- Horario: Lunes a Sábado 10:00 - 20:00, Domingos 12:00 - 18:00
- Ubicación: Av. Miguel Ángel de Quevedo 1150, Coyoacán, CDMX

ENLACES IMPORTANTES DE LA PÁGINA:
- Inicio: https://gamestore2-0.onrender.com/
- Juegos: https://gamestore2-0.onrender.com/juegos
- Consolas: https://gamestore2-0.onrender.com/consolas
- Accesorios: https://gamestore2-0.onrender.com/accesorios
- Controles: https://gamestore2-0.onrender.com/controles
- Carrito: https://gamestore2-0.onrender.com/carrito
- Favoritos: https://gamestore2-0.onrender.com/favoritos
- Pedidos: https://gamestore2-0.onrender.com/pedidos
- Perfil: https://gamestore2-0.onrender.com/perfil-usuario
- Contacto: https://gamestore2-0.onrender.com/contacto
- Sobre nosotros: https://gamestore2-0.onrender.com/sobre-nosotros

FUNCIONALIDADES:

1. AGREGAR AL CARRITO:
   - En cualquier página de productos, busca el botón "Agregar al carrito"
   - Puedes ver tu carrito en: https://gamestore2-0.onrender.com/carrito

2. ELIMINAR DEL CARRITO:
   - En la página del carrito, hay un botón de eliminar junto a cada producto

3. FAVORITOS:
   - Agregar: haz clic en el ícono de corazón en cualquier producto
   - Ver favoritos: https://gamestore2-0.onrender.com/favoritos
   - Eliminar: haz clic en el corazón nuevamente

4. PEDIDOS:
   - Ver pedidos: https://gamestore2-0.onrender.com/pedidos
   - Cancelar pedido: solo si está "pendiente". Si no, contactar a soporte

5. PERFIL:
   - Ver perfil: https://gamestore2-0.onrender.com/perfil-usuario (requiere login)

INSTRUCCIONES DE RESPUESTA:
- Responde cálido y amigable, usa emojis 😊
- SIEMPRE incluye enlaces directos como HTML cuando sea relevante
- Si el usuario pregunta algo que no sabes, sugiere contactar a soporte
- Detecta saludos, despedidas y responde apropiadamente
- Entiende el contexto aunque haya faltas de ortografía
- Sé conciso pero completo
- Si el usuario NO está logueado y pregunta sobre perfil/pedidos, indícale que necesita iniciar sesión
"""

# Historial de conversaciones por sesión
conversaciones = {}

# MODELOS ACTUALIZADOS DE GROQ (marzo 2026)
MODELOS_GROQ = {
    "rapido": "llama-3.1-8b-instant",      # Modelo rápido recomendado
    "potente": "llama-3.3-70b-versatile",   # Modelo potente
    "mixtral": "mixtral-8x7b-32768",        # Mixtral (mayor contexto)
    "gemma": "gemma2-9b-it"                  # Gemma 2
}

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chatbot con Groq"""
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip()
        
        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400
        
        # Obtener API key de Groq
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ ERROR: GROQ_API_KEY no está configurada")
            return jsonify({
                'error': 'API key no configurada', 
                'success': False
            }), 500
        
        # Crear cliente de Groq
        cliente = Groq(api_key=api_key)
        
        # Obtener ID de sesión
        sesion_id = session.get('session_id', request.remote_addr)
        
        # Inicializar historial
        if sesion_id not in conversaciones:
            conversaciones[sesion_id] = []
        
        # Preparar mensajes con contexto
        messages = [
            {"role": "system", "content": CONTEXTO_SISTEMA}
        ]
        
        # Agregar historial reciente (últimos 6 mensajes)
        for msg in conversaciones[sesion_id][-6:]:
            messages.append(msg)
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje_usuario})
        
        # Personalizar según sesión
        if 'user_id' in session:
            username = session.get('username', 'Usuario')
            messages.insert(1, {
                "role": "system", 
                "content": f"El usuario actual está logueado como: {username}. Salúdalo por su nombre cuando sea apropiado."
            })
        
        # Elegir modelo según longitud del mensaje (ACTUALIZADO)
        if len(mensaje_usuario.split()) < 15:
            modelo = MODELOS_GROQ["rapido"]  # llama-3.1-8b-instant
        else:
            modelo = MODELOS_GROQ["potente"]  # llama-3.3-70b-versatile
        
        print(f"🤖 Usando modelo: {modelo}")
        
        # Llamar a Groq
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.9,
            stream=False
        )
        
        # Obtener respuesta
        respuesta_texto = respuesta.choices[0].message.content
        
        # Guardar en historial
        conversaciones[sesion_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[sesion_id].append({"role": "assistant", "content": respuesta_texto})
        
        # Limitar historial
        if len(conversaciones[sesion_id]) > 20:
            conversaciones[sesion_id] = conversaciones[sesion_id][-20:]
        
        return jsonify({
            'respuesta': respuesta_texto,
            'modelo': modelo,
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error en chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Lo siento, tuve un problema. Por favor intenta de nuevo.',
            'success': False
        }), 500

@chatbot_bp.route('/api/chat/test', methods=['GET'])
def test_chatbot():
    """Endpoint para verificar que la API de Groq funciona"""
    try:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({
                'error': 'GROQ_API_KEY no configurada',
                'success': False
            }), 500
        
        cliente = Groq(api_key=api_key)
        
        respuesta = cliente.chat.completions.create(
            model=MODELOS_GROQ["rapido"],  # Usar modelo rápido para test
            messages=[
                {"role": "system", "content": "Responde solo con: OK"},
                {"role": "user", "content": "di OK"}
            ],
            max_tokens=10
        )
        
        return jsonify({
            'mensaje': '✅ API de Groq funcionando correctamente',
            'respuesta': respuesta.choices[0].message.content,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error en prueba: {str(e)}',
            'success': False
        }), 500

@chatbot_bp.route('/api/chat/modelos', methods=['GET'])
def listar_modelos():
    """Lista los modelos actualizados de Groq"""
    modelos = [
        {
            "id": MODELOS_GROQ["potente"],
            "nombre": "Llama 3.3 70B",
            "descripcion": "Modelo potente para respuestas detalladas",
            "contexto": 8192,
            "velocidad": "Media"
        },
        {
            "id": MODELOS_GROQ["rapido"],
            "nombre": "Llama 3.1 8B Instant",
            "descripcion": "Modelo rápido y ligero (recomendado)",
            "contexto": 8192,
            "velocidad": "Rápida"
        },
        {
            "id": MODELOS_GROQ["mixtral"],
            "nombre": "Mixtral 8x7B",
            "descripcion": "Buen balance velocidad/calidad, mayor contexto",
            "contexto": 32768,
            "velocidad": "Media"
        },
        {
            "id": MODELOS_GROQ["gemma"],
            "nombre": "Gemma 2 9B",
            "descripcion": "Modelo de Google eficiente",
            "contexto": 8192,
            "velocidad": "Rápida"
        }
    ]
    return jsonify({
        'success': True,
        'modelos': modelos
    })

@chatbot_bp.route('/api/chat/historial', methods=['GET'])
def obtener_historial():
    """Obtiene el historial de conversación"""
    try:
        sesion_id = session.get('session_id', request.remote_addr)
        historial = conversaciones.get(sesion_id, [])
        
        mensajes_mostrar = []
        for msg in historial:
            if msg['role'] in ['user', 'assistant']:
                mensajes_mostrar.append({
                    'rol': msg['role'],
                    'contenido': msg['content'],
                    'hora': datetime.now().strftime('%H:%M')
                })
        
        return jsonify({
            'success': True,
            'historial': mensajes_mostrar[-20:]
        })
        
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/chat/limpiar', methods=['POST'])
def limpiar_historial():
    """Limpia el historial de la sesión actual"""
    try:
        sesion_id = session.get('session_id', request.remote_addr)
        if sesion_id in conversaciones:
            conversaciones[sesion_id] = []
        
        return jsonify({
            'success': True,
            'message': 'Historial limpiado'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/user-info', methods=['GET'])
def user_info():
    """Obtiene información del usuario para personalizar"""
    if 'user_id' in session:
        from app.models.usuario import Usuario
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'username': usuario.nombre_usuario if usuario else session.get('username', 'Usuario'),
                'id': session.get('user_id'),
                'email': usuario.correo if usuario else ''
            }
        })
    return jsonify({'logged_in': False})