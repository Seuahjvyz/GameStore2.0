from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app import db
import datetime
from flask import Flask, request, jsonify,  current_app
from app.models.pedido import Pedido, PedidoItem
from app.models.usuario import Usuario
from app.models.models import Carrito, CarritoItem, Producto, Categoria
from app.models.role import Role
from app.models.favorito import Favorito

web_bp = Blueprint('web', __name__)

# ----------------------------------------- DECORATORS ---------------------------------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f" login_required EJECUTÁNDOSE para: {request.path}")
        print(f" Session data: {dict(session)}")
        print(f" user_id en session: {'user_id' in session}")
        
        # VERIFICACIÓN BÁSICA
        if 'user_id' not in session:
            print("REDIRIGIENDO a login - usuario NO autenticado")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': 'Sesión no válida',
                    'redirect': '/login'
                }), 401
            
            return redirect(url_for('web.login'))
        
        # VERIFICAR QUE EL USUARIO SIGA ACTIVO EN BD
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or not usuario.activo:
            print(f"Usuario {session['user_id']} desactivado - cerrando sesión")
            session.clear()
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': 'Tu cuenta ha sido desactivada',
                    'redirect': '/login?desactivada=true'
                }), 401
            
            return redirect(url_for('web.login', desactivada=True))
        
        # VERIFICAR TIEMPO DE INACTIVIDAD
        last_activity = session.get('last_activity')
        if last_activity:
            if isinstance(last_activity, str):
                try:
                    last_activity = datetime.datetime.fromisoformat(last_activity)
                    tiempo_inactivo = (datetime.datetime.now() - last_activity).seconds
                    if tiempo_inactivo > 3000:  # 30 minutos
                        session.clear()
                        if request.path.startswith('/api/'):
                            return jsonify({
                                'success': False, 
                                'error': 'Sesión expirada por inactividad',
                                'redirect': '/login'
                            }), 401
                        return redirect(url_for('web.login'))
                except:
                    pass
        
        print("✅ Acceso PERMITIDO - usuario autenticado y activo")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar autenticación primero
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'No autenticado'}), 401
            return redirect(url_for('web.login'))
        
        # 🔥 VERIFICAR QUE EL USUARIO SIGA ACTIVO
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or not usuario.activo:
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': 'Tu cuenta ha sido desactivada'
                }), 401
            return redirect(url_for('web.login', desactivada=True))
        
        # Verificar rol de administrador (1)
        if session.get('user_role') != 1:
            print(f"Acceso denegado - Usuario {session.get('user_id')} con rol {session.get('user_role')} intentó acceder a ruta admin")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': 'Acceso denegado'
                }), 403
            
            return redirect('/')
        
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------- RUTAS PRINCIPALES ---------------------------------------- #

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/login')
def login():
    return render_template('login.html')

@web_bp.route('/registro')
def registro():
    return render_template('registro.html')

@web_bp.route('/sobre-nosotros')
def sobre_nosotros():
    return render_template('sobre-nosotros.html')

@web_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')

# ----------------------------------------- RUTAS ADMINISTRADOR ---------------------------------------- #

@web_bp.route('/admin/gestion-productos')
@admin_required
def admin_productos():
    return render_template('admin_templates/gestion-productos.html')

@web_bp.route('/admin/registro-admin')
@admin_required
def admin_registro():
    return render_template('admin_templates/registro-admin.html')

@web_bp.route('/admin/gestion-usuarios')
@admin_required
def admin_usuarios():
    return render_template('admin_templates/gestion-usuarios.html')

@web_bp.route('/admin/reportes')
@admin_required
def admin_reportes():
    return render_template('admin_templates/reportes.html')

@web_bp.route('/admin/reporte-detalle')
@admin_required
def admin_reporte_detalle():
    return render_template('admin_templates/reporte-detalle.html')

@web_bp.route('/admin/gestion-pedidos')
@admin_required
def admin_pedidos():
    return render_template('admin_templates/gestion-pedidos.html')

@web_bp.route('/admin/perfil-admin')
@admin_required
def admin_perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('admin_templates/perfil-admin.html', usuario=usuario)

@web_bp.route('/dashboard')
@admin_required
def admin():
    """Ruta principal del administrador - SOLO accesible para rol 1"""
    return render_template('admin_templates/dashboard.html')

# ----------------------------------------- RUTAS DE USUARIO ---------------------------------------- #

@web_bp.route('/juegos')
def juegos():
    return render_template('juegos.html')

@web_bp.route('/consolas')
def consolas():
    return render_template('consolas.html')

@web_bp.route('/controles')
def controles():
    return render_template('controles.html')

@web_bp.route('/accesorios')
def accesorios():
    return render_template('accesorios.html')

@web_bp.route('/favoritos')
@login_required
def favoritos():
    return render_template('favoritos.html', usuario_actual=session.get('user_id'))


@web_bp.route('/perfil-usuario')
@login_required
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfil-usuario.html', usuario=usuario)

@web_bp.route('/pedidos')
@login_required
def pedidos():
    return render_template('pedidos.html')

@web_bp.route('/pagar')
@login_required
def pagar():
    return render_template('Pagar.html')

@web_bp.route('/compra-finalizada')
def compra_finalizada():
    return render_template('CompraFinalizada.html')

@web_bp.route('/carrito')
@login_required
def carrito():
    return render_template('Carrito.html', usuario_actual=session.get('user_id'))


# ----------------------------------------- AUTENTICACIÓN Y SESIÓN ---------------------------------------- #


@web_bp.route('/pago-exitoso')
def pago_exitoso():
    """Página de confirmación de pago exitoso"""
    return render_template('pago_exitoso.html')

@web_bp.route('/pago-cancelado')
def pago_cancelado():
    """Página cuando el pago es cancelado"""
    return render_template('pago_cancelado.html')


# ----------------------------------------- AUTENTICACIÓN Y SESIÓN ---------------------------------------- #

# En web.py - Ruta de login
@web_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        login_input = data.get('login_input')
        password = data.get('password')
        
        if not login_input or not password:
            return jsonify({'error': 'Completa todos los campos'}), 400
        
        # Buscar usuario
        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == login_input) | (Usuario.correo == login_input)
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # 🔥 VERIFICAR SI LA CUENTA ESTÁ ACTIVA
        if not usuario.activo:
            return jsonify({
                'error': 'Tu cuenta ha sido desactivada. Contacta al administrador.'
            }), 403  # 403 = Forbidden
        
        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Crear sesión
        session.clear()
        session['user_id'] = usuario.id_usuario
        session['username'] = usuario.nombre_usuario
        session['user_role'] = usuario.rol_id
        session['last_activity'] = datetime.datetime.now().isoformat()
        
        # Redirigir según rol
        if usuario.rol_id == 1:
            redirect_url = '/dashboard'
        else:
            redirect_url = '/'
        
        return jsonify({
            'success': True, 
            'message': 'Login exitoso',
            'redirect_url': redirect_url,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id,
                'activo': usuario.activo  # Incluir estado
            }
        }), 200
        
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@web_bp.route('/logout')
def logout():
    session.clear()
    response = redirect('/')
    response.delete_cookie('session')  # 'session' es el nombre por defecto
    
    return response

@web_bp.route('/api/user-info')
def user_info():
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            }
        })
    else:
        return jsonify({'logged_in': False})

