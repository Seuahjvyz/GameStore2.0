from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app import db
from app.models.usuario import Usuario
from app.models.models import Carrito, CarritoItem, Producto, Categoria
from app.models.role import Role
from app.models.favorito import Favorito


web_bp = Blueprint('web', __name__)

# ----------------------------------------- DECORATORS ---------------------------------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🎯 login_required EJECUTÁNDOSE para: {request.path}")
        print(f"🔍 Session data: {dict(session)}")
        print(f"🔍 user_id en session: {'user_id' in session}")
        
        if 'user_id' not in session:
            print("❌ REDIRIGIENDO a login - usuario NO autenticado")
            return redirect(url_for('web.login'))
        
        print("✅ Acceso PERMITIDO - usuario autenticado")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web.login'))
        
        if session.get('user_role') != 1:  # 1 = Administrador
            return jsonify({'error': 'Acceso denegado. Se requieren privilegios de administrador'}), 403
        
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

@web_bp.route('/registro-admin')
def registro_admin():
    return render_template('admin_templates/RegistroAdmin.html')

# ----------------------------------------- RUTAS FALTANTES ---------------------------------------- #

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

@web_bp.route('/api/usuario/actual')
def api_usuario_actual():
    """Obtener información del usuario actual"""
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'id': usuario.id_usuario,
            'username': usuario.nombre_usuario,
            'email': usuario.correo,
            'role': usuario.rol_id
        })
    else:
        return jsonify({'error': 'No autenticado'}), 401

# ----------------------------------------- RUTAS DE DEBUG ---------------------------------------- #

@web_bp.route('/debug/database')
def debug_database():
    """Ruta para debuggear el estado de la base de datos"""
    try:
        categorias = Categoria.query.all()
        productos = Producto.query.all()
        usuarios = Usuario.query.all()
        roles = Role.query.all()
        
        debug_info = {
            'categorias_count': len(categorias),
            'categorias': [{'id': c.id_categoria, 'nombre': c.nombre} for c in categorias],
            'productos_count': len(productos),
            'productos': [{'id': p.id_producto, 'nombre': p.nombre, 'categoria_id': p.categoria_id} for p in productos],
            'usuarios_count': len(usuarios),
            'usuarios': [{'id': u.id_usuario, 'username': u.nombre_usuario, 'rol_id': u.rol_id} for u in usuarios],
            'roles_count': len(roles),
            'roles': [{'id': r.id_rol, 'nombre': r.nombre} for r in roles]
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/debug/session')
def debug_session():
    """Ruta para debuggear la sesión"""
    return jsonify({
        'session_data': dict(session),
        'user_id_in_session': 'user_id' in session,
        'user_role_in_session': 'user_role' in session
    })

# ----------------------------------------- API LOGIN (ÚNICO) ---------------------------------------- #

@web_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        login_input = data.get('login_input')
        password = data.get('password')
        
        if not login_input:
            return jsonify({'error': 'Ingresa tu usuario o email'}), 400
        
        if not password:
            return jsonify({'error': 'Ingresa tu contraseña'}), 400
        
        # Buscar usuario
        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == login_input) | (Usuario.correo == login_input)
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Crear sesión
        session.clear()
        session['user_id'] = usuario.id_usuario
        session['username'] = usuario.nombre_usuario
        session['user_role'] = usuario.rol_id
        
        print(f"LOGIN EXITOSO: {usuario.nombre_usuario} (Rol: {usuario.rol_id})")
        
        # Redirigir según rol
        if usuario.rol_id == 1:  # Administrador
            redirect_url = '/admin'
            message = 'Login de administrador exitoso'
        else:  # Usuario normal
            redirect_url = '/'
            message = 'Login exitoso'
        
        return jsonify({
            'success': True, 
            'message': message,
            'redirect_url': redirect_url,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            }
        }), 200
        
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ----------------------------------------- LOGOUT ---------------------------------------- #

@web_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

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

# ----------------------------------------- RUTAS DE PÁGINAS ---------------------------------------- #

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
    return render_template('favoritos.html')

@web_bp.route('/perfil')
@login_required
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfiluser.html', usuario=usuario)

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

