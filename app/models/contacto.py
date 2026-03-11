# app/models/contacto.py
from app import db
from datetime import datetime

class Contacto(db.Model):
    __tablename__ = 'mensajes_contacto'
    
    id_mensaje = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    asunto = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    respondido = db.Column(db.Boolean, default=False)
    ip_usuario = db.Column(db.String(45))  # Para guardar IP (opcional)
    user_agent = db.Column(db.String(200))  # Para guardar navegador (opcional)
    
    def __repr__(self):
        return f'<MensajeContacto {self.nombre} - {self.asunto}>'
    
    def to_dict(self):
        return {
            'id': self.id_mensaje,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'asunto': self.get_asunto_display(),
            'asunto_valor': self.asunto,
            'mensaje': self.mensaje,
            'fecha_envio': self.fecha_envio.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_envio else None,
            'leido': self.leido,
            'respondido': self.respondido
        }
    
    def get_asunto_display(self):
        asuntos = {
            'consulta': 'Consulta general',
            'pedido': 'Problema con un pedido',
            'producto': 'Información de producto',
            'sugerencia': 'Sugerencia',
            'reclamacion': 'Reclamación'
        }
        return asuntos.get(self.asunto, self.asunto)