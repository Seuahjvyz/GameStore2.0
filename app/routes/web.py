from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app import db
from app.models.usuario import Usuario
from app.models.models import Carrito, CarritoItem, Producto, Categoria
from app.models.role import Role

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
            print(f"🔍 Filtrando por categoría: {categoria_nombre}, encontrados: {len(productos)} productos")
        else:
            # Todos los productos
            productos = Producto.query.filter_by(activo=True).all()
            print(f"🔍 Todos los productos, encontrados: {len(productos)} productos")
        
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
        print(f"❌ Error obteniendo productos: {e}")
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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Debes iniciar sesión para agregar productos al carrito'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)

        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        if producto.stock < cantidad:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            carrito = Carrito(usuario_id=session['user_id'])
            db.session.add(carrito)
            db.session.flush()

        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id
        ).first()

        if item_existente:
            nueva_cantidad = item_existente.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400
            item_existente.cantidad = nueva_cantidad
        else:
            nuevo_item = CarritoItem(
                carrito_id=carrito.id_carrito,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(nuevo_item)

        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Producto agregado al carrito',
            'carrito_count': len(carrito.items)
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error agregando al carrito: {e}")
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