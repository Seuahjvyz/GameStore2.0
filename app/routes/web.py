from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash
from app import db
from app.models.usuario import Usuario
from app.models.role import Role  
from werkzeug.security import check_password_hash
from flask import session



web_bp = Blueprint('web', __name__)

#-----------------------------------------PAGINA PRINCIPAL-----------------------------------------#


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

#-----------------------------------------PAGINA PRINCIPAL-----------------------------------------#


@web_bp.route('/')
def index():
    return render_template('index.html')


#-----------------------------------------LOGIN-----------------------------------------#

@web_bp.route('/login')
def login():
    return render_template('login.html')

@web_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        login_input = data.get('login_input')
        password = data.get('password')
        
        # Validaciones básicas
        if not login_input:
            return jsonify({'error': 'Ingresa tu usuario o email'}), 400
        
        if not password:
            return jsonify({'error': 'Ingresa tu contraseña'}), 400
        
        # Buscar usuario por nombre_usuario O correo
        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == login_input) | (Usuario.correo == login_input)
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Crear sesión (LOGIN EXITOSO)
        session['user_id'] = usuario.id_usuario
        session['username'] = usuario.nombre_usuario
        session['user_role'] = usuario.rol_id
        
        print(f"LOGIN EXITOSO: {usuario.nombre_usuario}")
        
        return jsonify({
            'success': True, 
            'message': 'Login exitoso',
            'redirect_url': '/',  
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo
            }
        }), 200
        
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    

#-----------------------------------------LOGOUT-----------------------------------------#


# Ruta para cerrar sesión
@web_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Ruta para verificar si hay usuario logueado
@web_bp.route('/api/user-info')
def user_info():
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo
            }
        })
    else:
        return jsonify({'logged_in': False})


    
#-----------------------------------------REGISTRO DE USUARIO-----------------------------------------#

@web_bp.route('/registro')
def registro():
    return render_template('registro.html')

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
        
        # Validaciones básicas
        if not username or len(username) < 6:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # VERIFICAR SI EL USUARIO YA EXISTE
        usuario_existente = Usuario.query.filter_by(nombre_usuario=username).first()
        if usuario_existente:
            return jsonify({'error': 'Este usuario ya existe'}), 400
            
        email_existente = Usuario.query.filter_by(correo=email).first()
        if email_existente:
            return jsonify({'error': 'Este email ya está registrado'}), 400
        
        # CREAR NUEVO USUARIO (ENCRIPTAR CONTRASEÑA)
        nuevo_usuario = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=2  # Cliente por defecto
        )
        
        # GUARDAR EN BD
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
    

#-----------------------------------------JUEGOS-----------------------------------------#
    

@web_bp.route('/juegos')
def juegos():
    return render_template('juegos.html')


#-----------------------------------------CONSOLAS-----------------------------------------#


@web_bp.route('/consolas')
def consolas():
    return render_template('consolas.html')



#-----------------------------------------CONTROLES-----------------------------------------#

@web_bp.route('/controles')
def controles():
    return render_template('controles.html')

#-----------------------------------------ACCESORIOS-----------------------------------------#


@web_bp.route('/accesorios')
def accesorios():  # ← Corregí el nombre de la función
    return render_template('accesorios.html')

#-----------------------------------------CARRITO-----------------------------------------#




#-----------------------------------------FAVORITOS-----------------------------------------#


@web_bp.route('/favoritos')
@login_required
def favoritos():
    return render_template('favoritos.html')


#-----------------------------------------PERFIL-----------------------------------------#


@web_bp.route('/perfil')
@login_required  # ← MISMA sangría que la función
def perfil():    # ← MISMA sangría que el decorador
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfiluser.html', usuario=usuario)

#-----------------------------------------PEDIDOS-----------------------------------------#


@web_bp.route('/pedidos')
@login_required
def pedidos():
    return render_template('pedidos.html')

#-----------------------------------------PAGAR-----------------------------------------#


@web_bp.route('/pagar')
@login_required
def pagar():
    return render_template('Pagar.html')



#-----------------------------------------COMPRA FINALIZADA-----------------------------------------#


@web_bp.route('/compra-finalizada')
def compra_finalizada():
    return render_template('CompraFinalizada.html')

#-----------------------------------------REGISTRO DE USUARIO-----------------------------------------#


@web_bp.route('/admin')
def admin():
    return render_template('admin_templates/admin.html')





@web_bp.route('/api/productos')
def api_productos():
    try:
        from app.models import Producto, Categoria
        # Obtener todos los productos activos con sus categorías
        productos = Producto.query.filter_by(activo=True).all()
        
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
            'productos': productos_data
        })
        
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

@web_bp.route('/api/productos/categoria/<int:categoria_id>')
def api_productos_por_categoria(categoria_id):
    try:
        from app.models import Producto
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
    
    
    # app/routes/web.py - Agrega estas rutas después de las rutas de productos

#-----------------------------------------CARRITO API-----------------------------------------#

@web_bp.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    try:
        # Verificar si el usuario está autenticado
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Debes iniciar sesión para agregar productos al carrito'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)

        # Validar datos
        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        # Verificar que el producto existe y está activo
        from app.models import Producto, Carrito, CarritoItem
        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        if producto.stock < cantidad:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400

        # Obtener o crear carrito activo del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            carrito = Carrito(usuario_id=session['user_id'])
            db.session.add(carrito)
            db.session.flush()  # Para obtener el ID sin commit

        # Verificar si el producto ya está en el carrito
        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id
        ).first()

        if item_existente:
            # Actualizar cantidad si ya existe
            nueva_cantidad = item_existente.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400
            item_existente.cantidad = nueva_cantidad
        else:
            # Crear nuevo item en el carrito
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

# app/routes/web.py - Rutas para el carrito

@web_bp.route('/carrito')
@login_required
def carrito():
    """Página principal del carrito"""
    return render_template('Carrito.html')

@web_bp.route('/api/carrito/detalles')
def api_carrito_detalles():
    """Obtener detalles completos del carrito"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        from app.models import Carrito, CarritoItem, Producto
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
                'total': subtotal,  # Por si agregas impuestos/envío después
                'count': len(carrito.items)
            }
        })

    except Exception as e:
        print(f"Error obteniendo carrito: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@web_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
def actualizar_cantidad_carrito(item_id):
    """Actualizar cantidad de un item en el carrito"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json()
        nueva_cantidad = data.get('cantidad', 1)

        from app.models import CarritoItem, Producto
        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        # Verificar que el item pertenece al usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        if not carrito or item.carrito_id != carrito.id_carrito:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403

        # Verificar stock
        producto = Producto.query.get(item.producto_id)
        if nueva_cantidad > producto.stock:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400

        if nueva_cantidad <= 0:
            # Eliminar item si cantidad es 0 o menos
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
    """Eliminar item del carrito"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        from app.models import CarritoItem, Carrito
        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        # Verificar que el item pertenece al usuario
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
    
    