@web_bp.route('/admin')
@admin_required
def admin():
    return render_template('admin_templates/admin.html')

@web_bp.route('/carrito')
@login_required
def carrito():
    return render_template('Carrito.html')

# ----------------------------------------- API PRODUCTOS ---------------------------------------- #

@web_bp.route('/api/productos')
def api_productos():
    try:
        # Obtener parámetro de categoría si existe
        categoria_nombre = request.args.get('categoria')
        
        if categoria_nombre:
            # Filtrar por nombre de categoría
            productos = Producto.query.join(Categoria).filter(
                Categoria.nombre == categoria_nombre,
                Producto.activo == True
            ).all()
            print(f" Filtrando por categoría: {categoria_nombre}, encontrados: {len(productos)} productos")
        else:
            # Todos los productos
            productos = Producto.query.filter_by(activo=True).all()
            print(f" Todos los productos, encontrados: {len(productos)} productos")
        
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
        productos = Producto.query.filter_by(
            categoria_id=categoria_id, 
            activo=True
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

        print(f"🛒 Carrito encontrado: {carrito.id_carrito if carrito else 'NONE'}")

        if not carrito:
            carrito = Carrito(usuario_id=session['user_id'])
            db.session.add(carrito)
            db.session.flush()
            print(f"🆕 Nuevo carrito creado: {carrito.id_carrito}")

        # ✅ VERIFICACIÓN MÁS ROBUSTA: Buscar item existente
        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id
        ).first()

        print(f"🔍 Item existente: {item_existente.id_item if item_existente else 'NONE'}")

        if item_existente:
            # Si ya existe, aumentar la cantidad
            nueva_cantidad = item_existente.cantidad + cantidad
            print(f"📈 Actualizando cantidad: {item_existente.cantidad} + {cantidad} = {nueva_cantidad}")
            
            # Verificar stock disponible
            if nueva_cantidad > producto.stock:
                return jsonify({'success': False, 'error': f'Stock insuficiente. Solo quedan {producto.stock} unidades'}), 400
            
            item_existente.cantidad = nueva_cantidad
            mensaje = f'Cantidad actualizada: ahora tienes {nueva_cantidad} unidades'
            accion = 'actualizado'
        else:
            # Si no existe, crear nuevo item
            print(f"🆕 Creando nuevo item para producto {producto_id}")
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
        print(f"✅ Commit exitoso - {accion}")
        
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
        print(f"❌ ERROR en agregar_al_carrito: {e}")
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
        
        for item in carrito.items:
            item_total = float(item.precio_unitario) * item.cantidad
            subtotal += item_total
            
            items_data.append({
                'id': item.id_item,
                'producto_id': item.producto.id_producto,
                'nombre': item.producto.nombre,
                'precio_unitario': float(item.precio_unitario),
                'cantidad': item.cantidad,
                'total': item_total,
                'imagen': item.producto.imagen,
                'stock': item.producto.stock
            })

        return jsonify({
            'success': True,
            'carrito': {
                'items': items_data,
                'subtotal': subtotal,
                'total': subtotal,
                'count': len(carrito.items)
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

# En la ruta /api/favoritos/agregar - CORREGIDA
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

# Ruta de debug para favoritos
@web_bp.route('/debug/favoritos')
@login_required
def debug_favoritos():
    """Ruta para debuggear favoritos"""
    try:
        usuario_id = session['user_id']
        
        # Contar favoritos del usuario
        count = Favorito.query.filter_by(usuario_id=usuario_id).count()
        
        # Obtener algunos favoritos de ejemplo
        favoritos = Favorito.query.filter_by(usuario_id=usuario_id).limit(5).all()
        
        favoritos_data = []
        for fav in favoritos:
            favoritos_data.append({
                'id_favorito': fav.id_favorito,
                'usuario_id': fav.usuario_id,
                'producto_id': fav.producto_id,
                'fecha_agregado': fav.fecha_agregado.isoformat() if fav.fecha_agregado else None
            })
        
        return jsonify({
            'usuario_actual': usuario_id,
            'total_favoritos': count,
            'favoritos_ejemplo': favoritos_data,
            'tabla_existe': True,
            'estructura': 'id_favorito, usuario_id, producto_id, fecha_agregado'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500




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