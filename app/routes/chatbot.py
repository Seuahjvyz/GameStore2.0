from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from datetime import datetime
from app import db
from app.models.models import Producto, Categoria
from app.models.pedido import Pedido
import uuid
import logging

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MODELOS DE GROQ
MODELOS_GROQ = {
    "rapido": "llama-3.1-8b-instant",
    "potente": "llama-3.3-70b-versatile",
    "mixtral": "mixtral-8x7b-32768",
    "gemma": "gemma2-9b-it"
}

# Historial por sesión
conversaciones = {}

def obtener_session_id():
    """Obtiene o crea un ID único para el usuario actual"""
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    return f"anon_{session['chat_session_id']}"

def obtener_productos_reales():
    """Obtiene SOLO los productos que existen en la BD"""
    try:
        productos = Producto.query.filter(
            Producto.activo == True,
            Producto.stock > 0
        ).all()
        
        if not productos:
            return "No hay productos disponibles en este momento."
        
        lista_productos = []
        for p in productos:
            # Determinar tipo de producto basado en la categoría REAL
            categoria_nombre = p.categoria.nombre.lower() if p.categoria else 'general'
            
            if 'juego' in categoria_nombre:
                tipo = 'juego'
            elif 'consola' in categoria_nombre:
                tipo = 'consola'
            elif 'control' in categoria_nombre:
                tipo = 'control'
            elif 'accesorio' in categoria_nombre:
                tipo = 'accesorio'
            else:
                tipo = 'producto'
            
            lista_productos.append({
                'nombre': p.nombre,
                'precio': float(p.precio),
                'categoria': p.categoria.nombre if p.categoria else 'General',
                'stock': p.stock,
                'tipo': tipo,
                'id': p.id_producto,
                'imagen': p.imagen
            })
        
        return lista_productos
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return []

