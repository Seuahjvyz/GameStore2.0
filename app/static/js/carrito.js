// app/static/js/agregar-carrito.js - Versión mejorada
class CarritoSimple {
    constructor() {
        this.initEventListeners();
        this.actualizarContadorCarrito(); // Actualizar contador al cargar
    }
    
    initEventListeners() {
        // Delegación de eventos para botones "Agregar al Carrito"
        document.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn_carrito, .btn-agregar, .btn-agregar-carrito');
            if (boton) {
                e.preventDefault();
                e.stopPropagation();
                this.agregarProductoDesdeBoton(boton);
            }
        });
    }
    
    async agregarProductoDesdeBoton(boton) {
        const productoCard = boton.closest('.producto');
        if (!productoCard) {
            console.error('No se encontró la tarjeta del producto');
            return;
        }
        
        const productoId = this.obtenerProductoId(productoCard, boton);
        
        if (!productoId) {
            console.error('No se pudo obtener el ID del producto');
            this.mostrarNotificacion('Error: Producto no válido', 'error');
            return;
        }
        
        console.log(`🛒 Intentando agregar producto ID: ${productoId}`);
        
        // Deshabilitar botón temporalmente
        this.deshabilitarBoton(boton);
        
        try {
            const response = await fetch('/api/carrito/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    producto_id: parseInt(productoId),
                    cantidad: 1
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.mostrarNotificacion('✅ ' + data.message, 'success');
                this.animarBotonAgregado(boton);
                this.actualizarContadorCarrito();
            } else {
                const errorMsg = data.error || 'Error al agregar producto';
                this.mostrarNotificacion('❌ ' + errorMsg, 'error');
                
                // Si es error de autenticación, redirigir al login
                if (response.status === 401) {
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            this.mostrarNotificacion('❌ Error de conexión con el servidor', 'error');
        } finally {
            this.habilitarBoton(boton);
        }
    }
    
    obtenerProductoId(elemento, boton) {
        // Buscar ID en diferentes lugares
        return elemento.dataset.productoId || 
               boton.dataset.productoId ||
               elemento.getAttribute('data-producto-id') ||
               boton.getAttribute('data-producto-id');
    }
    
    deshabilitarBoton(boton) {
        boton.disabled = true;
        boton.style.opacity = '0.6';
        boton.style.cursor = 'wait';
    }
    
    habilitarBoton(boton) {
        boton.disabled = false;
        boton.style.opacity = '1';
        boton.style.cursor = 'pointer';
    }
    
    async actualizarContadorCarrito() {
        try {
            const response = await fetch('/api/carrito');
            if (response.ok) {
                const data = await response.json();
                const contadores = document.querySelectorAll('.cart-count, .carrito-count, #carrito-contador');
                
                contadores.forEach(contador => {
                    contador.textContent = data.count || 0;
                    contador.style.display = (data.count > 0) ? 'inline' : 'none';
                });
                
                console.log(`🛒 Contador actualizado: ${data.count} productos`);
            }
        } catch (error) {
            console.error('Error actualizando contador:', error);
        }
    }
    
    animarBotonAgregado(boton) {
        const textoOriginal = boton.innerHTML;
        
        boton.innerHTML = '<i class="fa-solid fa-check"></i> Agregado';
        boton.style.background = '#10b981';
        boton.style.borderColor = '#10b981';
        boton.disabled = true;
        
        setTimeout(() => {
            boton.innerHTML = textoOriginal;
            boton.style.background = '';
            boton.style.borderColor = '';
            boton.disabled = false;
        }, 2000);
    }
    
    mostrarNotificacion(mensaje, tipo = 'success') {
        // Eliminar notificaciones existentes
        const notificacionesExistentes = document.querySelectorAll('.notification-custom');
        notificacionesExistentes.forEach(notif => notif.remove());
        
        // Crear nueva notificación
        const notification = document.createElement('div');
        notification.className = `notification-custom notification-${tipo}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${mensaje}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 20px;
            background: ${tipo === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease-out;
            max-width: 400px;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-eliminar después de 4 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 4000);
    }
}

// Agregar estilos de animación
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-content i {
        font-size: 1.2em;
    }
`;
document.head.appendChild(style);

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.carritoSimple = new CarritoSimple();
    console.log('🛒 Carrito simple inicializado');
});