from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.TIMESTAMP, nullable=True)
    telefono = db.Column(db.String(15))
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'