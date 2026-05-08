from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from datetime import datetime
from app import db
from app.models.models import Producto
from app.models.usuario import Usuario
import uuid
import logging

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELO_GROQ = "llama-3.1-8b-instant"

conversaciones = {}

def obtener_session_id():
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    return f"anon_{session['chat_session_id']}"

def obtener_contexto_tienda():
    productos = Producto.query.filter(Producto.activo == True, Producto.stock > 0).all()
    categorias = {}
    for p in productos:
        cat = p.categoria.nombre if p.categoria else 'General'
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(f"{p.nombre} ${float(p.precio):,.0f}")

    productos_str = ""
    for cat, items in categorias.items():
        productos_str += f"{cat}: {', '.join(items[:5])}\n"

    user_context = ""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        if usuario:
            user_context = f"Usuario autenticado: {usuario.nombre_usuario}\n"

    contexto = f"""Eres el asistente virtual de GAME STORE, tienda de videojuegos en línea (México).
Responde SOLO con información real de esta tienda. Sé amable, cordial y conciso.
IMPORTANTE: NO uses markdown (**texto**). Para destacar datos importantes escríbelos en mayúsculas o entre comillas. Por ejemplo: "PAYPAL", "Agregar al Carrito", "/juegos".

SALUDO Y DESPEDIDA:
- Detecta saludos en cualquier forma (hola, hey, buenas, qué tal, buenos días, buenas tardes, buenas noches, hi, hello, saludos, ¿cómo estás?, etc.) y responde calurosamente.
- Detecta despedidas (adiós, hasta luego, bye, chao, nos vemos, gracias, de nada, etc.) y responde cordialmente (ej: "¡Hasta luego! Fue un placer ayudarte 😊", "¡De nada! Estoy aquí cuando me necesites 😊").
- Siempre sé cordial, empático y usa emojis ocasionalmente 😊🎮.

DATOS DE LA TIENDA:
- Tel: +52 55 3190 8274 | Email: gamevaultcontacto@gmail.com
- Horario: Lun-Sáb 10:00-20:00, Dom 12:00-18:00
- Dirección: Av. Miguel Ángel de Quevedo 1150, Coyoacán, CDMX
- Redes sociales (Instagram, Facebook, X, WhatsApp): en el **footer** (parte inferior) de TODAS las páginas

PRODUCTOS DISPONIBLES:
{productos_str or "Sin productos disponibles."}
{user_context}

NAVEGACIÓN:
- Barra LATERAL (izquierda): Inicio(/), Favoritos(/favoritos), Pedidos(/pedidos), Juegos(/juegos), Accesorios(/accesorios), Consolas(/consolas), Controles(/controles), ¿Quiénes somos?(/sobre-nosotros), Contacto(/contacto)
- Barra SUPERIOR: logo "Game Store"→/, carrito 🛒→/carrito, usuario 👤→menú desplegable
- Menú 👤: Mi Perfil(/perfil-usuario), Cerrar Sesión — o Iniciar Sesión/Registro si no hay sesión
- FOOTER: redes sociales, teléfono, email, enlace a Sobre Nosotros
- Icono de accesibilidad: botón con ícono ♿ (fa-universal-access) visible en pantalla

SEGURIDAD Y ACCESO:
- CAPTCHA: solo en la pantalla de inicio de sesión (/login)
- Registro con Google: disponible en /registro como opción alternativa
- Registro con Google: disponible como opción en /registro.
- Registro manual (/registro): usuario (mín 6 chars), email, contraseña segura (mín 8 chars, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial), confirmar contraseña, elegir 2 preguntas de seguridad de un listado de 5 y responderlas. SÍ se envía correo de verificación al registrarse (debe verificarse antes de iniciar sesión).
- Login (/login): usuario O email + contraseña + CAPTCHA. Límite de 5 intentos fallidos → cuenta bloqueada automáticamente 10 minutos. Después de los 10 minutos se desbloquea sola, NO hay forma de desbloquearla antes ni por email.
- Recuperar contraseña: en /login → "Olvidé mi contraseña" → seleccionar una de las preguntas de seguridad que elegiste al registrarte → responder correctamente → puedes cambiar tu contraseña.

COMPRAS Y PAGOS:
- Para comprar: iniciar sesión → sección del producto → clic en "Agregar al Carrito" (NUNCA digas "botón Comprar") → /carrito → "Pagar con PayPal".
- Único método de pago: PAYPAL. IVA y envío incluidos en el precio. Sin correo de confirmación, solo mensaje en pantalla.
- NO hay cambios ni devoluciones por ninguna razón. Si producto dañado/faltante: enviar email con fotos/videos, respuesta ~4h.
- Cancelar pedido: solo primeras 24h desde /pedidos → botón rojo "Cancelar pedido". Después, escribir al email.

PEDIDOS Y ENTREGAS:
- /pedidos: estados Procesando(🟠)→Enviado(🔵, ~7 días)→Entregado(🟢, ~20 días hábiles)→Cancelado(🔴).
- Sin correos de seguimiento. NO hay página individual por pedido ni por producto.
- Envíos solo en México. Entrega estimada: 20 días hábiles.

OTRAS FUNCIONES:
- Favoritos(/favoritos): requiere login. Corazón 🤍 en cada producto → clic → ❤️.
- Perfil(/perfil-usuario): icono 👤 → "Mi Perfil". Muestra usuario, email, ID, rol.
- Cerrar sesión: icono 👤 → "Cerrar Sesión".
- Accesibilidad: panel con botón ♿ en pantalla. Opciones: escala de grises, alto contraste, invertir colores, máscara de lectura, guía de lectura, fuente para dislexia, resaltar enlaces, lector de pantalla, espaciado vertical/horizontal, tamaño de texto.
- Navegación por teclado: Tab para moverse, Enter para seleccionar, flechas para scroll. Existe "Saltar al contenido principal".

RESTRICCIONES:
- NUNCA reveles datos personales del usuario (email, ID). Puedes saludar por su nombre si está logueado.
- NUNCA menciones: facturas, tickets, términos y condiciones, costos de envío por separado, páginas individuales de producto o pedido.
- Temas ajenos a Game Store: "Lo siento, solo puedo ayudarte con temas de Game Store. 😊"
- Respuestas cortas y directas. Incluye ruta (/ruta) cuando sea útil.
- MUY IMPORTANTE: NO uses asteriscos ni markdown en tus respuestas. Nunca escribas **texto**. Para enfatizar usa comillas o mayúsculas.
- LIMITACIONES DEL CHATBOT (sé honesto con el usuario sobre esto): El chatbot NO puede realizar acciones por el usuario. No puedes agregar productos al carrito, no puedes procesar pagos, no puedes crear pedidos, no puedes redirigir al usuario automáticamente, no puedes calcular totales, no puedes ver el carrito del usuario. Solo puedes INFORMAR y GUIAR al usuario para que él mismo realice las acciones en la página."""

    return contexto


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip()

        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400

        session_id = obtener_session_id()
        logger.info(f"👤 Sesión: {session_id} - Mensaje: {mensaje_usuario[:50]}...")

        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.error("GROQ_API_KEY no configurada")
            return jsonify({
                'respuesta': "Lo siento, el servicio no está disponible. Intenta más tarde.",
                'success': True,
                'fuente': 'error'
            })

        cliente = Groq(api_key=api_key)
        contexto = obtener_contexto_tienda()

        messages = [{"role": "system", "content": contexto}]

        # Solo los últimos 6 mensajes (3 turnos) para ahorrar tokens
        if session_id in conversaciones:
            messages.extend(conversaciones[session_id][-6:])

        messages.append({"role": "user", "content": mensaje_usuario})

        logger.info("🤖 Enviando consulta a Groq...")
        respuesta_groq = cliente.chat.completions.create(
            model=MODELO_GROQ,
            messages=messages,
            temperature=0.7,
            max_tokens=400,
            top_p=0.9
        )

        respuesta_texto = respuesta_groq.choices[0].message.content

        if session_id not in conversaciones:
            conversaciones[session_id] = []

        conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[session_id].append({"role": "assistant", "content": respuesta_texto})

        if len(conversaciones[session_id]) > 20:
            conversaciones[session_id] = conversaciones[session_id][-20:]

        return jsonify({'respuesta': respuesta_texto, 'fuente': 'groq', 'success': True})

    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        return jsonify({
            'respuesta': "Lo siento, tuve un problema técnico. ¿Puedes repetir tu pregunta? 😊",
            'success': True,
            'fuente': 'error'
        })