def generar_contexto_sistema():
    """Genera contexto DINÁMICO con datos reales de la BD"""
    productos_reales = obtener_productos_reales()
    
    # Si no hay productos, contexto mínimo
    if not productos_reales or isinstance(productos_reales, str):
        return """
Eres un asistente virtual de GAME STORE.

⚠️ **INFORMACIÓN IMPORTANTE:**
Actualmente no hay productos disponibles en la tienda.

🏪 **INFORMACIÓN DE CONTACTO:**
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- 📝 **FORMULARIO DE CONTACTO:** https://gamestore2-0.onrender.com/contacto
- Horario: Lunes a Sábado 10:00-20:00, Domingos 12:00-18:00

🌐 **SECCIONES DISPONIBLES:**
- Inicio: https://gamestore2-0.onrender.com/
- Juegos: /juegos
- Consolas: /consolas
- Controles: /controles
- Accesorios: /accesorios
- Carrito: /carrito
- Perfil: /perfil-usuario
- 📝 Contacto: /contacto
- Favoritos: /favoritos
- Pedidos: /pedidos

**REGLAS IMPORTANTES:**
1. SOLO habla de productos que existen en la lista anterior.
2. Si el usuario pregunta por algo que no está en la lista, di que no está disponible.
3. NO inventes productos, precios o características.
4. El ÚNICO método de pago es PayPal.
5. NO se envía correo de confirmación, la información está en "Mis Pedidos" (/pedidos).
6. Los pedidos se pueden cancelar SOLO dentro de las primeras 24 horas.
7. **SÍ HAY FORMULARIO DE CONTACTO** en la sección /contacto.
8. NO existen páginas individuales de productos - todos los productos se muestran en grids por categoría.
9. NO hay recuperación de contraseña.
10. NO hay reviews ni calificaciones de productos.
"""
    
    # Construir lista de productos por categoría
    juegos = [p for p in productos_reales if p['tipo'] == 'juego']
    consolas = [p for p in productos_reales if p['tipo'] == 'consola']
    controles = [p for p in productos_reales if p['tipo'] == 'control']
    accesorios = [p for p in productos_reales if p['tipo'] == 'accesorio']
    
    contexto = f"""
Eres un asistente virtual de GAME STORE.

📊 **PRODUCTOS DISPONIBLES (SOLO ESTOS EXISTEN):**

"""
    if juegos:
        contexto += "🎮 **JUEGOS:**\n"
        for j in juegos:
            contexto += f"  • {j['nombre']} - ${j['precio']:,.0f} (Stock: {j['stock']})\n"
    
    if consolas:
        contexto += "\n🕹️ **CONSOLAS:**\n"
        for c in consolas:
            contexto += f"  • {c['nombre']} - ${c['precio']:,.0f} (Stock: {c['stock']})\n"
    
    if controles:
        contexto += "\n🎮 **CONTROLES:**\n"
        for ct in controles:
            contexto += f"  • {ct['nombre']} - ${ct['precio']:,.0f} (Stock: {ct['stock']})\n"
    
    if accesorios:
        contexto += "\n🎧 **ACCESORIOS:**\n"
        for a in accesorios:
            contexto += f"  • {a['nombre']} - ${a['precio']:,.0f} (Stock: {a['stock']})\n"
    
    contexto += f"""
🏪 **INFORMACIÓN DE LA TIENDA:**
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- 📝 **FORMULARIO DE CONTACTO:** https://gamestore2-0.onrender.com/contacto
- Horario: Lunes a Sábado 10:00-20:00, Domingos 12:00-18:00

🌐 **SECCIONES DISPONIBLES:**
- Inicio: https://gamestore2-0.onrender.com/
- Juegos: /juegos
- Consolas: /consolas
- Controles: /controles
- Accesorios: /accesorios
- Carrito: /carrito
- Perfil: /perfil-usuario
- 📝 Contacto: /contacto
- Favoritos: /favoritos
- Pedidos: /pedidos

**ℹ️ INFORMACIÓN DEL SISTEMA (MUY IMPORTANTE):**

💰 **MÉTODO DE PAGO:**
- El ÚNICO método de pago aceptado es PayPal.
- No hay otros métodos (tarjeta, transferencia, etc.)

📦 **PROCESO DE COMPRA:**
1. Agregas productos al carrito (desde /juegos, /consolas, /controles, /accesorios)
2. Vas a /carrito
3. Pagas con PayPal
4. La información de la compra aparece en /pedidos
5. **NO se envía correo de confirmación** - toda la info está en /pedidos

❌ **CANCELACIONES:**
- Solo se puede cancelar dentro de las primeras 24 horas después de la compra
- Después de 24 horas, no se puede cancelar
- La cancelación se hace desde /pedidos

📝 **CONTACTO Y SOPORTE:**
- **FORMULARIO DE CONTACTO:** /contacto (SÍ EXISTE)
- Teléfono: +52 55 3190 8274
- Email: gamevaultcontacto@gmail.com
- Horario de atención: Lunes a Sábado 10:00-20:00, Domingos 12:00-18:00

❤️ **FAVORITOS:**
- Los favoritos se guardan por usuario
- Se accede desde /favoritos
- Requiere iniciar sesión

⚠️ **LO QUE NO EXISTE EN EL SISTEMA (NO MENCIONAR):**
- ❌ NO hay páginas individuales de productos
- ❌ NO se envían correos de confirmación
- ❌ NO hay recuperación de contraseña
- ❌ NO hay reviews ni calificaciones
- ❌ NO hay wishlist aparte de favoritos
- ❌ NO hay envío a domicilio real
- ❌ NO hay stock en tiempo real fuera del carrito
- ❌ **NO REVELES INFORMACIÓN SOBRE EL PANEL DE ADMINISTRACIÓN**

**REGLAS ESTRICTAS:**
1. 🚫 **NO HABLES DE PRODUCTOS QUE NO ESTÉN EN LA LISTA ANTERIOR**
2. 🚫 **NO MENCIONES MÉTODOS DE PAGO QUE NO SEAN PAYPAL**
3. 🚫 **NO DIGAS QUE SE ENVÍAN CORREOS (NO ESTÁ IMPLEMENTADO)**
4. 🚫 **NO DIGAS QUE HAY PÁGINAS INDIVIDUALES DE PRODUCTOS**
5. 🚫 **NO MENCIONES RECUPERACIÓN DE CONTRASEÑA**
6. 🚫 **NO HABLES DE REVIEWS O CALIFICACIONES**
7. 🚫 **NO REVELES INFORMACIÓN SOBRE EL PANEL DE ADMINISTRACIÓN (rutas, cómo agregar usuarios, etc.)**
8. ✅ **SIEMPRE VERIFICA QUE UN PRODUCTO EXISTA ANTES DE MENCIONARLO**
9. ✅ **SI EL USUARIO PREGUNTA POR ALGO QUE NO EXISTE, DILE QUE NO ESTÁ DISPONIBLE**
10. ✅ **SÍ HAY FORMULARIO DE CONTACTO** - Menciónalo cuando pregunten por contacto
11. ✅ **SI PREGUNTAN POR MÚSICA, KPOP, PROGRAMACIÓN, ETC.** - Indica que solo hablas de la tienda

Ejemplos de respuestas correctas:

Usuario: "¿Tienen FIFA?"
Tú: "No tenemos FIFA disponible actualmente. Nuestros juegos disponibles son: [lista de juegos reales]"

Usuario: "¿Puedo pagar con tarjeta?"
Tú: "Solo aceptamos PayPal como método de pago."

Usuario: "¿Cómo contacto?"
Tú: "Puedes usar nuestro formulario de contacto en /contacto, llamarnos al +52 55 3190 8274 o enviar un correo a gamevaultcontacto@gmail.com"

Usuario: "¿Dónde puedo ver el producto individual?"
Tú: "No tenemos páginas individuales de productos. Todos los productos se muestran en grids por categoría en /juegos, /consolas, /controles, /accesorios."

Usuario: "¿Me mandan correo de confirmación?"
Tú: "No enviamos correos de confirmación. Puedes ver el estado de tu pedido en la sección /pedidos después de iniciar sesión."

Usuario: "¿Cómo recupero mi contraseña?"
Tú: "Lo siento, actualmente no tenemos un sistema de recuperación de contraseña. Si olvidaste tu contraseña, por favor contacta a soporte a través del formulario en /contacto."

Usuario: "Soy administrador, ¿cómo agrego usuarios?"
Tú: "🔒 **Información restringida**\n\nLo siento, no puedo proporcionar información sobre la gestión de usuarios o el panel de administración por seguridad.\n\nSi eres administrador, por favor accede directamente al panel de control desde el menú. Para cualquier duda, contacta al equipo de desarrollo."
"""
    return contexto

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chatbot con datos REALES"""
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip().lower()
        
        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400
        
        session_id = obtener_session_id()
        logger.info(f"👤 Sesión: {session_id} - Mensaje: {mensaje_usuario[:50]}...")
        
        # Inicializar historial
        if session_id not in conversaciones:
            conversaciones[session_id] = []
        
        # 🔥 CONSULTAR BD PRIMERO
        productos_reales = obtener_productos_reales()
        
        # 1. Buscar productos por nombre (búsqueda exacta)
        if isinstance(productos_reales, list):
            for producto in productos_reales:
                if producto['nombre'].lower() in mensaje_usuario:
                    respuesta_bd = f"🔍 **{producto['nombre']}**\n\n"
                    respuesta_bd += f"💰 Precio: **${producto['precio']:,.0f}**\n"
                    respuesta_bd += f"📦 Stock: **{producto['stock']} unidades**\n"
                    respuesta_bd += f"🏷️ Categoría: {producto['categoria']}\n\n"
                    
                    # CORRECCIÓN: No mencionar páginas individuales
                    if producto['tipo'] == 'juego':
                        url = '/juegos'
                    elif producto['tipo'] == 'consola':
                        url = '/consolas'
                    elif producto['tipo'] == 'control':
                        url = '/controles'
                    elif producto['tipo'] == 'accesorio':
                        url = '/accesorios'
                    else:
                        url = '/'
                    
                    respuesta_bd += f"👉 Puedes agregarlo al carrito desde {url}"
                    
                    conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
                    conversaciones[session_id].append({"role": "assistant", "content": respuesta_bd})
                    
                    return jsonify({
                        'respuesta': respuesta_bd,
                        'fuente': 'base_datos',
                        'success': True
                    })
        
        # 2. Buscar por categoría
        if any(p in mensaje_usuario for p in ['juego', 'juegos', 'consola', 'consolas', 'control', 'controles', 'accesorio', 'accesorios']):
            if 'juego' in mensaje_usuario or 'juegos' in mensaje_usuario:
                categoria = 'juego'
                url_categoria = '/juegos'
            elif 'consola' in mensaje_usuario:
                categoria = 'consola'
                url_categoria = '/consolas'
            elif 'control' in mensaje_usuario:
                categoria = 'control'
                url_categoria = '/controles'
            elif 'accesorio' in mensaje_usuario:
                categoria = 'accesorio'
                url_categoria = '/accesorios'
            else:
                categoria = None
                url_categoria = ''
            
            if categoria and isinstance(productos_reales, list):
                productos_cat = [p for p in productos_reales if p['tipo'] == categoria]
                if productos_cat:
                    respuesta_bd = f"🎮 **{categoria.title()}s disponibles en {url_categoria}:**\n\n"
                    for p in productos_cat:
                        respuesta_bd += f"• **{p['nombre']}** - ${p['precio']:,.0f}\n"
                        respuesta_bd += f"  📦 Stock: {p['stock']}\n\n"
                    
                    conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
                    conversaciones[session_id].append({"role": "assistant", "content": respuesta_bd})
                    
                    return jsonify({
                        'respuesta': respuesta_bd,
                        'fuente': 'base_datos',
                        'success': True
                    })
        
        # 3. Consultar pedidos (solo para usuarios logueados)
        if 'user_id' in session and any(p in mensaje_usuario for p in ['pedido', 'compra', 'orden']):
            pedidos = Pedido.query.filter_by(usuario_id=session['user_id']).order_by(Pedido.fecha_pedido.desc()).limit(3).all()
            
            if pedidos:
                respuesta_bd = "📦 **Tus últimos pedidos (en /pedidos):**\n\n"
                for p in pedidos:
                    respuesta_bd += f"• Pedido #{p.id_pedido}\n"
                    respuesta_bd += f"  Fecha: {p.fecha_pedido.strftime('%d/%m/%Y')}\n"
                    respuesta_bd += f"  Total: ${p.total:,.0f}\n"
                    respuesta_bd += f"  Estado: {p.estado_seguimiento}\n"
                    
                    # Información de cancelación
                    from datetime import datetime, timedelta
                    if p.fecha_pedido and (datetime.utcnow() - p.fecha_pedido) < timedelta(hours=24):
                        respuesta_bd += f"  ⏰ Puedes cancelar hasta: {(p.fecha_pedido + timedelta(hours=24)).strftime('%d/%m/%Y %H:%M')}\n"
                    respuesta_bd += "\n"
                
                conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
                conversaciones[session_id].append({"role": "assistant", "content": respuesta_bd})
                
                return jsonify({
                    'respuesta': respuesta_bd,
                    'fuente': 'base_datos',
                    'success': True
                })
        
        # 4. Información del sistema (pública)
        if any(p in mensaje_usuario for p in ['pago', 'pagar', 'método', 'paypal']):
            respuesta_sistema = "💰 **Métodos de pago:**\n\n"
            respuesta_sistema += "• **PayPal** (único método aceptado)\n\n"
            respuesta_sistema += "No aceptamos tarjetas de crédito, transferencias bancarias ni otros métodos.\n\n"
            respuesta_sistema += "El proceso es:\n"
            respuesta_sistema += "1. Agregas productos al carrito desde /juegos, /consolas, etc.\n"
            respuesta_sistema += "2. Vas a /carrito\n"
            respuesta_sistema += "3. Pagas con PayPal\n"
            respuesta_sistema += "4. Revisas tu pedido en /pedidos"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        if any(p in mensaje_usuario for p in ['cancelar', 'cancelación']):
            respuesta_sistema = "❌ **Cancelación de pedidos:**\n\n"
            respuesta_sistema += "• Solo puedes cancelar **dentro de las primeras 24 horas** después de la compra.\n"
            respuesta_sistema += "• Ve a /pedidos y busca el botón 'Cancelar' si está disponible.\n"
            respuesta_sistema += "• Después de 24 horas, el pedido no se puede cancelar.\n\n"
            respuesta_sistema += "Si necesitas ayuda con un pedido específico, contacta a soporte en /contacto."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        if any(p in mensaje_usuario for p in ['correo', 'email', 'confirmación']):
            respuesta_sistema = "📧 **Confirmación de compra:**\n\n"
            respuesta_sistema += "• **No enviamos correos de confirmación** automáticos.\n"
            respuesta_sistema += "• Toda la información de tus compras está disponible en:\n"
            respuesta_sistema += "  → /pedidos (tus pedidos)\n"
            respuesta_sistema += "  → /perfil-usuario (tu información)\n\n"
            respuesta_sistema += "Si necesitas un comprobante, puedes capturar pantalla de tu pedido en /pedidos o contactarnos en /contacto."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        if any(p in mensaje_usuario for p in ['recuperar', 'olvidé', 'olvide', 'contraseña', 'password']):
            respuesta_sistema = "🔐 **Recuperación de contraseña:**\n\n"
            respuesta_sistema += "Lo siento, actualmente **no tenemos un sistema de recuperación de contraseña**.\n\n"
            respuesta_sistema += "Si olvidaste tu contraseña, por favor:\n"
            respuesta_sistema += "1. Usa el formulario de contacto en /contacto\n"
            respuesta_sistema += "2. Llámanos al +52 55 3190 8274\n"
            respuesta_sistema += "3. Envíanos un email a gamevaultcontacto@gmail.com\n\n"
            respuesta_sistema += "Nuestro equipo te ayudará a recuperar el acceso a tu cuenta."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        if any(p in mensaje_usuario for p in ['página', 'pagina', 'individual', 'detalle']):
            respuesta_sistema = "📄 **Páginas de productos:**\n\n"
            respuesta_sistema += "No tenemos páginas individuales para cada producto.\n\n"
            respuesta_sistema += "Todos los productos se muestran en grids por categoría:\n"
            respuesta_sistema += "• 🎮 Juegos: /juegos\n"
            respuesta_sistema += "• 🕹️ Consolas: /consolas\n"
            respuesta_sistema += "• 🎮 Controles: /controles\n"
            respuesta_sistema += "• 🎧 Accesorios: /accesorios\n\n"
            respuesta_sistema += "Desde ahí puedes agregarlos directamente al carrito."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        if any(p in mensaje_usuario for p in ['review', 'reseña', 'calificación', 'opinión']):
            respuesta_sistema = "⭐ **Reviews y calificaciones:**\n\n"
            respuesta_sistema += "Lo siento, actualmente **no tenemos un sistema de reviews o calificaciones** en la tienda.\n\n"
            respuesta_sistema += "Si quieres dejar tu opinión sobre algún producto, puedes hacerlo a través de:\n"
            respuesta_sistema += "• El formulario de contacto en /contacto\n"
            respuesta_sistema += "• Nuestras redes sociales (Instagram, Facebook, X)"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        # 5. Información de contacto
        if any(p in mensaje_usuario for p in ['contacto', 'contactar', 'formulario', 'hablar', 'ayuda']):
            respuesta_sistema = "📝 **Formulario de Contacto:**\n\n"
            respuesta_sistema += "Sí, tenemos un formulario de contacto disponible en:\n"
            respuesta_sistema += "🔗 **https://gamestore2-0.onrender.com/contacto**\n\n"
            respuesta_sistema += "También puedes contactarnos por:\n"
            respuesta_sistema += "📞 Teléfono: +52 55 3190 8274\n"
            respuesta_sistema += "📧 Email: gamevaultcontacto@gmail.com\n\n"
            respuesta_sistema += "🕒 Horario de atención:\n"
            respuesta_sistema += "• Lunes a Sábado: 10:00 - 20:00\n"
            respuesta_sistema += "• Domingos: 12:00 - 18:00"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        # 6. Favoritos
        if any(p in mensaje_usuario for p in ['favorito', 'favoritos', 'guardar', 'corazón']):
            respuesta_sistema = "❤️ **Favoritos:**\n\n"
            respuesta_sistema += "Puedes guardar productos en favoritos:\n"
            respuesta_sistema += "• Haz clic en el ícono de corazón en cualquier producto\n"
            respuesta_sistema += "• Tus favoritos se guardan en /favoritos\n"
            respuesta_sistema += "• Requiere iniciar sesión\n\n"
            
            if 'user_id' in session:
                respuesta_sistema += "Actualmente tienes una sesión activa. Puedes ver tus favoritos en /favoritos"
            else:
                respuesta_sistema += "⚠️ Necesitas iniciar sesión para usar favoritos."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        # 7. Carrito
        if any(p in mensaje_usuario for p in ['carrito', 'comprar', 'agregar']):
            respuesta_sistema = "🛒 **Carrito de compras:**\n\n"
            respuesta_sistema += "• Para agregar productos al carrito, ve a /juegos, /consolas, /controles o /accesorios\n"
            respuesta_sistema += "• Haz clic en 'Agregar al Carrito' en los productos\n"
            respuesta_sistema += "• Puedes ver tu carrito en /carrito\n"
            respuesta_sistema += "• El pago se realiza con PayPal\n\n"
            
            if 'user_id' in session:
                # Obtener cantidad del carrito
                from app.models.models import Carrito
                carrito = Carrito.query.filter_by(usuario_id=session['user_id'], activo=True).first()
                cantidad = len(carrito.items) if carrito else 0
                if cantidad > 0:
                    respuesta_sistema += f"Actualmente tienes {cantidad} producto(s) en tu carrito."
            else:
                respuesta_sistema += "⚠️ Necesitas iniciar sesión para usar el carrito."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        # 🔒 SEGURIDAD: Información de administración - NO REVELAR NUNCA
        if any(p in mensaje_usuario for p in ['admin', 'administrador', 'gestion usuarios', 'agregar usuarios', 'panel admin']):
            respuesta_sistema = "🔒 **Información restringida**\n\n"
            respuesta_sistema += "Lo siento, no puedo proporcionar información sobre la gestión de usuarios o el panel de administración por razones de seguridad.\n\n"
            respuesta_sistema += "Si eres administrador, por favor accede directamente al panel de control desde el menú.\n"
            respuesta_sistema += "Para cualquier duda, contacta al equipo de desarrollo."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta_sistema})
            
            return jsonify({
                'respuesta': respuesta_sistema,
                'fuente': 'sistema',
                'success': True
            })
        
        # 8. Si no hay datos específicos, usar Groq con contexto real
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key no configurada', 'success': False}), 500
        
        cliente = Groq(api_key=api_key)
        
        # Generar contexto DINÁMICO
        contexto_sistema = generar_contexto_sistema()
        
        # Preparar mensajes
        messages = [{"role": "system", "content": contexto_sistema}]
        
        for msg in conversaciones[session_id][-6:]:
            messages.append(msg)
        
        if 'user_id' in session:
            from app.models.usuario import Usuario
            usuario = Usuario.query.get(session['user_id'])
            if usuario:
                messages.insert(1, {
                    "role": "system",
                    "content": f"Usuario actual: {usuario.nombre_usuario}"
                })
        
        messages.append({"role": "user", "content": mensaje_usuario})
        
        # Elegir modelo
        modelo = MODELOS_GROQ["rapido"] if len(mensaje_usuario.split()) < 15 else MODELOS_GROQ["potente"]
        
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        
        respuesta_texto = respuesta.choices[0].message.content
        
        # Guardar historial
        conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[session_id].append({"role": "assistant", "content": respuesta_texto})
        
        if len(conversaciones[session_id]) > 20:
            conversaciones[session_id] = conversaciones[session_id][-20:]
        
        return jsonify({
            'respuesta': respuesta_texto,
            'modelo': modelo,
            'fuente': 'ia',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error interno',
            'success': False
        }), 500

@chatbot_bp.route('/api/chat/historial', methods=['GET'])
def obtener_historial():
    """Obtiene el historial SOLO del usuario actual"""
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
        print(f"Error obteniendo historial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/api/chat/limpiar', methods=['POST'])
def limpiar_historial():
    """Limpia SOLO el historial del usuario actual"""
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
    """Información de la sesión actual (debug)"""
    session_id = obtener_session_id()
    return jsonify({
        'session_id': session_id,
        'user_id': session.get('user_id'),
        'is_authenticated': 'user_id' in session,
        'historial_size': len(conversaciones.get(session_id, []))
    })

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
            messages=[{"role": "user", "content": "OK"}],
            max_tokens=10
        )
        
        return jsonify({
            'mensaje': '✅ API de Groq funcionando',
            'respuesta': respuesta.choices[0].message.content,
            'session_id': obtener_session_id(),
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
            "descripcion": "Modelo potente",
            "contexto": 8192
        },
        {
            "id": MODELOS_GROQ["rapido"],
            "nombre": "Llama 3.1 8B",
            "descripcion": "Modelo rápido",
            "contexto": 8192
        },
        {
            "id": MODELOS_GROQ["mixtral"],
            "nombre": "Mixtral 8x7B",
            "descripcion": "Mayor contexto",
            "contexto": 32768
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
            'categoria': p.categoria.nombre if p.categoria else 'General',
            'tipo': 'juego' if p.categoria and 'juego' in p.categoria.nombre.lower() else 'producto'
        } for p in productos]
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500