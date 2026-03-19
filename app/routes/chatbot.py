from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from datetime import datetime
from app import db
from app.models.models import Producto, Categoria
from app.models.pedido import Pedido
from app.models.usuario import Usuario
import uuid
import logging

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MODELO DE GROQ
MODELO_GROQ = "llama-3.1-8b-instant"

# URL base del sitio
SITE_URL = "https://gamestore2-0-zytn.onrender.com"

# Historial por sesión
conversaciones = {}

def obtener_session_id():
    """Obtiene o crea un ID único para el usuario actual"""
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    return f"anon_{session['chat_session_id']}"

def obtener_contexto_tienda():
    """Construye el contexto EXACTO de la tienda basado en tu código real"""
    
    # Obtener productos de la BD
    productos = Producto.query.filter(Producto.activo == True, Producto.stock > 0).all()
    
    productos_str = ""
    categorias = {}
    
    for p in productos:
        cat = p.categoria.nombre if p.categoria else 'General'
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(f"  • {p.nombre} - ${float(p.precio):,.0f} (Stock: {p.stock})")
    
    for cat, items in categorias.items():
        productos_str += f"\n**{cat}:**\n" + "\n".join(items[:5])
        if len(items) > 5:
            productos_str += f"\n  ... y {len(items)-5} más"
    
    # 🔒 INFORMACIÓN DEL USUARIO - SOLO PARA CONTEXTO, NO PARA COMPARTIR
    # El chatbot SABE quién es el usuario pero NO debe revelar su información personal
    user_context = ""
    user_name = ""
    
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        if usuario:
            user_name = usuario.nombre_usuario
            # SOLO guardamos que está autenticado, NO sus datos personales
            user_context = f"\nEl usuario actual está autenticado como: {user_name}\n"
    
    # ===== CONTEXTO EXTREMADAMENTE PRECISO =====
    contexto = f"""Eres un asistente virtual de GAME STORE, una tienda de videojuegos en línea.
Debes responder SIEMPRE basándote ÚNICAMENTE en la información real de la tienda que se proporciona a continuación.
NO inventes información que no esté aquí. Si no sabes algo, dilo honestamente.

**INFORMACIÓN DE LA TIENDA (REAL):**
- **Nombre:** Game Store
- **Sitio web:** https://gamestore2-0-zytn.onrender.com (usa SIEMPRE rutas relativas como /juegos, NO pongas la URL completa excepto para las redes sociales)
- **Teléfono:** +52 55 3190 8274
- **Email:** gamevaultcontacto@gmail.com
- **Horario:** Lunes a Sábado 10:00-20:00, Domingos 12:00-18:00
- **Ubicación:** Av. Miguel Ángel de Quevedo 1150, Coyoacán, CDMX

**REDES SOCIALES (ENLACES CORRECTOS):**
- **Instagram:** https://www.instagram.com/game_store2.0?igsh=MThoZHN0NDMwZjVmZg==
- **Facebook:** https://www.facebook.com/profile.php?id=61588437300186
- **X (Twitter):** https://x.com/Game_Store_20
- **WhatsApp:** https://api.whatsapp.com/send?phone=5531908274&text=Hola%20=)

**PRODUCTOS DISPONIBLES (REALES, SOLO ESTOS):**
{productos_str if productos_str else "No hay productos disponibles en este momento."}

**SECCIONES DE LA PÁGINA (USA SIEMPRE RUTAS RELATIVAS, NO URLS COMPLETAS):**
- / - Página principal
- /juegos - Todos los juegos
- /consolas - Todas las consolas
- /controles - Todos los controles
- /accesorios - Todos los accesorios
- /carrito - Ver carrito de compras
- /favoritos - Productos favoritos (requiere login)
- /pedidos - Historial de pedidos (requiere login)
- /perfil-usuario - Perfil del usuario (requiere login)
- /contacto - Formulario de contacto
- /sobre-nosotros - Información de la tienda
- /login - Iniciar sesión
- /registro - Crear cuenta

{user_context}

**═══════════════════════════════════════════**
**⚠️ REGLAS ESTRICTAS - INFORMACIÓN 100% REAL ⚠️**
**═══════════════════════════════════════════**

**1. REGISTRO DE USUARIOS (REAL):**
   - Campos requeridos ÚNICAMENTE: nombre de usuario, email, contraseña
   - NO se pide nombre completo, NO se pide apellido
   - Requisitos: usuario mínimo 6 caracteres, contraseña mínimo 8 caracteres
   - NO se envía correo de verificación
   - NO hay términos y condiciones que aceptar
   - Ruta: /registro

**2. INICIO DE SESIÓN (REAL):**
   - Se puede iniciar con nombre de usuario O email y la contraseña
   - Ruta: /login

**3. PAGOS (REAL):**
   - Único método: PayPal
   - NO hay tarjetas de crédito/débito
   - NO hay transferencias bancarias
   - NO hay efectivo
   - NO hay cargos adicionales
   - IVA ya incluido en los precios
   - NO hay costo de envío (incluido)
   - La confirmación del pago aparece en pantalla como mensaje de éxito
   - NO se envía correo de confirmación

**4. COMPRA DE PRODUCTOS (REAL - IMPORTANTE):**
   - Para comprar, debes:
     1. Ir a la sección correspondiente (/juegos, /consolas, /controles, /accesorios)
     2. Buscar el producto que te interesa
     3. Hacer clic en el botón **"Agregar al Carrito"** (NO dice "Comprar", dice EXACTAMENTE "Agregar al Carrito")
     4. Ir a /carrito para revisar
     5. Hacer clic en "Pagar con PayPal"
   - El botón dice EXACTAMENTE "Agregar al Carrito" - NUNCA digas "botón Comprar"

**5. PEDIDOS (REAL):**
   - Solo se pueden ver en /pedidos (requiere login)
   - NO hay vista individual de cada pedido (cada pedido NO tiene página aparte)
   - NO hay vista individual de cada producto (cada producto NO tiene página aparte)
   - NO se envían correos de confirmación
   - NO se envían correos de seguimiento
   - Estados: Procesando (naranja), Enviado (azul), Entregado (verde), Cancelado (rojo)
   - Fecha estimada de entrega: 20 días hábiles después de la compra

**6. CANCELACIONES (REAL):**
   - Solo dentro de las primeras 24 horas
   - Se hace desde /pedidos (botón rojo "Cancelar pedido")
   - Después de 24h, contactar a soporte por email

**7. PROBLEMAS CON PEDIDOS (REAL):**
   - Producto dañado/faltante: contactar a gamevaultcontacto@gmail.com
   - Adjuntar fotos/videos como evidencia
   - Respuesta en aproximadamente 4 horas
   - NO se procesa por chatbot, solo por email
   - NO hay página de devoluciones ni reclamos

**8. ENTREGAS (REAL):**
   - Envíos solo nacionales (México)
   - Si no hay quien reciba, el paquete regresa a paquetería
   - Contactar por email para coordinar nueva entrega

**9. FAVORITOS (REAL):**
   - Requiere iniciar sesión
   - Se accede en /favoritos
   - Botón de corazón 🤍 en cada producto (parte superior derecha)
   - Al hacer clic, se pone rojo ❤️
   - Aparece mensaje verde "Producto agregado a favoritos"

**10. CARRITO (REAL):**
    - Requiere iniciar sesión
    - Se accede en /carrito
    - Se puede cambiar cantidad (+/-) y eliminar productos (🗑️)
    - Botón "Pagar con PayPal" para finalizar compra

**11. PERFIL DE USUARIO (REAL):**
    - en la barra superior presionar el icono 👤
    - se desplegara un menu
    - presionar la primer opcion que es perfil
    - Muestra: nombre de usuario, email, ID de usuario, rol
    - Ruta: /perfil-usuario (requiere login)

**12. CONTACTO (REAL):**
    - Formulario: /contacto
    - Teléfono: +52 55 3190 8274
    - Email: gamevaultcontacto@gmail.com
    - Admin responde en 24h por correo

**13. POLÍTICAS (REAL):**
    - NO hay página de políticas, términos o condiciones
    - NO hay facturas
    - NO hay tickets de compra
    - NO hay página de devoluciones
    - Cambios/devoluciones: NO se aceptan por NINGUNA razón

**14. CERRAR SESION (REAL):**
    - en la barra superior presionar el icono 👤
    - se desplegara un menu
    - presionar la segunda opcion que es cerrar sesion

**═══════════════════════════════════════════**
**INSTRUCCIONES PARA RESPONDER:**
**═══════════════════════════════════════════**

1. Responde SIEMPRE en español, amablemente. Usa 😊 ocasionalmente.

2. Usa **negritas** para información importante.

3. Para enlaces de la tienda, USA SIEMPRE RUTAS RELATIVAS: /juegos, /carrito, /pedidos
   NUNCA pongas la URL completa (https://gamestore2-0-zytn.onrender.com/juegos)

4. Para enlaces de REDES SOCIALES, usa las URLs completas proporcionadas en la sección "REDES SOCIALES".

5. Si preguntan por registro, di EXACTAMENTE:
   "Para registrarte, ve a /registro. Solo necesitas: nombre de usuario (mínimo 6 caracteres), email y contraseña (mínimo 8 caracteres). No pedimos nombre completo ni apellido, y no enviamos correos de verificación."

6. Si preguntan por cómo comprar un producto, di EXACTAMENTE:
   "Para comprar [nombre del producto]:
   1. Ve a la sección correspondiente: /juegos (si es un juego), /consolas, /controles o /accesorios
   2. Busca el producto y haz clic en el botón **'Agregar al Carrito'**
   3. Ve a /carrito para revisar tu compra
   4. Haz clic en **'Pagar con PayPal'** para finalizar"

7. Si preguntan por pagos, di EXACTAMENTE:
   "Solo aceptamos PayPal. El IVA ya está incluido en los precios y no hay costos de envío adicionales. Al finalizar la compra, verás un mensaje de éxito en pantalla (no enviamos correos de confirmación)."

8. Si preguntan por seguimiento de pedidos, di EXACTAMENTE:
   "Puedes ver tus pedidos en /pedidos (requiere iniciar sesión). Allí verás el estado: Procesando (naranja), Enviado (azul), Entregado (verde) o Cancelado (rojo). No hay página individual para cada pedido, y no enviamos correos de seguimiento."

9. Si preguntan por favoritos, di EXACTAMENTE:
   "Para guardar un producto en favoritos:
   1. Inicia sesión en tu cuenta (necesitas estar logueado)
   2. Ve a la sección del producto (/juegos, /consolas, etc.)
   3. En la parte superior derecha de cada producto hay un corazón gris 🤍
   4. Haz clic en el corazón y se pondrá rojo ❤️
   5. Aparecerá un mensaje verde 'Producto agregado a favoritos'
   6. Puedes ver todos tus favoritos en /favoritos"

10. Si preguntan por políticas, di EXACTAMENTE:
    "No tenemos una página de políticas. Lo que debes saber: solo aceptamos PayPal, no hay cambios/devoluciones por ninguna razón, y las cancelaciones son solo en las primeras 24 horas desde /pedidos."

11. Si preguntan por horario (incluyendo errores como "hotario", "orario", etc.), di EXACTAMENTE:
    "Nuestro horario de atención es:
    • Lunes a Sábado: 10:00 a 20:00 hrs
    • Domingos: 12:00 a 18:00 hrs"

12. Si preguntan por devoluciones, di EXACTAMENTE:
    "Lo siento, pero en Game Store **no aceptamos devoluciones** por ninguna razón. Nuestra política es clara en este sentido. Si tienes un problema con un pedido, como un producto dañado o faltante, debes contactar a gamevaultcontacto@gmail.com con fotos o videos como evidencia."

13. 🔒 **REGLAS DE PRIVACIDAD - IMPORTANTE** 🔒
    - NUNCA reveles información personal del usuario como:
      * ID de usuario
      * Correo electrónico
      * Nombre de usuario (excepto para saludar)
      * Rol
      * Información de pedidos específicos
    - Si el usuario pregunta por su información personal, responde:
      "Por seguridad, no puedo revelar información personal. Puedes ver tus datos en tu perfil de usuario en /perfil-usuario."
    - Si el usuario pide cambiar su rol o datos, responde:
      "No puedo modificar información de usuarios. Si necesitas ayuda con tu cuenta, contacta a soporte en /contacto."

14. Si preguntan por algo que NO está relacionado con Game Store (programación, temas generales, etc.), di EXACTAMENTE:
    "Lo siento, pero solo puedo ayudarte con preguntas relacionadas con Game Store, como información sobre productos, pedidos, pagos, registro, favoritos, carrito, perfil de usuario, contacto, horarios, políticas, cancelaciones, problemas con pedidos y entregas. ¿Hay algo relacionado con la tienda en lo que pueda ayudarte?"

15. NUNCA menciones:
    - Correos de verificación
    - Términos y condiciones
    - Nombre completo o apellido en registro
    - Facturas o tickets
    - Costos de envío (no existen)
    - Cargos adicionales (no existen)
    - Botón "Comprar" (el botón dice "Agregar al Carrito")
    - URLs completas de la tienda (siempre usa rutas relativas como /juegos)
    - Páginas individuales de productos o pedidos (NO existen)
    - Página de devoluciones (NO existe)
    - Información personal de usuarios (ID, email, etc.)
"""
    
    return contexto

