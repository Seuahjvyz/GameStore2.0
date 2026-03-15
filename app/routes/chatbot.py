from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from datetime import datetime, timedelta
from app import db
from app.models.models import Producto, Categoria
from app.models.pedido import Pedido
from app.models.usuario import Usuario
from app.models.contacto import Contacto
import uuid
import logging

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MODELOS DE GROQ
MODELOS_GROQ = {
    "rapido": "llama-3.1-8b-instant",      # Para saludos y consultas simples
    "potente": "llama-3.3-70b-versatile"    # Solo para consultas complejas
}

# URL base del sitio - SIN BARRA AL FINAL
SITE_URL = "https://gamestore2-0-zytn.onrender.com"

# Historial por sesión
conversaciones = {}

# Control de límite de tokens
ultimo_reset = datetime.now()
tokens_usados_hoy = 0
LIMITE_DIARIO = 90000  # Dejamos margen de 10000

def formatear_enlace_html(ruta, texto=None):
    """
    Genera un enlace en formato HTML en lugar de Markdown
    para evitar problemas con paréntesis y espacios
    """
    if not ruta:
        ruta = '/'
    
    # Limpiar la ruta
    ruta = ruta.strip().replace(' ', '')
    
    # Asegurar que empiece con /
    if not ruta.startswith('/') and not ruta.startswith('http'):
        ruta = '/' + ruta
    
    # Si no es URL completa, agregar el dominio
    if not ruta.startswith('http'):
        url_completa = f"{SITE_URL}{ruta}"
    else:
        url_completa = ruta
    
    # Texto por defecto si no se proporciona
    if not texto:
        texto = ruta
    
    # Devolver enlace HTML
    return f'<a href="{url_completa}" target="_blank" style="color: #8b5cf6; text-decoration: underline;">{texto}</a>'

def formatear_texto_con_enlaces(texto):
    """
    Reemplaza cualquier URL en el texto con enlaces HTML clickeables
    """
    import re
    # Patrón para encontrar URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    def reemplazar_url(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" style="color: #8b5cf6;">{url}</a>'
    
    return re.sub(url_pattern, reemplazar_url, texto)

def obtener_session_id():
    """Obtiene o crea un ID único para el usuario actual"""
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    return f"anon_{session['chat_session_id']}"

def es_administrador():
    """Verifica si el usuario actual es administrador"""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return usuario and usuario.rol_id == 1
    return False

def verificar_limite_tokens():
    """Verifica si hemos alcanzado el límite diario de tokens"""
    global ultimo_reset, tokens_usados_hoy
    
    ahora = datetime.now()
    if ahora.date() > ultimo_reset.date():
        tokens_usados_hoy = 0
        ultimo_reset = ahora
    
    return tokens_usados_hoy < LIMITE_DIARIO

def obtener_productos_reales():
    """Obtiene productos de la BD con su información completa"""
    try:
        productos = Producto.query.filter(
            Producto.activo == True
        ).all()
        
        if not productos:
            return []
        
        lista_productos = []
        for p in productos:
            lista_productos.append({
                'nombre': p.nombre,
                'precio': float(p.precio),
                'descripcion': p.descripcion or "Sin descripción disponible",
                'categoria': p.categoria.nombre if p.categoria else 'General',
                'stock': p.stock,
                'id': p.id_producto,
                'disponible': p.stock > 0,
                'imagen': p.imagen
            })
        
        return lista_productos
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return []

