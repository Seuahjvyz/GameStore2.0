// Script SIMPLIFICADO para agregar productos al carrito
class CarritoSimple {
    constructor() {
        this.initEventListeners();
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
        const productoCard = boton.closest('.producto, .producto-card, .product-card');
        if (!productoCard) return;
        
        const productoId = this.obtenerProductoId(productoCard);
        
        if (!productoId) {
            console.error('No se pudo obtener el ID del producto');
            this.mostrarNotificacion('Error: Producto no válido', 'error');
            return;
        }
        
        console.log(`🛒 Intentando agregar producto ID: ${productoId}`);
        
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
                this.mostrarNotificacion('✅ Producto agregado al carrito', 'success');
                this.animarBotonAgregado(boton);
                this.actualizarContadorCarrito();
            } else {
                this.mostrarNotificacion(data.message || '❌ Error al agregar producto', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarNotificacion('❌ Error de conexión', 'error');
        }
    }
    
    obtenerProductoId(elemento) {
        // Buscar ID de diferentes formas
        return elemento.dataset.productoId || 
               elemento.querySelector('[data-producto-id]')?.dataset.productoId;
    }
    
    async actualizarContadorCarrito() {
        try {
            const response = await fetch('/api/carrito');
            if (response.ok) {
                const data = await response.json();
                const contadores = document.querySelectorAll('.cart-count, .carrito-count');
                contadores.forEach(contador => {
                    contador.textContent = data.count || 0;
                    contador.style.display = (data.count > 0) ? 'inline' : 'none';
                });
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
        // Notificación simple
        const notification = document.createElement('div');
        notification.className = `notification notification-${tipo}`;
        notification.textContent = mensaje;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${tipo === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            font-weight: bold;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.carritoSimple = new CarritoSimple();
    console.log('🛒 Carrito simple inicializado');
});