@web_bp.route('/api/usuario/actual')
def api_usuario_actual():
    """Obtener información del usuario actual"""
    try:
        if 'user_id' in session:
            usuario = Usuario.query.get(session['user_id'])
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            return jsonify({
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            })
        else:
            return jsonify({'error': 'No autenticado'}), 401
    except Exception as e:
        print(f"Error en api_usuario_actual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ----------------------------------------- REGISTROS ---------------------------------------- #

@web_bp.route('/api/registro', methods=['POST'])
def api_registro():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'error': 'Este email ya está registrado'}), 400
        
        # Crear usuario normal
        nuevo_usuario = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=2  # Cliente
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        print(f"USUARIO GUARDADO EN BD: {username}, Email: {email}")
        
        return jsonify({
            'success': True, 
            'message': 'Usuario registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/registro-admin', methods=['POST'])
def api_registro_admin():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'error': 'Este email ya está registrado'}), 400
        
        # Crear administrador
        nuevo_admin = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=1  # Administrador
        )
        
        db.session.add(nuevo_admin)
        db.session.commit()
        
        print(f"ADMINISTRADOR GUARDADO EN BD: {username}, Email: {email}")
        
        return jsonify({
            'success': True, 
            'message': 'Administrador registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro admin: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ----------------------------------------- API PRODUCTOS ---------------------------------------- #

@web_bp.route('/api/productos')
def api_productos():
    try:
        # Obtener parámetro de categoría si existe
        categoria_nombre = request.args.get('categoria')
        
        # ✅ SOLO MOSTRAR PRODUCTOS ACTIVOS Y CON STOCK > 0
        if categoria_nombre:
            productos = Producto.query.join(Categoria).filter(
                Categoria.nombre == categoria_nombre,
                Producto.activo == True,
                Producto.stock > 0  # ✅ SOLO productos con stock
            ).all()
            print(f"🔍 Filtrando por categoría: {categoria_nombre}, encontrados: {len(productos)} productos")
        else:
            # Todos los productos activos con stock
            productos = Producto.query.filter(
                Producto.activo == True,
                Producto.stock > 0  # ✅ SOLO productos con stock
            ).all()
            print(f"📦 Todos los productos activos con stock, encontrados: {len(productos)} productos")
        
        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'categoria_id': producto.categoria_id
            })
        
        return jsonify({
            'success': True,
            'productos': productos_data,
            'filtro_aplicado': categoria_nombre if categoria_nombre else 'todos'
        })
        
    except Exception as e:
        print(f" Error obteniendo productos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

@web_bp.route('/api/productos/categoria/<int:categoria_id>')
def api_productos_por_categoria(categoria_id):
    try:
        #  SOLO productos activos y con stock
        productos = Producto.query.filter(
            Producto.categoria_id == categoria_id,
            Producto.activo == True,
            Producto.stock > 0  # SOLO productos con stock
        ).all()
        
        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria_id': producto.categoria_id
            })
        
        return jsonify({
            'success': True,
            'productos': productos_data
        })
        
    except Exception as e:
        print(f"Error obteniendo productos por categoría: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

# ----------------------------------------- CARRITO API ---------------------------------------- #

@web_bp.route('/api/carrito/cantidad')
def api_carrito_cantidad():
    """Obtener cantidad de items en el carrito"""
    try:
        if 'user_id' not in session:
            return jsonify({'count': 0})
        
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        count = len(carrito.items) if carrito else 0
        return jsonify({'count': count})
        
    except Exception as e:
        print(f"Error obteniendo cantidad del carrito: {e}")
        return jsonify({'count': 0})

@web_bp.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    try:
        print(f"🎯 INICIANDO agregar_al_carrito - User: {session.get('user_id')}")
        
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Inicia sesion para poder agregar productos al carrito'}), 401

        data = request.get_json()
        print(f"📦 Datos recibidos: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)

        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        # Convertir a entero para evitar problemas de tipo
        producto_id = int(producto_id)
        cantidad = int(cantidad)

        print(f"🔍 Buscando producto {producto_id}")
        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Buscar carrito activo del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            carrito = Carrito(usuario_id=session['user_id'])
            db.session.add(carrito)
            db.session.flush()

        # Buscar item existente
        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id
        ).first()

        if item_existente:
            # Si ya existe, calcular nueva cantidad
            nueva_cantidad = item_existente.cantidad + cantidad
            
            # 🔥 VERIFICAR STOCK DISPONIBLE (considerando lo que ya tiene en carrito)
            if nueva_cantidad > producto.stock:
                return jsonify({
                    'success': False, 
                    'error': f'Solo hay {producto.stock} unidades disponibles. Ya tienes {item_existente.cantidad} en tu carrito.'
                }), 400
            
            item_existente.cantidad = nueva_cantidad
            mensaje = f'Cantidad actualizada: ahora tienes {nueva_cantidad} unidades'
            accion = 'actualizado'
        else:
            # Si no existe, verificar stock para nueva compra
            if cantidad > producto.stock:
                return jsonify({
                    'success': False, 
                    'error': f'Solo hay {producto.stock} unidades disponibles'
                }), 400
            
            nuevo_item = CarritoItem(
                carrito_id=carrito.id_carrito,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(nuevo_item)
            mensaje = 'Producto agregado al carrito'
            accion = 'agregado'

        db.session.commit()
        print(f"Commit exitoso - {accion}")
        
        # Obtener el conteo actualizado
        carrito_actualizado = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        count = len(carrito_actualizado.items) if carrito_actualizado else 0
        
        print(f"🎉 Carrito {accion} exitosamente. Total items: {count}")
        
        return jsonify({
            'success': True, 
            'message': mensaje,
            'carrito_count': count,
            'accion': accion
        })

    except Exception as e:
        db.session.rollback()
        print(f"ERROR en agregar_al_carrito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/carrito/detalles')
def api_carrito_detalles():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            return jsonify({
                'success': True,
                'carrito': {
                    'items': [],
                    'subtotal': 0,
                    'total': 0,
                    'count': 0
                }
            })

        items_data = []
        subtotal = 0
        items_a_eliminar = []  # Lista para items que debemos eliminar
        
        for item in carrito.items:
            producto = Producto.query.get(item.producto_id)
            
            # 🔥 VERIFICAR SI EL PRODUCTO EXISTE Y ESTÁ ACTIVO
            if not producto or not producto.activo:
                # Producto no existe o está inactivo - marcarlo para eliminar
                items_a_eliminar.append(item)
                print(f"⚠️ Producto {item.producto_id} no disponible - será eliminado del carrito")
                continue
            
            # Producto válido - calcular total
            item_total = float(item.precio_unitario) * item.cantidad
            subtotal += item_total
            
            items_data.append({
                'id': item.id_item,
                'producto_id': item.producto_id,
                'nombre': producto.nombre,
                'precio_unitario': float(item.precio_unitario),
                'cantidad': item.cantidad,
                'total': item_total,
                'imagen': producto.imagen,
                'stock': producto.stock,
                'activo': producto.activo
            })
        
        # 🔥 ELIMINAR ITEMS DE PRODUCTOS INACTIVOS O ELIMINADOS
        if items_a_eliminar:
            for item in items_a_eliminar:
                db.session.delete(item)
            db.session.commit()
            print(f"✅ Eliminados {len(items_a_eliminar)} items del carrito por productos no disponibles")
        
        return jsonify({
            'success': True,
            'carrito': {
                'items': items_data,
                'subtotal': subtotal,
                'total': subtotal,
                'count': len(items_data)
            }
        })

    except Exception as e:
        print(f"Error obteniendo carrito: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
    
@web_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
def actualizar_cantidad_carrito(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json()
        nueva_cantidad = data.get('cantidad', 1)

        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        if not carrito or item.carrito_id != carrito.id_carrito:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403

        producto = Producto.query.get(item.producto_id)
        if nueva_cantidad > producto.stock:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400

        if nueva_cantidad <= 0:
            db.session.delete(item)
        else:
            item.cantidad = nueva_cantidad

        db.session.commit()
        return jsonify({'success': True, 'message': 'Carrito actualizado'})

    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando carrito: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
    


@web_bp.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
def eliminar_item_carrito(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        if not carrito or item.carrito_id != carrito.id_carrito:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403

        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto eliminado del carrito'})

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando item: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@web_bp.route('/api/carrito/limpiar-duplicados', methods=['POST'])
@login_required
def limpiar_duplicados_carrito():
    """Limpiar productos duplicados del carrito"""
    try:
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            return jsonify({'success': True, 'message': 'No hay carrito'})

        # Encontrar duplicados
        items_por_producto = {}
        items_a_eliminar = []
        
        for item in carrito.items:
            if item.producto_id in items_por_producto:
                # Ya existe un item para este producto, marcar para eliminar
                items_a_eliminar.append(item)
                # Sumar la cantidad al item existente
                items_por_producto[item.producto_id].cantidad += item.cantidad
            else:
                items_por_producto[item.producto_id] = item

        # Eliminar duplicados
        for item in items_a_eliminar:
            db.session.delete(item)

        if items_a_eliminar:
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': f'Se limpiaron {len(items_a_eliminar)} productos duplicados',
                'duplicados_eliminados': len(items_a_eliminar)
            })
        else:
            return jsonify({'success': True, 'message': 'No se encontraron duplicados'})

    except Exception as e:
        db.session.rollback()
        print(f"Error limpiando duplicados: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

# ----------------------------------------- API FAVORITOS ---------------------------------------- #

@web_bp.route('/api/favoritos')
@login_required
def api_favoritos():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Debes iniciar sesión para ver favoritos'}), 401
        
        usuario_id = session['user_id']
        
        # Obtener favoritos con información del producto y categoría
        favoritos = Favorito.query.filter_by(usuario_id=usuario_id)\
            .join(Producto)\
            .join(Categoria)\
            .all()
        
        favoritos_data = []
        for favorito in favoritos:
            producto = favorito.producto
            favoritos_data.append({
                'id': favorito.id_favorito,
                'fecha_agregado': favorito.fecha_agregado.isoformat() if favorito.fecha_agregado else None,
                'producto': {
                    'id': producto.id_producto,
                    'nombre': producto.nombre,
                    'descripcion': producto.descripcion,
                    'precio': float(producto.precio) if producto.precio else 0,
                    'stock': producto.stock,
                    'imagen': producto.imagen,
                    'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                    'categoria_id': producto.categoria_id
                }
            })
        
        return jsonify({
            'success': True,
            'favoritos': favoritos_data,
            'count': len(favoritos)
        })
        
    except Exception as e:
        print(f"Error obteniendo favoritos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener favoritos'}), 500

@web_bp.route('/api/favoritos/agregar', methods=['POST'])
@login_required
def api_agregar_favorito():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        # Verificar si el producto existe
        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Verificar si ya está en favoritos
        favorito_existente = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        if favorito_existente:
            return jsonify({'success': False, 'error': 'El producto ya está en favoritos'}), 400

        # Agregar a favoritos
        nuevo_favorito = Favorito(
            usuario_id=session['user_id'],
            producto_id=producto_id
        )

        db.session.add(nuevo_favorito)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto agregado a favoritos'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error agregando favorito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/favoritos/eliminar/<int:producto_id>', methods=['DELETE'])
@login_required
def api_eliminar_favorito(producto_id):
    try:
        favorito = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        if not favorito:
            return jsonify({'success': False, 'error': 'Favorito no encontrado'}), 404

        db.session.delete(favorito)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto eliminado de favoritos'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando favorito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/favoritos/verificar/<int:producto_id>')
@login_required
def api_verificar_favorito(producto_id):
    try:
        favorito = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        return jsonify({
            'success': True,
            'es_favorito': favorito is not None
        })

    except Exception as e:
        print(f"Error verificando favorito: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# ----------------------------------------- API ADMIN PRODUCTOS ---------------------------------------- #

@web_bp.route('/api/admin/productos')
@admin_required
def api_admin_productos():
    try:
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria', '')
        estado = request.args.get('estado', '')

        # Consulta base
        query = Producto.query.join(Categoria)

        # Aplicar filtros
        if search:
            query = query.filter(Producto.nombre.ilike(f'%{search}%'))
        
        if categoria_id:
            query = query.filter(Producto.categoria_id == categoria_id)
        
        if estado:
            if estado == 'activo':
                query = query.filter(Producto.activo == True)
            elif estado == 'inactivo':
                query = query.filter(Producto.activo == False)

        productos = query.order_by(Producto.fecha_creacion.desc()).all()

        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'categoria_id': producto.categoria_id,
                'activo': producto.activo,
                'fecha_creacion': producto.fecha_creacion.isoformat() if producto.fecha_creacion else None
            })

        return jsonify({
            'success': True,
            'productos': productos_data
        })
        
    except Exception as e:
        print(f"Error obteniendo productos admin: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

@web_bp.route('/api/categorias')
@admin_required
def api_categorias():
    try:
        categorias = Categoria.query.all()
        
        categorias_data = [{
            'id': cat.id_categoria,
            'nombre': cat.nombre,
            'descripcion': cat.descripcion
        } for cat in categorias]

        return jsonify({
            'success': True,
            'categorias': categorias_data
        })
        
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener categorías'}), 500

@web_bp.route('/api/admin/productos/agregar', methods=['POST'])
@admin_required
def api_admin_agregar_producto():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data.get('nombre'):
            return jsonify({'success': False, 'error': 'El nombre es requerido'}), 400
        
        if not data.get('precio') or float(data.get('precio')) <= 0:
            return jsonify({'success': False, 'error': 'El precio debe ser mayor a 0'}), 400
        
        if data.get('stock') is None or int(data.get('stock')) < 0:
            return jsonify({'success': False, 'error': 'El stock no puede ser negativo'}), 400

        if not data.get('categoria_id'):
            return jsonify({'success': False, 'error': 'La categoría es requerida'}), 400

        # Crear nuevo producto
        nuevo_producto = Producto(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            precio=float(data.get('precio')),
            stock=int(data.get('stock')),
            imagen=data.get('imagen', ''),
            categoria_id=data.get('categoria_id'),
            activo=data.get('activo', True)
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto agregado correctamente',
            'producto_id': nuevo_producto.id_producto
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error agregando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al agregar producto'}), 500

@web_bp.route('/api/admin/productos/editar', methods=['PUT'])
@admin_required
def api_admin_editar_producto():
    try:
        data = request.get_json()
        producto_id = data.get('id')
        
        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto requerido'}), 400

        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Actualizar campos
        stock_anterior = producto.stock
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'precio' in data:
            producto.precio = float(data['precio'])
        if 'stock' in data:
            nuevo_stock = int(data['stock'])
            producto.stock = nuevo_stock
            
            #  DESHABILITAR SI EL NUEVO STOCK ES 0
            if nuevo_stock == 0:
                producto.activo = False
            # HABILITAR SI HABÍA STOCK 0 Y AHORA TIENE STOCK
            elif nuevo_stock > 0 and stock_anterior == 0:
                producto.activo = True
                
        if 'imagen' in data:
            producto.imagen = data['imagen']
        if 'categoria_id' in data:
            producto.categoria_id = data['categoria_id']
        if 'activo' in data:
            # Si el admin manualmente activa un producto con stock 0, prevenir
            if data['activo'] and producto.stock == 0:
                return jsonify({
                    'success': False, 
                    'error': 'No se puede activar un producto con stock 0'
                }), 400
            producto.activo = data['activo']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error editando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al editar producto'}), 500

@web_bp.route('/api/admin/productos/estado', methods=['PUT'])
@admin_required
def api_admin_cambiar_estado():
    try:
        data = request.get_json()
        producto_id = data.get('id')
        activo = data.get('activo')

        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Cambiar estado sin restricciones
        producto.activo = activo
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Estado del producto actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando estado: {e}")
        return jsonify({'success': False, 'error': 'Error al cambiar estado'}), 500

@web_bp.route('/api/admin/productos/eliminar/<int:producto_id>', methods=['DELETE'])
@admin_required
def api_admin_eliminar_producto(producto_id):
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # 1. Eliminar items del carrito relacionados
        items_carrito = CarritoItem.query.filter_by(producto_id=producto_id).all()
        for item in items_carrito:
            db.session.delete(item)

        # 2. Eliminar favoritos relacionados
        from app.models.favorito import Favorito
        favoritos = Favorito.query.filter_by(producto_id=producto_id).all()
        for favorito in favoritos:
            db.session.delete(favorito)

        # 3. Finalmente eliminar el producto
        db.session.delete(producto)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar producto'}), 500

# ----------------------------------------- API PEDIDOS ---------------------------------------- #

@web_bp.route('/api/pedidos/procesar', methods=['POST'])
@login_required
def api_procesar_pedido():
    """Procesa el pedido después del pago exitoso (VERSIÓN COMPLETA)"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json()
        print(f"DATOS RECIBIDOS: {data}")  # ← AGREGAR ESTE LOG PARA DEBUG
        
        metodo_pago = data.get('metodo_pago', 'paypal')
        order_id = data.get('order_id')  # ← AGREGAR ESTA LÍNEA
        detalles_paypal = data.get('detalles_paypal', {})
        direccion_envio = data.get('direccion_envio', '')
        
        # Si recibimos order_id, lo usamos como transacción
        id_transaccion = order_id if order_id else detalles_paypal.get('id', '')
        
        print(f" Procesando pedido para usuario {session['user_id']}")
        print(f" ID Transacción: {id_transaccion}")

        # El resto del código IGUAL...
        # Obtener el carrito activo del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito or not carrito.items:
            return jsonify({'success': False, 'error': 'Carrito vacío'}), 400

        # Verificar stock y calcular total
        total_pedido = 0
        items_pedido = []
        
        for item in carrito.items:
            producto = Producto.query.get(item.producto_id)
            
            if not producto or not producto.activo:
                return jsonify({
                    'success': False, 
                    'error': f'El producto {producto.nombre if producto else "desconocido"} no está disponible'
                }), 400
            
            if producto.stock < item.cantidad:
                return jsonify({
                    'success': False, 
                    'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {item.cantidad}'
                }), 400
            
            item_total = float(item.precio_unitario) * item.cantidad
            total_pedido += item_total
            items_pedido.append({
                'producto': producto,
                'item_carrito': item,
                'cantidad': item.cantidad,
                'precio': float(item.precio_unitario),
                'total': item_total
            })

        # Calcular fecha de entrega
        from datetime import datetime, timedelta
        
        fecha_actual = datetime.utcnow()
        
        dias_habiles = 0
        fecha_temp = fecha_actual
        
        while dias_habiles < 20:
            fecha_temp += timedelta(days=1)
            if fecha_temp.weekday() < 5:
                dias_habiles += 1
        
        fecha_entrega = fecha_temp

        # Crear pedido (usando id_transaccion)
        nuevo_pedido = Pedido(
            usuario_id=session['user_id'],
            total=total_pedido,
            estado='completado',
            estado_seguimiento='procesando',
            fecha_pedido=fecha_actual,
            fecha_entrega_estimada=fecha_entrega,
            metodo_pago=metodo_pago,
            id_transaccion_paypal=id_transaccion,  # ← AHORA USA id_transaccion
            direccion_envio=direccion_envio,
            puede_cancelar=True
        )
        
        db.session.add(nuevo_pedido)
        db.session.flush()

        # Crear items del pedido y actualizar stock
        for item_data in items_pedido:
            producto = item_data['producto']
            item_carrito = item_data['item_carrito']
            
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id_pedido,
                producto_id=producto.id_producto,
                cantidad=item_carrito.cantidad,
                precio_unitario=item_carrito.precio_unitario
            )
            db.session.add(pedido_item)
            
            producto.stock -= item_carrito.cantidad
            
            if producto.stock == 0:
                producto.activo = False
                print(f"Producto deshabilitado por stock 0: {producto.nombre}")

        # Limpiar el carrito
        for item in carrito.items:
            db.session.delete(item)
        
        carrito.activo = False

        db.session.commit()

        print(f"Pedido {nuevo_pedido.id_pedido} procesado exitosamente. Total: ${total_pedido}")
        print(f"Fecha de entrega estimada: {fecha_entrega.strftime('%d/%m/%Y')}")

        return jsonify({
            'success': True,
            'message': 'Compra procesada correctamente',
            'pedido_id': nuevo_pedido.id_pedido,
            'total': float(total_pedido),
            'transaccion_id': nuevo_pedido.id_transaccion_paypal,
            'fecha_entrega_estimada': fecha_entrega.strftime('%Y-%m-%d'),
            'estado_seguimiento': 'procesando'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error procesando pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al procesar la compra'}), 500
    
    
@web_bp.route('/api/pedidos/crear-manual', methods=['POST'])
@login_required
@admin_required
def api_crear_pedido_manual():
    """Crear un pedido manualmente desde el panel de admin"""
    try:
        data = request.get_json()
        
        usuario_id = data.get('usuario_id')
        items = data.get('items', [])
        total = data.get('total', 0)
        metodo_pago = data.get('metodo_pago', 'manual')
        
        if not usuario_id or not items:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        # Verificar stock
        for item in items:
            producto = Producto.query.get(item['producto_id'])
            if not producto or not producto.activo:
                return jsonify({'success': False, 'error': f'Producto {item["producto_id"]} no disponible'}), 400
            if producto.stock < item['cantidad']:
                return jsonify({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'}), 400
        
        # Calcular fecha de entrega
        from datetime import datetime, timedelta
        fecha_actual = datetime.utcnow()
        
        dias_habiles = 0
        fecha_temp = fecha_actual
        while dias_habiles < 20:
            fecha_temp += timedelta(days=1)
            if fecha_temp.weekday() < 5:
                dias_habiles += 1
        
        fecha_entrega = fecha_temp
        
        # Crear pedido
        nuevo_pedido = Pedido(
            usuario_id=usuario_id,
            total=total,
            estado='pendiente',
            estado_seguimiento='procesando',
            fecha_pedido=fecha_actual,
            fecha_entrega_estimada=fecha_entrega,
            metodo_pago=metodo_pago,
            direccion_envio='',
            puede_cancelar=True
        )
        
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # Crear items y actualizar stock
        for item in items:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id_pedido,
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            db.session.add(pedido_item)
            
            producto = Producto.query.get(item['producto_id'])
            producto.stock -= item['cantidad']
            if producto.stock == 0:
                producto.activo = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'pedido_id': nuevo_pedido.id_pedido
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando pedido manual: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al crear pedido'}), 500
        
# ----------------------------------------- API PEDIDOS USUARIO ---------------------------------------- #
@web_bp.route('/api/pedidos/mis-pedidos', methods=['GET'])
@login_required
def api_mis_pedidos():
    """Obtiene todos los pedidos del usuario autenticado"""
    try:
        usuario_id = session['user_id']
        print(f"🔍 Obteniendo pedidos para usuario ID: {usuario_id}")
        
        # Obtener información del usuario
        usuario = Usuario.query.get(usuario_id)
        print(f"👤 Usuario: {usuario.nombre_usuario} (ID: {usuario_id})")
        
        # Obtener TODOS los pedidos del usuario ordenados por fecha (para contar)
        todos_pedidos_usuario = Pedido.query.filter_by(usuario_id=usuario_id)\
            .order_by(Pedido.fecha_pedido.asc())\
            .all()
        
        # Crear un diccionario que mapea ID real → número secuencial
        # El más antiguo (primero en la lista) será #1
        mapeo_ids = {}
        for idx, pedido in enumerate(todos_pedidos_usuario, 1):
            mapeo_ids[pedido.id_pedido] = idx
            print(f"📌 Mapeo: Pedido ID={pedido.id_pedido} → #{idx} (fecha: {pedido.fecha_pedido})")
        
        print(f"📦 Total de pedidos del usuario: {len(todos_pedidos_usuario)}")
        
        # ✅ Ahora obtenerlos ordenados del más reciente al más antiguo para la vista
        pedidos_ordenados = Pedido.query.filter_by(usuario_id=usuario_id)\
            .order_by(Pedido.fecha_pedido.desc())\
            .all()
        
        from datetime import datetime
        import pytz
        ahora = datetime.utcnow()
        
        # Zona horaria de México
        zona_mexico = pytz.timezone('America/Mexico_City')
        
        pedidos_json = []
        for pedido in pedidos_ordenados:
            try:
                # Obtener el número secuencial del mapeo
                numero_secuencial = mapeo_ids.get(pedido.id_pedido, 0)
                
                # Actualizar estado de seguimiento automáticamente
                if pedido.estado_seguimiento not in ['cancelado', 'entregado']:
                    if pedido.fecha_entrega_estimada and ahora >= pedido.fecha_entrega_estimada:
                        pedido.estado_seguimiento = 'entregado'
                        pedido.fecha_entrega_real = ahora
                        pedido.puede_cancelar = False
                    elif (ahora - pedido.fecha_pedido).days >= 7:
                        pedido.estado_seguimiento = 'enviado'
                    
                    pedido.puede_cancelar = (ahora - pedido.fecha_pedido).total_seconds() < 86400
                
                # ✅ CONVERTIR FECHA UTC A HORA DE MÉXICO USANDO PYTZ
                if pedido.fecha_pedido:
                    # Asegurar que la fecha tenga zona horaria UTC
                    fecha_utc = pedido.fecha_pedido
                    if fecha_utc.tzinfo is None:
                        fecha_utc = pytz.UTC.localize(fecha_utc)
                    
                    # Convertir a zona horaria de México
                    fecha_mexico = fecha_utc.astimezone(zona_mexico)
                    fecha_pedido_str = fecha_mexico.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    fecha_pedido_str = None
                
                # ✅ CONVERTIR FECHA ENTREGA ESTIMADA (solo fecha, sin hora)
                if pedido.fecha_entrega_estimada:
                    fecha_entrega_utc = pedido.fecha_entrega_estimada
                    if fecha_entrega_utc.tzinfo is None:
                        fecha_entrega_utc = pytz.UTC.localize(fecha_entrega_utc)
                    fecha_entrega_mexico = fecha_entrega_utc.astimezone(zona_mexico)
                    fecha_entrega_str = fecha_entrega_mexico.strftime('%Y-%m-%d')
                else:
                    fecha_entrega_str = None
                
                # ✅ CONVERTIR FECHA ENTREGA REAL (solo fecha, sin hora)
                if pedido.fecha_entrega_real:
                    fecha_real_utc = pedido.fecha_entrega_real
                    if fecha_real_utc.tzinfo is None:
                        fecha_real_utc = pytz.UTC.localize(fecha_real_utc)
                    fecha_real_mexico = fecha_real_utc.astimezone(zona_mexico)
                    fecha_real_str = fecha_real_mexico.strftime('%Y-%m-%d')
                else:
                    fecha_real_str = None
                
                # ✅ Usamos el número secuencial del mapeo
                pedido_json = {
                    'id_pedido': pedido.id_pedido,
                    'numero_pedido': f"#{numero_secuencial}",
                    'fecha_pedido': fecha_pedido_str,
                    'fecha_entrega_estimada': fecha_entrega_str,
                    'fecha_entrega_real': fecha_real_str,
                    'total': float(pedido.total),
                    'estado_pago': pedido.estado,
                    'estado_seguimiento': pedido.estado_seguimiento,
                    'puede_cancelar': pedido.puede_cancelar,
                    'items': []
                }
                
                # Agregar items
                for item in pedido.items:
                    try:
                        producto = Producto.query.get(item.producto_id)
                        
                        nombre_producto = 'Producto no disponible'
                        imagen_producto = '/static/img/default-product.png'
                        
                        if producto:
                            nombre_producto = producto.nombre or 'Producto sin nombre'
                            if hasattr(producto, 'imagen') and producto.imagen:
                                imagen_producto = producto.imagen
                        
                        pedido_json['items'].append({
                            'producto_id': item.producto_id,
                            'nombre': nombre_producto,
                            'imagen': imagen_producto,
                            'cantidad': item.cantidad,
                            'precio_unitario': float(item.precio_unitario) if item.precio_unitario else 0,
                            'subtotal': float(item.cantidad * item.precio_unitario) if item.precio_unitario else 0
                        })
                    except Exception as item_error:
                        print(f"⚠️ Error procesando item {item.id_item}: {item_error}")
                        pedido_json['items'].append({
                            'producto_id': item.producto_id,
                            'nombre': 'Error al cargar producto',
                            'imagen': '/static/img/default-product.png',
                            'cantidad': item.cantidad,
                            'precio_unitario': 0,
                            'subtotal': 0
                        })
                
                pedidos_json.append(pedido_json)
                
            except Exception as pedido_error:
                print(f"⚠️ Error procesando pedido {pedido.id_pedido}: {pedido_error}")
                continue
        
        # Guardar cambios de estado
        try:
            db.session.commit()
        except Exception as commit_error:
            print(f"⚠️ Error en commit: {commit_error}")
            db.session.rollback()
        
        print(f"✅ Pedidos procesados correctamente: {len(pedidos_json)}")
        
        return jsonify({
            'success': True,
            'pedidos': pedidos_json,
            'count': len(pedidos_json)
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo pedidos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error al obtener pedidos: {str(e)}'}), 500
@web_bp.route('/api/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
@login_required
def api_cancelar_pedido(pedido_id):
    """Cancela un pedido si es posible"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        # Verificar que el pedido pertenezca al usuario
        if pedido.usuario_id != session['user_id']:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
        
        from datetime import datetime
        ahora = datetime.utcnow()
        horas_desde_compra = (ahora - pedido.fecha_pedido).total_seconds() / 3600
        
        # Verificar si puede cancelar (menos de 24 horas)
        if horas_desde_compra >= 24:
            return jsonify({
                'success': False, 
                'error': 'Ya no puedes cancelar este pedido (han pasado más de 24 horas)'
            }), 400
        
        if pedido.estado_seguimiento in ['entregado', 'cancelado']:
            return jsonify({
                'success': False, 
                'error': f'El pedido ya está {pedido.estado_seguimiento}'
            }), 400
        
        # Cancelar pedido
        pedido.estado_seguimiento = 'cancelado'
        pedido.puede_cancelar = False
        
        # Restaurar stock
        for item in pedido.items:
            producto = Producto.query.get(item.producto_id)
            if producto:
                producto.stock += item.cantidad
                # Reactivar si estaba deshabilitado por stock 0
                if producto.stock > 0 and not producto.activo:
                    producto.activo = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido cancelado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelando pedido: {e}")
        return jsonify({'success': False, 'error': 'Error al cancelar pedido'}), 500

# ----------------------------------------- API USUARIOS ADMIN ---------------------------------------- #

@web_bp.route('/api/admin/usuarios')
@admin_required
def api_admin_usuarios():
    """Obtener todos los usuarios para administración"""
    try:
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        rol_id = request.args.get('rol', '')
        estado = request.args.get('estado', '')

        # Consulta base
        query = Usuario.query.join(Role)

        # Aplicar filtros
        if search:
            query = query.filter(
                (Usuario.nombre_usuario.ilike(f'%{search}%')) |
                (Usuario.correo.ilike(f'%{search}%'))
            )
        
        if rol_id:
            query = query.filter(Usuario.rol_id == rol_id)
        
        if estado:
            if estado == 'activo':
                query = query.filter(Usuario.activo == True)
            elif estado == 'inactivo':
                query = query.filter(Usuario.activo == False)

        usuarios = query.order_by(Usuario.fecha_registro.desc()).all()

        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'rol': usuario.rol.nombre if usuario.rol else 'Sin rol',
                'rol_id': usuario.rol_id,
                'activo': usuario.activo,
                'fecha_registro': usuario.fecha_registro.isoformat() if usuario.fecha_registro else None,
                'ultimo_login': usuario.ultimo_acceso.isoformat() if usuario.ultimo_acceso else None
            })

        return jsonify({
            'success': True,
            'usuarios': usuarios_data,
            'total': len(usuarios_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo usuarios admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener usuarios'}), 500

@web_bp.route('/api/admin/usuarios/editar', methods=['PUT'])
@admin_required
def api_admin_editar_usuario():
    """Editar usuario desde administración"""
    try:
        data = request.get_json()
        usuario_id = data.get('id')
        
        if not usuario_id:
            return jsonify({'success': False, 'error': 'ID de usuario requerido'}), 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        # Verificar que no se modifique a sí mismo
        if usuario.id_usuario == session['user_id']:
            return jsonify({'success': False, 'error': 'No puedes modificar tu propio usuario desde aquí'}), 400

        # Actualizar campos
        if 'username' in data:
            # Verificar si el username ya existe (excluyendo el usuario actual)
            existing_user = Usuario.query.filter(
                Usuario.nombre_usuario == data['username'],
                Usuario.id_usuario != usuario_id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Este nombre de usuario ya está en uso'}), 400
            usuario.nombre_usuario = data['username']

        if 'email' in data:
            # Verificar si el email ya existe (excluyendo el usuario actual)
            existing_email = Usuario.query.filter(
                Usuario.correo == data['email'],
                Usuario.id_usuario != usuario_id
            ).first()
            if existing_email:
                return jsonify({'success': False, 'error': 'Este email ya está en uso'}), 400
            usuario.correo = data['email']

        if 'rol_id' in data:
            usuario.rol_id = data['rol_id']

        if 'activo' in data:
            usuario.activo = data['activo']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error editando usuario: {e}")
        return jsonify({'success': False, 'error': 'Error al editar usuario'}), 500

@web_bp.route('/api/admin/usuarios/agregar', methods=['POST'])
@admin_required
def api_admin_agregar_usuario():
    """Agregar nuevo usuario desde administración"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol_id = data.get('rol_id', 2)  # Por defecto cliente
        activo = data.get('activo', True)

        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'success': False, 'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'success': False, 'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'success': False, 'error': 'Este email ya está registrado'}), 400

        # Crear usuario
        nuevo_usuario = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=rol_id,
            activo=activo
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        print(f"USUARIO ADMIN CREADO: {username}, Email: {email}, Rol: {rol_id}")
        
        return jsonify({
            'success': True, 
            'message': 'Usuario creado exitosamente',
            'usuario_id': nuevo_usuario.id_usuario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando usuario admin: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/admin/usuarios/eliminar/<int:usuario_id>', methods=['DELETE'])
@admin_required
def api_admin_eliminar_usuario(usuario_id):
    """Eliminar usuario desde administración"""
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        # Verificar que no se elimine a sí mismo
        if usuario.id_usuario == session['user_id']:
            return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 400

        db.session.delete(usuario)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuario eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando usuario: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar usuario'}), 500

@web_bp.route('/api/admin/roles')
@admin_required
def api_admin_roles():
    """Obtener todos los roles"""
    try:
        roles = Role.query.all()
        
        roles_data = [{
            'id_rol': rol.id_rol,
            'nombre': rol.nombre,
        } for rol in roles]

        return jsonify({
            'success': True,
            'roles': roles_data
        })
        
    except Exception as e:
        print(f"Error obteniendo roles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener roles'}), 500

# ----------------------------------------- API PEDIDOS ADMIN (CORREGIDA) ---------------------------------------- #

@web_bp.route('/api/admin/pedidos')
@admin_required
def api_admin_pedidos():
    """Obtener todos los pedidos para administración"""
    try:
        from app.models.pedido import Pedido, PedidoItem
        from app.models.usuario import Usuario
        from app.models.models import Producto
        
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        estado_pago = request.args.get('estado_pago', '')  # ✅ Cambiar nombre
        estado_seguimiento = request.args.get('estado_seguimiento', '')  # ✅ NUEVO filtro
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # Consulta base
        query = Pedido.query.join(Usuario).outerjoin(PedidoItem).outerjoin(Producto)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                (Usuario.nombre_usuario.ilike(f'%{search}%')) |
                (Usuario.correo.ilike(f'%{search}%')) |
                (Producto.nombre.ilike(f'%{search}%')) |
                (Pedido.id_pedido.cast(db.String).ilike(f'%{search}%'))
            )
        
        if estado_pago:
            query = query.filter(Pedido.estado == estado_pago)
        
        if estado_seguimiento:  # ✅ NUEVO filtro
            query = query.filter(Pedido.estado_seguimiento == estado_seguimiento)
        
        if fecha_inicio:
            query = query.filter(Pedido.fecha_pedido >= fecha_inicio)
        
        if fecha_fin:
            query = query.filter(Pedido.fecha_pedido <= fecha_fin)
        
        # Eliminar duplicados por los joins
        query = query.distinct()
        
        # Ordenar por fecha más reciente primero
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()
        
        # Procesar datos para el frontend
        pedidos_data = []
        for pedido in pedidos:
            # Obtener todos los items del pedido
            items_data = []
            for item in pedido.items:
                items_data.append({
                    'producto_id': item.producto_id,
                    'producto_nombre': item.producto.nombre if item.producto else 'Producto no disponible',
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario) if item.precio_unitario else 0,
                    'total_item': float(item.precio_unitario * item.cantidad) if item.precio_unitario else 0
                })
            
            pedidos_data.append({
                'id_pedido': pedido.id_pedido,
                'numero_pedido': f"#ORD-{pedido.id_pedido:03d}",
                'cliente_nombre': pedido.usuario.nombre_usuario if pedido.usuario else 'Cliente no disponible',
                'cliente_email': pedido.usuario.correo if pedido.usuario else '',
                'productos': items_data,
                'cantidad_total': sum(item.cantidad for item in pedido.items),
                'total_pedido': float(pedido.total) if pedido.total else 0,
                'estado_pago': pedido.estado,  # ✅ Más claro
                'estado_seguimiento': pedido.estado_seguimiento,  # ✅ NUEVO campo
                'puede_cancelar': pedido.puede_cancelar,  # ✅ NUEVO campo
                'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M') if pedido.fecha_pedido else '',
                'fecha_entrega_estimada': pedido.fecha_entrega_estimada.strftime('%Y-%m-%d') if pedido.fecha_entrega_estimada else '',  # ✅ NUEVO
                'fecha_entrega_real': pedido.fecha_entrega_real.strftime('%Y-%m-%d') if pedido.fecha_entrega_real else '',  # ✅ NUEVO
                'fecha_iso': pedido.fecha_pedido.isoformat() if pedido.fecha_pedido else '',
                'direccion_envio': pedido.direccion_envio or 'No especificada',
                'metodo_pago': pedido.metodo_pago,  # ✅
                'id_transaccion': pedido.id_transaccion_paypal  # ✅
            })
        
        return jsonify({
            'success': True,
            'pedidos': pedidos_data,
            'total': len(pedidos_data),
            'filtros_aplicados': {
                'search': search,
                'estado_pago': estado_pago,
                'estado_seguimiento': estado_seguimiento,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        })
        
    except Exception as e:
        print(f"Error obteniendo pedidos admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener pedidos'}), 500

@web_bp.route('/api/admin/pedidos/estado', methods=['PUT'])
@admin_required
def api_admin_cambiar_estado_pedido():
    """Cambiar estado de un pedido (ahora maneja ambos estados)"""
    try:
        from app.models.pedido import Pedido
        
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        tipo_estado = data.get('tipo_estado', 'pago')  # 'pago' o 'seguimiento'
        nuevo_estado = data.get('estado')
        
        if not pedido_id or not nuevo_estado:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Validar según tipo
        if tipo_estado == 'pago':
            estados_validos = ['pendiente', 'procesando', 'completado', 'cancelado', 'fallido']
            if nuevo_estado not in estados_validos:
                return jsonify({'success': False, 'error': 'Estado de pago no válido'}), 400
            pedido.estado = nuevo_estado
            
        elif tipo_estado == 'seguimiento':
            estados_validos = ['procesando', 'enviado', 'entregado', 'cancelado']
            if nuevo_estado not in estados_validos:
                return jsonify({'success': False, 'error': 'Estado de seguimiento no válido'}), 400
            pedido.estado_seguimiento = nuevo_estado
            
            # Si se marca como entregado, registrar fecha
            if nuevo_estado == 'entregado' and not pedido.fecha_entrega_real:
                pedido.fecha_entrega_real = datetime.utcnow()
                pedido.puede_cancelar = False
            
            # Si se cancela, restaurar stock
            if nuevo_estado == 'cancelado':
                for item in pedido.items:
                    producto = Producto.query.get(item.producto_id)
                    if producto:
                        producto.stock += item.cantidad
                pedido.puede_cancelar = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Estado actualizado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando estado de pedido: {e}")
        return jsonify({'success': False, 'error': 'Error al cambiar estado'}), 500

@web_bp.route('/api/admin/pedidos/<int:pedido_id>')
@admin_required
def api_admin_detalle_pedido(pedido_id):
    """Obtener detalle completo de un pedido (versión mejorada)"""
    try:
        from app.models.pedido import Pedido, PedidoItem
        from app.models.usuario import Usuario
        from app.models.models import Producto
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Datos del pedido con todos los campos
        pedido_data = {
            'id_pedido': pedido.id_pedido,
            'numero_pedido': f"#ORD-{pedido.id_pedido:03d}",
            'cliente': {
                'id': pedido.usuario.id_usuario,
                'nombre': pedido.usuario.nombre_usuario,
                'email': pedido.usuario.correo,
                'telefono': pedido.usuario.telefono if hasattr(pedido.usuario, 'telefono') else ''
            } if pedido.usuario else None,
            'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M') if pedido.fecha_pedido else '',
            'fecha_entrega_estimada': pedido.fecha_entrega_estimada.strftime('%Y-%m-%d') if pedido.fecha_entrega_estimada else '',
            'fecha_entrega_real': pedido.fecha_entrega_real.strftime('%Y-%m-%d') if pedido.fecha_entrega_real else '',
            'total': float(pedido.total) if pedido.total else 0,
            'estado_pago': pedido.estado,
            'estado_seguimiento': pedido.estado_seguimiento,
            'puede_cancelar': pedido.puede_cancelar,
            'direccion_envio': pedido.direccion_envio or 'No especificada',
            'metodo_pago': pedido.metodo_pago,
            'id_transaccion': pedido.id_transaccion_paypal
        }
        
        # Items del pedido
        items_data = []
        for item in pedido.items:
            items_data.append({
                'producto_id': item.producto_id,
                'producto_nombre': item.producto.nombre if item.producto else 'Producto no disponible',
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario) if item.precio_unitario else 0,
                'total': float(item.precio_unitario * item.cantidad) if item.precio_unitario else 0,
                'imagen': item.producto.imagen if item.producto and hasattr(item.producto, 'imagen') else '/static/img/default-product.png'
            })
        
        pedido_data['items'] = items_data
        
        return jsonify({
            'success': True,
            'pedido': pedido_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener detalle'}), 500

# ✅ NUEVA ruta para estadísticas de pedidos (útil para dashboard)
@web_bp.route('/api/admin/pedidos/estadisticas')
@admin_required
def api_admin_estadisticas_pedidos():
    """Obtener estadísticas de pedidos para el dashboard"""
    try:
        from datetime import datetime, timedelta
        
        # Totales por estado de seguimiento
        procesando = Pedido.query.filter_by(estado_seguimiento='procesando').count()
        enviado = Pedido.query.filter_by(estado_seguimiento='enviado').count()
        entregado = Pedido.query.filter_by(estado_seguimiento='entregado').count()
        cancelado = Pedido.query.filter_by(estado_seguimiento='cancelado').count()
        
        # Totales por estado de pago
        pagado = Pedido.query.filter_by(estado='completado').count()
        pendiente = Pedido.query.filter_by(estado='pendiente').count()
        
        # Pedidos de hoy
        hoy = datetime.now().date()
        pedidos_hoy = Pedido.query.filter(
            db.func.date(Pedido.fecha_pedido) == hoy
        ).count()
        
        # Ingresos totales
        ingresos_totales = db.session.query(db.func.sum(Pedido.total)).filter(
            Pedido.estado == 'completado'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'seguimiento': {
                    'procesando': procesando,
                    'enviado': enviado,
                    'entregado': entregado,
                    'cancelado': cancelado
                },
                'pago': {
                    'completado': pagado,
                    'pendiente': pendiente
                },
                'pedidos_hoy': pedidos_hoy,
                'ingresos_totales': float(ingresos_totales)
            }
        })
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener estadísticas'}), 500

# ----------------------------------------- UTILIDADES ---------------------------------------- #

def deshabilitar_productos_sin_stock():
    """Deshabilita automáticamente productos cuando el stock llega a 0"""
    try:
        productos_sin_stock = Producto.query.filter(
            Producto.stock == 0,
            Producto.activo == True
        ).all()
        
        for producto in productos_sin_stock:
            producto.activo = False
            print(f"Producto deshabilitado por stock 0: {producto.nombre}")
        
        if productos_sin_stock:
            db.session.commit()
            print(f"Se deshabilitaron {len(productos_sin_stock)} productos sin stock")
            
        return len(productos_sin_stock)
        
    except Exception as e:
        print(f"Error deshabilitando productos sin stock: {e}")
        db.session.rollback()
        return 0

@web_bp.route('/api/admin/limpiar-stock-cero', methods=['POST'])
@admin_required
def api_limpiar_stock_cero():
    """Endpoint para que el admin pueda limpiar manualmente productos sin stock"""
    try:
        cantidad_deshabilitados = deshabilitar_productos_sin_stock()
        
        return jsonify({
            'success': True,
            'message': f'Se deshabilitaron {cantidad_deshabilitados} productos sin stock'
        })
        
    except Exception as e:
        print(f"Error en limpieza de stock: {e}")
        return jsonify({'success': False, 'error': 'Error en limpieza de stock'}), 500

@web_bp.route('/api/admin/productos/validar')
@admin_required
def api_validar_producto():
    """Validar si ya existe un producto con el mismo nombre en la misma categoría"""
    try:
        nombre = request.args.get('nombre', '').strip()
        categoria_id = request.args.get('categoria_id', '')
        excluir_id = request.args.get('excluir_id', '')

        if not nombre or not categoria_id:
            return jsonify({'existe': False})

        # Construir consulta
        query = Producto.query.filter(
            Producto.nombre.ilike(nombre),
            Producto.categoria_id == categoria_id
        )

        # Excluir producto actual en caso de edición
        if excluir_id:
            query = query.filter(Producto.id_producto != excluir_id)

        # Verificar si existe
        producto_existente = query.first()
        existe = producto_existente is not None

        return jsonify({'existe': existe})

    except Exception as e:
        print(f"Error validando producto: {e}")
        return jsonify({'existe': False, 'error': 'Error en validación'}), 500


@web_bp.route('/api/paypal/config')
def api_paypal_config():
    """Endpoint seguro para obtener configuración de PayPal"""
    try:
        # Obtener del archivo de configuración (.env)
        client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        mode = current_app.config.get('PAYPAL_MODE', 'sandbox')
        
        if not client_id:
            return jsonify({
                'success': False, 
                'error': 'Configuración de PayPal no encontrada'
            }), 500
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'mode': mode
        })
        
    except Exception as e:
        print(f"Error en api_paypal_config: {e}")
        return jsonify({
            'success': False, 
            'error': 'Error interno del servidor'
        }), 500
        
@web_bp.route('/api/verify-user-status')
def verify_user_status():
    """Verificar si el usuario actual sigue activo en el sistema"""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        
        # Verificar si el usuario existe y está activo
        if not usuario or not usuario.activo:
            # Usuario fue desactivado o eliminado
            session.clear()
            return jsonify({
                'valid': False,
                'message': 'Tu cuenta ha sido desactivada',
                'redirect': '/login?desactivada=true'
            }), 401
            
        return jsonify({
            'valid': True,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'role': usuario.rol_id,
                'activo': usuario.activo
            }
        })
    
    return jsonify({'valid': False}), 401

# ----------------------------------------- ESTADÍSTICAS PARA DASHBOARD ---------------------------------------- #

@web_bp.route('/api/admin/estadisticas/productos-mas-vendidos')
@admin_required
def api_productos_mas_vendidos():
    """Obtiene los productos más vendidos para la gráfica del dashboard"""
    try:
        # Obtener parámetros
        limite = request.args.get('limite', 10, type=int)
        meses = request.args.get('meses', 6, type=int)  # Últimos N meses
        
        from datetime import datetime, timedelta
        
        # Calcular fecha de inicio (hace N meses)
        fecha_inicio = datetime.utcnow() - timedelta(days=30*meses)
        
        # Consulta para obtener productos más vendidos
        resultados = db.session.query(
            Producto.id_producto,
            Producto.nombre,
            Producto.imagen,
            db.func.sum(PedidoItem.cantidad).label('total_vendido'),
            db.func.sum(PedidoItem.cantidad * PedidoItem.precio_unitario).label('total_ingresos')
        ).join(
            PedidoItem, PedidoItem.producto_id == Producto.id_producto
        ).join(
            Pedido, Pedido.id_pedido == PedidoItem.pedido_id
        ).filter(
            Pedido.fecha_pedido >= fecha_inicio,
            Pedido.estado.in_(['completado', 'pendiente'])  # Solo pedidos confirmados
        ).group_by(
            Producto.id_producto, Producto.nombre, Producto.imagen
        ).order_by(
            db.desc('total_vendido')
        ).limit(limite).all()
        
        productos_data = []
        for prod in resultados:
            productos_data.append({
                'id': prod.id_producto,
                'nombre': prod.nombre,
                'imagen': prod.imagen or '/static/img/default-product.png',
                'total_vendido': int(prod.total_vendido),
                'total_ingresos': float(prod.total_ingresos)
            })
        
        # Obtener total de ingresos general para porcentajes
        total_ingresos_general = db.session.query(
            db.func.sum(PedidoItem.cantidad * PedidoItem.precio_unitario)
        ).join(
            Pedido, Pedido.id_pedido == PedidoItem.pedido_id
        ).filter(
            Pedido.fecha_pedido >= fecha_inicio,
            Pedido.estado.in_(['completado', 'pendiente'])
        ).scalar() or 1  # Evitar división por cero
        
        return jsonify({
            'success': True,
            'productos': productos_data,
            'total_ingresos': float(total_ingresos_general),
            'periodo': {
                'desde': fecha_inicio.strftime('%Y-%m-%d'),
                'hasta': datetime.utcnow().strftime('%Y-%m-%d'),
                'meses': meses
            }
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo productos más vendidos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@web_bp.route('/api/admin/estadisticas/ventas-por-mes')
@admin_required
def api_ventas_por_mes():
    """Obtiene las ventas por mes para la gráfica de tendencia"""
    try:
        from datetime import datetime, timedelta
        import calendar
        
        # Últimos 12 meses
        meses = []
        labels = []
        datos_ventas = []
        
        fecha_actual = datetime.utcnow()
        
        for i in range(11, -1, -1):
            fecha = fecha_actual - timedelta(days=30*i)
            mes = fecha.month
            año = fecha.year
            
            # Primer día del mes
            inicio_mes = datetime(año, mes, 1)
            # Último día del mes
            if mes == 12:
                fin_mes = datetime(año + 1, 1, 1) - timedelta(days=1)
            else:
                fin_mes = datetime(año, mes + 1, 1) - timedelta(days=1)
            
            # Total de ventas en el mes
            total = db.session.query(
                db.func.sum(Pedido.total)
            ).filter(
                Pedido.fecha_pedido >= inicio_mes,
                Pedido.fecha_pedido <= fin_mes,
                Pedido.estado.in_(['completado', 'pendiente'])
            ).scalar() or 0
            
            meses.append({
                'año': año,
                'mes': mes,
                'nombre': calendar.month_name[mes][:3]  # Abreviatura
            })
            labels.append(f"{calendar.month_name[mes][:3]} {año}")
            datos_ventas.append(float(total))
        
        return jsonify({
            'success': True,
            'labels': labels,
            'datos': datos_ventas,
            'meses': meses
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo ventas por mes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@web_bp.route('/api/admin/estadisticas/resumen')
@admin_required
def api_resumen_estadisticas():
    """Obtiene un resumen de estadísticas para el dashboard"""
    try:
        from datetime import datetime, timedelta
        
        ahora = datetime.utcnow()
        inicio_mes = datetime(ahora.year, ahora.month, 1)
        inicio_semana = ahora - timedelta(days=7)
        inicio_ano = datetime(ahora.year, 1, 1)
        
        # Totales generales
        total_productos = Producto.query.count()
        total_usuarios = Usuario.query.filter_by(rol_id=2).count()  # Solo clientes
        total_pedidos = Pedido.query.count()
        
        # Pedidos por estado
        pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()
        pedidos_completados = Pedido.query.filter_by(estado='completado').count()
        pedidos_cancelados = Pedido.query.filter_by(estado='cancelado').count()
        
        # Ventas del mes
        ventas_mes = db.session.query(
            db.func.sum(Pedido.total)
        ).filter(
            Pedido.fecha_pedido >= inicio_mes,
            Pedido.estado.in_(['completado', 'pendiente'])
        ).scalar() or 0
        
        # Ventas de la semana
        ventas_semana = db.session.query(
            db.func.sum(Pedido.total)
        ).filter(
            Pedido.fecha_pedido >= inicio_semana,
            Pedido.estado.in_(['completado', 'pendiente'])
        ).scalar() or 0
        
        # Ventas del año
        ventas_ano = db.session.query(
            db.func.sum(Pedido.total)
        ).filter(
            Pedido.fecha_pedido >= inicio_ano,
            Pedido.estado.in_(['completado', 'pendiente'])
        ).scalar() or 0
        
        # Productos con stock bajo
        stock_bajo = Producto.query.filter(
            Producto.stock < 10,
            Producto.activo == True
        ).count()
        
        return jsonify({
            'success': True,
            'resumen': {
                'total_productos': total_productos,
                'total_usuarios': total_usuarios,
                'total_pedidos': total_pedidos,
                'pedidos_pendientes': pedidos_pendientes,
                'pedidos_completados': pedidos_completados,
                'pedidos_cancelados': pedidos_cancelados,
                'ventas_mes': float(ventas_mes),
                'ventas_semana': float(ventas_semana),
                'ventas_ano': float(ventas_ano),
                'stock_bajo': stock_bajo
            }
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo resumen: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500