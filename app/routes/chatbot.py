
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

# MODELOS DE GROQ
MODELOS_GROQ = {
    "rapido": "llama-3.1-8b-instant",
    "potente": "llama-3.3-70b-versatile"
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

def es_administrador():
    """Verifica si el usuario actual es administrador"""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return usuario and usuario.rol_id == 1
    return False

def obtener_productos_reales():
    """Obtiene SOLO los productos que existen en la BD"""
    try:
        productos = Producto.query.filter(
            Producto.activo == True,
            Producto.stock > 0
        ).all()
        
        if not productos:
            return []
        
        lista_productos = []
        for p in productos:
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
                'id': p.id_producto
            })
        
        return lista_productos
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return []

# 🔥 TEMAS NO RELACIONADOS CON LA TIENDA
TEMAS_NO_RELACIONADOS = [
    'clima', 'temperatura', 'lluvia', 'soleado',
    'política', 'politica', 'gobierno', 'presidente', 'votar',
    'música', 'musica', 'canción', 'cancion', 'artista', 'banda', 'kpop', 'rock',
    'película', 'pelicula', 'serie', 'netflix', 'disney',
    'deportes', 'fútbol', 'futbol', 'béisbol', 'beisbol', 'nfl', 'nba',
    'receta', 'cocina', 'comida',
    'viajes', 'vacaciones', 'hotel',
    'tecnología', 'tecnologia', 'celular', 'iphone', 'samsung',
    'programación', 'programacion', 'java', 'python', 'html', 'css',
    'javascript', 'código', 'codigo'
]