@chatbot_bp.route('/api/chat/cerrar', methods=['POST'])
def cerrar_chat():
    """Al cerrar el panel se borra el historial — el próximo saludo vuelve a ser el mensaje de bienvenida."""
    try:
        session_id = obtener_session_id()
        if session_id in conversaciones:
            conversaciones[session_id] = []
            logger.info(f"🧹 Chat cerrado y limpiado: {session_id}")
        return jsonify({'success': True, 'message': 'Chat reiniciado', 'cleared': True})
    except Exception as e:
        logger.error(f"❌ Error limpiando chat: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@chatbot_bp.route('/api/chat/historial', methods=['GET'])
def obtener_historial():
    try:
        session_id = obtener_session_id()
        historial = conversaciones.get(session_id, [])
        mensajes_mostrar = []
        for msg in historial[-20:]:
            mensajes_mostrar.append({
                'rol': msg['role'],
                'contenido': msg['content'],
                'hora': datetime.now().strftime('%H:%M')
            })
        return jsonify({'success': True, 'historial': mensajes_mostrar, 'session_id': session_id})
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@chatbot_bp.route('/api/chat/limpiar', methods=['POST'])
def limpiar_historial():
    try:
        session_id = obtener_session_id()
        if session_id in conversaciones:
            conversaciones[session_id] = []
        return jsonify({'success': True, 'message': 'Historial limpiado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chatbot_bp.route('/api/chat/sesion-info', methods=['GET'])
def sesion_info():
    session_id = obtener_session_id()
    usuario = None
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
    return jsonify({
        'session_id': session_id,
        'user_id': session.get('user_id'),
        'username': usuario.nombre_usuario if usuario else None,
        'is_authenticated': 'user_id' in session,
        'is_admin': usuario and usuario.rol_id == 1,
        'historial_size': len(conversaciones.get(session_id, []))
    })


@chatbot_bp.route('/api/user-info', methods=['GET'])
def user_info():
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        if usuario:
            return jsonify({
                'logged_in': True,
                'user': {
                    'username': usuario.nombre_usuario,
                    'id': usuario.id_usuario,
                    'email': usuario.correo,
                    'is_admin': usuario.rol_id == 1
                }
            })
    return jsonify({'logged_in': False})