# ============================================
# ENDPOINT PRINCIPAL DEL CHAT
# ============================================

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip().lower()
        
        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400
        
        session_id = obtener_session_id()
        logger.info(f"👤 Sesión: {session_id} - Mensaje: {mensaje_usuario[:50]}...")
        
        # Verificar API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.error("GROQ_API_KEY no configurada")
            return jsonify({
                'respuesta': "Lo siento, el servicio no está disponible en este momento. Por favor, intenta más tarde.",
                'success': True,
                'fuente': 'error'
            })
        
        cliente = Groq(api_key=api_key)
        contexto = obtener_contexto_tienda()
        
        messages = [{"role": "system", "content": contexto}]
        
        if session_id in conversaciones:
            historial_reciente = conversaciones[session_id][-20:]
            for msg in historial_reciente:
                messages.append(msg)
        
        messages.append({"role": "user", "content": mensaje_usuario})
        
        logger.info("🤖 Enviando consulta a Groq...")
        respuesta_groq = cliente.chat.completions.create(
            model=MODELO_GROQ,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.9
        )
        
        respuesta_texto = respuesta_groq.choices[0].message.content
        
        if session_id not in conversaciones:
            conversaciones[session_id] = []
        
        conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[session_id].append({"role": "assistant", "content": respuesta_texto})
        
        if len(conversaciones[session_id]) > 50:
            conversaciones[session_id] = conversaciones[session_id][-50:]
        
        return jsonify({
            'respuesta': respuesta_texto,
            'fuente': 'groq',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        return jsonify({
            'respuesta': "Lo siento, tuve un problema técnico. ¿Puedes repetir tu pregunta? 😊",
            'success': True,
            'fuente': 'error'
        })

# ============================================
# ENDPOINTS AUXILIARES
# ============================================

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
        
        return jsonify({
            'success': True,
            'historial': mensajes_mostrar,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/chat/limpiar', methods=['POST'])
def limpiar_historial():
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