def obtener_contexto_completo(mensaje_usuario, session_id):
    """Genera el contexto completo de la tienda para Groq"""
    
    # Verificar si el usuario saludó
    saludos = ['hola', 'holis', 'holi', 'holus', 'buenos dias', 'buenas tardes', 'buenas noches', 
               'que tal', 'qué tal', 'que onda', 'qué onda', 'k onda', 'k pedo', 'k honda', 'hey',
               'hola!', 'hola?', 'buenas', 'saludos']
    usuario_saludo = any(saludo in mensaje_usuario.lower() for saludo in saludos)
    
    productos = obtener_productos_reales()
    
    # Información del usuario actual
    info_usuario = ""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        if usuario:
            info_usuario = f"El usuario actual es {usuario.nombre_usuario}"
            if usuario.rol_id == 1:
                info_usuario += " y es ADMINISTRADOR."
    
    # Construir contexto
    contexto = f"""Eres un asistente virtual amigable de GAME STORE, una tienda en línea de videojuegos.

INFORMACIÓN GENERAL:
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- Formulario: {formatear_enlace_html('/contacto', 'Contacto')}
- Horario: L-S 10:00-20:00, D 12:00-18:00
- Ubicación: Av. Miguel Ángel de Quevedo 1150, Coyoacán, CDMX

PRODUCTOS:
"""
    if productos:
        for p in productos:
            if p['disponible']:
                contexto += f"- {p['nombre']}: ${p['precio']:,.0f}\n"
    else:
        contexto += "No hay productos disponibles.\n"

    contexto += f"""
SECCIONES:
- Inicio: {formatear_enlace_html('/')}
- Juegos: {formatear_enlace_html('/juegos')}
- Consolas: {formatear_enlace_html('/consolas')}
- Controles: {formatear_enlace_html('/controles')}
- Accesorios: {formatear_enlace_html('/accesorios')}
- Carrito: {formatear_enlace_html('/carrito')}
- Favoritos: {formatear_enlace_html('/favoritos')}
- Pedidos: {formatear_enlace_html('/pedidos')}
- Perfil: {formatear_enlace_html('/perfil-usuario')}
- Contacto: {formatear_enlace_html('/contacto')}
- Sobre nosotros: {formatear_enlace_html('/sobre-nosotros')}
- Registrarse: {formatear_enlace_html('/registro')}
- Iniciar sesión: {formatear_enlace_html('/login')}

POLÍTICAS:
1. 💰 PAGOS: Solo PayPal
2. ❌ CAMBIOS Y DEVOLUCIONES: No se aceptan por NINGUNA razón
3. ⏰ CANCELACIONES: Solo en primeras 24h en {formatear_enlace_html('/pedidos')}
4. 📦 PEDIDOS: Se ven en {formatear_enlace_html('/pedidos')}
5. 📧 CORREOS: No enviamos confirmaciones
6. ❤️ FAVORITOS: En {formatear_enlace_html('/favoritos')} (requiere login)
7. 👤 PERFIL: Muestra nombre, ID, email, rol
8. 🔐 RECUPERACIÓN: No hay, contactar a soporte
9. 📞 CONTACTO: Admin responde en 24h por correo
10. 📦 PRODUCTO EN MAL ESTADO: Contactar con fotos/video

INSTRUCCIONES DETALLADAS PARA ACCIONES:

**CÓMO AGREGAR A FAVORITOS:**
- Busca el producto en {formatear_enlace_html('/juegos')}, {formatear_enlace_html('/consolas')}, etc.
- En la **parte superior derecha** de cada producto hay un ícono de corazón 🤍 (gris)
- Haz clic en el corazón
- Se pondrá **ROJO con fondo BLANCO** ❤️
- Aparecerá un mensaje verde "Producto agregado a favoritos"
- Para ver todos: {formatear_enlace_html('/favoritos')}
- Para quitarlo: haz clic nuevamente en el corazón rojo

**CÓMO AGREGAR AL CARRITO:**
- Ve a la categoría del producto
- Busca el producto
- Haz clic en el botón **"Agregar al Carrito"** (fondo degradado azul/morado, ícono 🛒)
- Aparecerá mensaje de confirmación
- Ver carrito: {formatear_enlace_html('/carrito')}
- En el carrito puedes: cambiar cantidades (+/-), eliminar (🗑️)

**CÓMO VER CARRITO:**
- En la barra superior, ícono del carrito 🛒
- Al lado, un círculo rojo con el número de productos
- Haz clic o ve a {formatear_enlace_html('/carrito')}

**CÓMO PAGAR CON PAYPAL:**
- Ten productos en el carrito
- Ve a {formatear_enlace_html('/carrito')}
- Botón **"Pagar con PayPal"** (fondo degradado azul/morado)
- Serás redirigido a PayPal
- Confirma el pago
- Verás mensaje de éxito
- Ve el pedido en {formatear_enlace_html('/pedidos')}

**CÓMO VER PEDIDOS:**
- Inicia sesión
- En barra lateral, "Pedidos"
- O ve a {formatear_enlace_html('/pedidos')}
- Verás lista con: número, fecha, total, estado
- Estados: Procesando (naranja), Enviado (azul), Entregado (verde), Cancelado (rojo)

**CÓMO CANCELAR UN PEDIDO:**
- Ve a {formatear_enlace_html('/pedidos')}
- Busca el pedido (menos de 24h)
- Botón rojo **"Cancelar pedido"**
- Confirma
- El estado cambiará a "Cancelado"
- Después de 24h, no se puede

**CÓMO VER PERFIL:**
- En barra superior, ícono de usuario 👤
- En menú, "Perfil"
- O ve a {formatear_enlace_html('/perfil-usuario')}
- Verás: nombre, número de cliente (#ID), email, rol

**CÓMO REGISTRARSE:**
- En barra superior, ícono 👤 → "Registrarse"
- O ve a {formatear_enlace_html('/registro')}
- Completa: usuario (mín 6), email, contraseña (mín 8)
- Botón morado **"Crear Cuenta"**
- Usa datos reales

**CÓMO INICIAR SESIÓN:**
- En barra superior, ícono 👤 → "Iniciar Sesión"
- O ve a {formatear_enlace_html('/login')}
- Ingresa usuario O email + contraseña
- Botón morado **"Iniciar Sesión"**

**CÓMO CERRAR SESIÓN:**
- En barra superior, ícono 👤 → "Cerrar Sesión"

**CÓMO CONTACTAR:**
- Formulario: {formatear_enlace_html('/contacto')}
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- Admin responde en 24h

**CÓMO VER UBICACIÓN:**
- En {formatear_enlace_html('/sobre-nosotros')}
- Al final hay un mapa
- Dirección: Av. Miguel Ángel de Quevedo 1150, Coyoacán

**CÓMO VER REDES SOCIALES:**
- En el footer de cada página
- Instagram (fondo rosa), Facebook (azul), X (negro), WhatsApp (verde)

**REGLAS IMPORTANTES PARA ENLACES:**
- Siempre usa enlaces HTML: <a href="URL">texto</a>
- NUNCA uses formato Markdown [texto](url)
- Asegúrate de que los enlaces tengan espacios antes y después

{info_usuario}
"""
    return contexto

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chatbot"""
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip()
        
        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400
        
        session_id = obtener_session_id()
        logger.info(f"👤 Sesión: {session_id} - Mensaje: {mensaje_usuario[:50]}...")
        
        # Inicializar historial
        if session_id not in conversaciones:
            conversaciones[session_id] = []
        
        # Verificar límite de tokens
        if not verificar_limite_tokens():
            return jsonify({
                'respuesta': "Lo siento, hemos alcanzado el límite de consultas por hoy. Por favor intenta mañana. 🌙",
                'success': True,
                'fuente': 'limite'
            })
        
        # Obtener API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.error("❌ GROQ_API_KEY no configurada")
            return jsonify({
                'respuesta': "Lo siento, el servicio no está disponible en este momento. Por favor intenta más tarde.",
                'success': True,
                'fuente': 'error'
            })
        
        # Crear cliente de Groq
        cliente = Groq(api_key=api_key)
        
        # Elegir modelo según la consulta
        if len(mensaje_usuario.split()) < 5 and any(saludo in mensaje_usuario.lower() for saludo in ['hola', 'holis', 'buenas']):
            modelo = MODELOS_GROQ["rapido"]  # Modelo rápido para saludos
        else:
            modelo = MODELOS_GROQ["potente"]  # Modelo potente para consultas complejas
        
        # Obtener contexto
        contexto_sistema = obtener_contexto_completo(mensaje_usuario, session_id)
        
        # Preparar mensajes
        messages = [{"role": "system", "content": contexto_sistema}]
        
        # Agregar historial (solo últimos 4 para ahorrar tokens)
        for msg in conversaciones[session_id][-4:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": mensaje_usuario})
        
        logger.info(f"🤖 Usando modelo: {modelo}")
        
        # Llamar a Groq
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=messages,
            temperature=0.7,
            max_tokens=800,  # Reducido para ahorrar tokens
            top_p=0.9
        )
        
        # Actualizar contador de tokens
        global tokens_usados_hoy
        if hasattr(respuesta, 'usage'):
            tokens_usados_hoy += respuesta.usage.total_tokens
            logger.info(f"📊 Tokens hoy: {tokens_usados_hoy}/{LIMITE_DIARIO}")
        
        respuesta_texto = respuesta.choices[0].message.content
        
        # Formatear enlaces en la respuesta
        respuesta_texto = formatear_texto_con_enlaces(respuesta_texto)
        
        # Guardar en historial
        conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[session_id].append({"role": "assistant", "content": respuesta_texto})
        
        # Limitar historial
        if len(conversaciones[session_id]) > 10:
            conversaciones[session_id] = conversaciones[session_id][-10:]
        
        return jsonify({
            'respuesta': respuesta_texto,
            'modelo': modelo,
            'fuente': 'groq',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Manejo específico de límite de tasa
        if "rate_limit" in str(e).lower():
            return jsonify({
                'respuesta': "Hemos llegado al límite de consultas por hoy. Por favor intenta mañana. 🌙",
                'success': True,
                'fuente': 'limite'
            })
        
        return jsonify({
            'respuesta': "Lo siento, tuve un problema técnico. ¿Puedes repetir tu pregunta? 😊",
            'success': True,
            'fuente': 'error'
        })

@chatbot_bp.route('/api/chat/historial', methods=['GET'])
def obtener_historial():
    """Obtiene el historial del usuario actual"""
    try:
        session_id = obtener_session_id()
        historial = conversaciones.get(session_id, [])
        
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
            'historial': mensajes_mostrar,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/chat/limpiar', methods=['POST'])
def limpiar_historial():
    """Limpia el historial del usuario actual"""
    try:
        session_id = obtener_session_id()
        if session_id in conversaciones:
            conversaciones[session_id] = []
        
        return jsonify({
            'success': True,
            'message': 'Historial limpiado',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/chat/sesion-info', methods=['GET'])
def sesion_info():
    """Información de la sesión actual"""
    session_id = obtener_session_id()
    return jsonify({
        'session_id': session_id,
        'user_id': session.get('user_id'),
        'is_authenticated': 'user_id' in session,
        'is_admin': es_administrador(),
        'historial_size': len(conversaciones.get(session_id, []))
    })

@chatbot_bp.route('/api/user-info', methods=['GET'])
def user_info():
    """Obtiene información del usuario"""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'username': usuario.nombre_usuario if usuario else session.get('username', 'Usuario'),
                'id': session.get('user_id'),
                'email': usuario.correo if usuario else '',
                'is_admin': usuario and usuario.rol_id == 1
            },
            'session_id': obtener_session_id()
        })
    return jsonify({
        'logged_in': False,
        'session_id': obtener_session_id()
    })

@chatbot_bp.route('/api/chat/test', methods=['GET'])
def test_chatbot():
    """Endpoint de prueba"""
    try:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({'error': 'GROQ_API_KEY no configurada'}), 500
        
        cliente = Groq(api_key=api_key)
        
        respuesta = cliente.chat.completions.create(
            model=MODELOS_GROQ["rapido"],
            messages=[{"role": "user", "content": "Hola, prueba"}],
            max_tokens=20
        )
        
        return jsonify({
            'mensaje': '✅ API de chatbot funcionando correctamente',
            'respuesta': respuesta.choices[0].message.content,
            'session_id': obtener_session_id(),
            'is_admin': es_administrador(),
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@chatbot_bp.route('/api/chat/modelos', methods=['GET'])
def listar_modelos():
    """Lista los modelos disponibles"""
    modelos = [
        {
            "id": MODELOS_GROQ["potente"],
            "nombre": "Llama 3.3 70B",
            "descripcion": "Modelo potente para consultas complejas",
            "contexto": 8192
        },
        {
            "id": MODELOS_GROQ["rapido"],
            "nombre": "Llama 3.1 8B",
            "descripcion": "Modelo rápido para saludos",
            "contexto": 8192
        }
    ]
    return jsonify({'success': True, 'modelos': modelos})

@chatbot_bp.route('/api/buscar-productos', methods=['GET'])
def buscar_productos_api():
    """Búsqueda rápida de productos"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'resultados': []})
        
        productos = Producto.query.filter(
            Producto.activo == True,
            Producto.stock > 0,
            (Producto.nombre.ilike(f'%{query}%') |
             Producto.descripcion.ilike(f'%{query}%'))
        ).limit(5).all()
        
        resultados = [{
            'id': p.id_producto,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'imagen': p.imagen,
            'categoria': p.categoria.nombre if p.categoria else 'General'
        } for p in productos]
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500