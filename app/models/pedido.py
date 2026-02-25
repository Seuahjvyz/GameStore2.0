# models/pedido.py
from app import db
from datetime import datetime, timedelta

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id_pedido = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.DateTime, nullable=True)
    fecha_entrega_real = db.Column(db.DateTime, nullable=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(50), default='pendiente')  # Estado del pago: pendiente, completado, fallido
    estado_seguimiento = db.Column(db.String(50), default='procesando')  # procesando, enviado, entregado, cancelado
    direccion_envio = db.Column(db.Text)
    metodo_pago = db.Column(db.String(50), default='paypal')
    id_transaccion_paypal = db.Column(db.String(255))
    puede_cancelar = db.Column(db.Boolean, default=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))
    items = db.relationship('PedidoItem', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def calcular_fecha_entrega(self):
        """Calcula la fecha de entrega estimada (20 días hábiles después de la compra)"""
        if not self.fecha_pedido:
            self.fecha_pedido = datetime.utcnow()
        
        # Contar 20 días hábiles (sin contar sábados y domingos)
        dias_habiles = 0
        fecha_temp = self.fecha_pedido
        
        while dias_habiles < 20:
            fecha_temp += timedelta(days=1)
            # Lunes a viernes son hábiles (0=lunes, 6=domingo)
            if fecha_temp.weekday() < 5:  # 0-4 son lunes a viernes
                dias_habiles += 1
        
        self.fecha_entrega_estimada = fecha_temp
        return self.fecha_entrega_estimada
    
    def actualizar_estado_por_fecha(self):
        """Actualiza el estado de seguimiento basado en la fecha actual"""
        if not self.fecha_entrega_estimada:
            return
        
        ahora = datetime.utcnow()
        
        # Si ya está cancelado o entregado, no cambiar
        if self.estado_seguimiento in ['cancelado', 'entregado']:
            self.puede_cancelar = False
            return
        
        # Calcular días desde la compra
        dias_desde_compra = (ahora - self.fecha_pedido).days
        
        # Verificar si puede cancelar (menos de 1 día)
        self.puede_cancelar = dias_desde_compra < 1 and self.estado_seguimiento != 'cancelado'
        
        # Actualizar estado según días transcurridos
        if ahora >= self.fecha_entrega_estimada:
            self.estado_seguimiento = 'entregado'
            if not self.fecha_entrega_real:
                self.fecha_entrega_real = ahora
            self.puede_cancelar = False
        elif dias_desde_compra >= 7:
            self.estado_seguimiento = 'enviado'
        else:
            self.estado_seguimiento = 'procesando'
    
    def cancelar(self):
        """Cancela el pedido si es posible"""
        self.actualizar_estado_por_fecha()
        
        if not self.puede_cancelar:
            return False, "Ya no es posible cancelar este pedido"
        
        self.estado_seguimiento = 'cancelado'
        self.puede_cancelar = False
        
        # Restaurar stock de los productos
        for item in self.items:
            producto = item.producto
            if producto:
                producto.stock += item.cantidad
        
        db.session.commit()
        return True, "Pedido cancelado exitosamente"
    
    def to_dict(self):
        """Convierte el pedido a diccionario para JSON"""
        self.actualizar_estado_por_fecha()
        
        return {
            'id_pedido': self.id_pedido,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_entrega_estimada': self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            'fecha_entrega_real': self.fecha_entrega_real.isoformat() if self.fecha_entrega_real else None,
            'total': float(self.total),
            'estado_pago': self.estado,
            'estado_seguimiento': self.estado_seguimiento,
            'metodo_pago': self.metodo_pago,
            'id_transaccion_paypal': self.id_transaccion_paypal,
            'puede_cancelar': self.puede_cancelar,
            'items': [item.to_dict() for item in self.items]
        }

class PedidoItem(db.Model):
    __tablename__ = 'pedido_items'
    id_item = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2))
    
    producto = db.relationship('Producto', backref='pedido_items')
    
    def to_dict(self):
        """Convierte el item a diccionario para JSON"""
        return {
            'id_item': self.id_item,
            'producto_id': self.producto_id,
            'nombre': self.producto.nombre if self.producto else 'Producto no disponible',
            'imagen': self.producto.imagen if self.producto and hasattr(self.producto, 'imagen') else '/static/img/default-product.png',
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.cantidad * self.precio_unitario)
        }