def es_tema_no_relacionado(mensaje):
    """Verifica si el mensaje es sobre temas no relacionados con la tienda"""
    mensaje_lower = mensaje.lower()
    for tema in TEMAS_NO_RELACIONADOS:
        if tema in mensaje_lower:
            return True
    return False

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chatbot"""
    try:
        data = request.json
        mensaje_usuario = data.get('mensaje', '').strip()
        
        if not mensaje_usuario:
            return jsonify({'error': 'Mensaje vacío', 'success': False}), 400
        
        mensaje_lower = mensaje_usuario.lower()
        session_id = obtener_session_id()
        logger.info(f"👤 Sesión: {session_id} - Mensaje: {mensaje_usuario[:50]}...")
        
        # Inicializar historial
        if session_id not in conversaciones:
            conversaciones[session_id] = []
        
        # 🔥 VERIFICAR SI ES TEMA NO RELACIONADO
        if es_tema_no_relacionado(mensaje_lower):
            respuesta = "🎮 **Game Store - Asistente Virtual**\n\n"
            respuesta += "Solo puedo ayudarte con temas relacionados a nuestra tienda de videojuegos:\n"
            respuesta += "• Productos disponibles\n"
            respuesta += "• Carrito de compras\n"
            respuesta += "• Pedidos y cancelaciones\n"
            respuesta += "• Contacto y soporte\n\n"
            respuesta += "¿Hay algo sobre la tienda en lo que pueda ayudarte?"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({
                'respuesta': respuesta,
                'fuente': 'sistema',
                'success': True
            })
        
        # 🔥 CONSULTAR BD PRIMERO
        productos_reales = obtener_productos_reales()
        
        # 1. Buscar productos por nombre
        if productos_reales:
            for producto in productos_reales:
                if producto['nombre'].lower() in mensaje_lower:
                    respuesta_bd = f"🔍 **{producto['nombre']}**\n\n"
                    respuesta_bd += f"💰 Precio: **${producto['precio']:,.0f}**\n"
                    respuesta_bd += f"📦 Stock: **{producto['stock']} unidades**\n"
                    respuesta_bd += f"🏷️ Categoría: {producto['categoria']}\n\n"
                    
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
        if any(p in mensaje_lower for p in ['juego', 'juegos', 'consola', 'consolas', 'control', 'controles', 'accesorio', 'accesorios']):
            if 'juego' in mensaje_lower or 'juegos' in mensaje_lower:
                categoria = 'juego'
                url_categoria = '/juegos'
            elif 'consola' in mensaje_lower:
                categoria = 'consola'
                url_categoria = '/consolas'
            elif 'control' in mensaje_lower:
                categoria = 'control'
                url_categoria = '/controles'
            elif 'accesorio' in mensaje_lower:
                categoria = 'accesorio'
                url_categoria = '/accesorios'
            else:
                categoria = None
                url_categoria = ''
            
            if categoria and productos_reales:
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
        if 'user_id' in session and any(p in mensaje_lower for p in ['pedido', 'compra', 'orden']):
            pedidos = Pedido.query.filter_by(usuario_id=session['user_id']).order_by(Pedido.fecha_pedido.desc()).limit(3).all()
            
            if pedidos:
                respuesta_bd = "📦 **Tus últimos pedidos (en /pedidos):**\n\n"
                for p in pedidos:
                    respuesta_bd += f"• Pedido #{p.id_pedido}\n"
                    respuesta_bd += f"  Fecha: {p.fecha_pedido.strftime('%d/%m/%Y')}\n"
                    respuesta_bd += f"  Total: ${p.total:,.0f}\n"
                    respuesta_bd += f"  Estado: {p.estado_seguimiento}\n\n"
                
                conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
                conversaciones[session_id].append({"role": "assistant", "content": respuesta_bd})
                
                return jsonify({
                    'respuesta': respuesta_bd,
                    'fuente': 'base_datos',
                    'success': True
                })
        
        # 4. Información del sistema
        
        # Olvidé mi contraseña - SIEMPRE decir la verdad
        if any(p in mensaje_lower for p in ['olvidé', 'olvide', 'recuperar', 'contraseña', 'password']):
            respuesta = "🔐 **Recuperación de contraseña**\n\n"
            respuesta += "Actualmente **no tenemos un sistema de recuperación de contraseña** en la tienda.\n\n"
            respuesta += "Si olvidaste tu contraseña, puedes:\n"
            respuesta += "1. Usar el formulario de contacto en /contacto\n"
            respuesta += "2. Llamarnos al +52 55 3190 8274\n"
            respuesta += "3. Enviar un email a gamevaultcontacto@gmail.com\n\n"
            respuesta += "Nuestro equipo te ayudará a recuperar el acceso a tu cuenta."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Panel de administración - SOLO para admins
        if any(p in mensaje_lower for p in ['admin', 'administrador', 'gestion usuarios', 'gestión usuarios', 'panel admin']):
            if es_administrador():
                respuesta = "🔧 **Panel de Administración**\n\n"
                respuesta += "Como administrador, tienes acceso a:\n"
                respuesta += "• /dashboard - Panel principal\n"
                respuesta += "• /admin/gestion-productos - Gestionar productos\n"
                respuesta += "• /admin/gestion-usuarios - Gestionar usuarios\n"
                respuesta += "• /admin/gestion-pedidos - Gestionar pedidos\n"
                respuesta += "• /admin/mensajes - Ver mensajes de contacto\n\n"
                respuesta += "¿Necesitas ayuda con alguna sección específica?"
            else:
                respuesta = "🔒 **Información restringida**\n\n"
                respuesta += "Lo siento, solo los administradores pueden acceder a información sobre el panel de control.\n\n"
                respuesta += "Si necesitas ayuda con la tienda, puedo informarte sobre:\n"
                respuesta += "• Productos disponibles\n"
                respuesta += "• Cómo realizar compras\n"
                respuesta += "• Estado de pedidos\n"
                respuesta += "• Contacto y soporte"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Métodos de pago
        if any(p in mensaje_lower for p in ['pago', 'pagar', 'paypal']):
            respuesta = "💰 **Métodos de pago**\n\n"
            respuesta += "• **PayPal** (único método aceptado)\n\n"
            respuesta += "Proceso de compra:\n"
            respuesta += "1. Agrega productos al carrito\n"
            respuesta += "2. Ve a /carrito\n"
            respuesta += "3. Paga con PayPal\n"
            respuesta += "4. Revisa tu pedido en /pedidos"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Cancelaciones
        if any(p in mensaje_lower for p in ['cancelar', 'cancelación']):
            respuesta = "❌ **Cancelación de pedidos**\n\n"
            respuesta += "• Solo puedes cancelar **dentro de las primeras 24 horas**\n"
            respuesta += "• Ve a /pedidos y busca el botón 'Cancelar'\n"
            respuesta += "• Después de 24 horas, el pedido no se puede cancelar\n\n"
            respuesta += "Si tienes problemas, contacta a soporte en /contacto"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Correos de confirmación
        if any(p in mensaje_lower for p in ['correo', 'email', 'confirmación']):
            respuesta = "📧 **Confirmación de compra**\n\n"
            respuesta += "• **No enviamos correos de confirmación**\n"
            respuesta += "• Toda la información de tus compras está en /pedidos\n"
            respuesta += "• Puedes ver el estado y detalles de tus pedidos ahí"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Contacto
        if any(p in mensaje_lower for p in ['contacto', 'contactar', 'ayuda', 'soporte']):
            respuesta = "📝 **Contacto y Soporte**\n\n"
            respuesta += "• Formulario: /contacto\n"
            respuesta += "• Teléfono: +52 55 3190 8274\n"
            respuesta += "• Email: gamevaultcontacto@gmail.com\n\n"
            respuesta += "🕒 Horario de atención:\n"
            respuesta += "• Lunes a Sábado: 10:00 - 20:00\n"
            respuesta += "• Domingos: 12:00 - 18:00"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Favoritos
        if any(p in mensaje_lower for p in ['favorito', 'favoritos']):
            respuesta = "❤️ **Favoritos**\n\n"
            respuesta += "• Haz clic en el ícono de corazón en cualquier producto\n"
            respuesta += "• Tus favoritos se guardan en /favoritos\n"
            respuesta += "• Requiere iniciar sesión"
            
            if 'user_id' in session:
                respuesta += "\n\nActualmente tienes una sesión activa. Puedes ver tus favoritos en /favoritos"
            else:
                respuesta += "\n\n⚠️ Necesitas iniciar sesión para usar favoritos."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # Carrito
        if any(p in mensaje_lower for p in ['carrito', 'comprar']):
            respuesta = "🛒 **Carrito de compras**\n\n"
            respuesta += "• Para agregar productos: /juegos, /consolas, /controles, /accesorios\n"
            respuesta += "• Haz clic en 'Agregar al Carrito'\n"
            respuesta += "• Revisa tu carrito en /carrito\n"
            respuesta += "• Paga con PayPal\n\n"
            
            if 'user_id' in session:
                from app.models.models import Carrito
                carrito = Carrito.query.filter_by(usuario_id=session['user_id'], activo=True).first()
                cantidad = len(carrito.items) if carrito else 0
                if cantidad > 0:
                    respuesta += f"Actualmente tienes **{cantidad} producto(s)** en tu carrito."
            else:
                respuesta += "⚠️ Necesitas iniciar sesión para usar el carrito."
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({'respuesta': respuesta, 'fuente': 'sistema', 'success': True})
        
        # 5. Si no hay match específico, mostrar productos disponibles
        if productos_reales:
            respuesta = "🎮 **Game Store - Productos disponibles**\n\n"
            
            juegos = [p for p in productos_reales if p['tipo'] == 'juego']
            if juegos:
                respuesta += "**Juegos:**\n"
                for j in juegos[:3]:
                    respuesta += f"• {j['nombre']} - ${j['precio']:,.0f}\n"
            
            consolas = [p for p in productos_reales if p['tipo'] == 'consola']
            if consolas:
                respuesta += "\n**Consolas:**\n"
                for c in consolas:
                    respuesta += f"• {c['nombre']} - ${c['precio']:,.0f}\n"
            
            controles = [p for p in productos_reales if p['tipo'] == 'control']
            if controles:
                respuesta += "\n**Controles:**\n"
                for ct in controles[:3]:
                    respuesta += f"• {ct['nombre']} - ${ct['precio']:,.0f}\n"
            
            accesorios = [p for p in productos_reales if p['tipo'] == 'accesorio']
            if accesorios:
                respuesta += "\n**Accesorios:**\n"
                for a in accesorios[:3]:
                    respuesta += f"• {a['nombre']} - ${a['precio']:,.0f}\n"
            
            respuesta += "\n¿Quieres saber más sobre algún producto en específico?"
            
            conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
            conversaciones[session_id].append({"role": "assistant", "content": respuesta})
            
            return jsonify({
                'respuesta': respuesta,
                'fuente': 'sistema',
                'success': True
            })
        
        # 6. Respuesta por defecto
        respuesta_default = "🏪 **Game Store**\n\n"
        respuesta_default += "Bienvenido al asistente virtual. ¿En qué puedo ayudarte?\n\n"
        respuesta_default += "Puedo informarte sobre:\n"
        respuesta_default += "• Productos disponibles\n"
        respuesta_default += "• Cómo comprar en la tienda\n"
        respuesta_default += "• Estado de pedidos\n"
        respuesta_default += "• Contacto y soporte"
        
        conversaciones[session_id].append({"role": "user", "content": mensaje_usuario})
        conversaciones[session_id].append({"role": "assistant", "content": respuesta_default})
        
        return jsonify({
            'respuesta': respuesta_default,
            'fuente': 'sistema',
            'success': True
        })
        
    except Exception as