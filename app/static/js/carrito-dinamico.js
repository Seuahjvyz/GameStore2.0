// app/static/js/carrito-dinamico.js
class CarritoDinamico {
    constructor() {
        this.carritoData = null;
        this.init();
    }

    async init() {
        await this.cargarCarrito();
        this.actualizarVistaCarrito();
        this.initEventListeners();
    }

    async cargarCarrito() {
        try {
            const response = await fetch('/api/carrito/detalles');
            const data = await response.json();

            if (data.success) {
                this.carritoData = data.carrito;
            } else {
                console.error('Error cargando carrito:', data.error);
                this.carritoData = { items: [], subtotal: 0, total: 0, count: 0 };
            }
        } catch (error) {
            console.error('Error:', error);
            this.carritoData = { items: [], subtotal: 0, total: 0, count: 0 };
        }
    }

    actualizarVistaCarrito() {
        const container = document.getElementById('carrito-container');
        if (!container) return;

        if (this.carritoData.items.length === 0) {
            container.innerHTML = this.crearCarritoVacioHTML();
        } else {
            container.innerHTML = this.crearCarritoConItemsHTML();
        }

        this.actualizarResumenCarrito();
    }

    crearCarritoVacioHTML() {
        return `
            <div class="carrito-vacio">
                <div class="empty-cart-icon">
                    <i class="fa-solid fa-cart-shopping"></i>
                </div>
                <h3>Tu carrito está vacío</h3>
                <p>Agrega algunos productos increíbles</p>
                <a href="/accesorios" class="btn btn-primary">Descubrir productos</a>
            </div>
        `;
    }

    crearCarritoConItemsHTML() {
        return `
            <div class="carrito-con-items">
                <div class="carrito-header">
                    <h3>Tu Carrito (${this.carritoData.count} productos)</h3>
                </div>
                
                <div class="carrito-items">
                    ${this.carritoData.items.map(item => this.crearItemHTML(item)).join('')}
                </div>
                
                <div class="carrito-resumen">
                    ${this.crearResumenHTML()}
                </div>
            </div>
        `;
    }

    crearItemHTML(item) {
        return `
            <div class="carrito-item" data-item-id="${item.id}">
                <div class="item-imagen">
                    <img src="${item.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${item.nombre}"
                         onerror="this.src='/static/img/placeholder.jpg'">
                </div>
                
                <div class="item-info">
                    <h4 class="item-nombre">${item.nombre}</h4>
                    <p class="item-precio-unitario">$${item.precio_unitario.toFixed(2)} c/u</p>
                </div>
                
                <div class="item-cantidad">
                    <button class="btn-cantidad btn-menos" data-item-id="${item.id}">
                        <i class="fa-solid fa-minus"></i>
                    </button>
                    <span class="cantidad-value">${item.cantidad}</span>
                    <button class="btn-cantidad btn-mas" data-item-id="${item.id}" 
                            ${item.cantidad >= item.stock ? 'disabled' : ''}>
                        <i class="fa-solid fa-plus"></i>
                    </button>
                </div>
                
                <div class="item-total">
                    <span class="total-price">$${item.total.toFixed(2)}</span>
                </div>
                
                <div class="item-acciones">
                    <button class="btn-eliminar" data-item-id="${item.id}" title="Eliminar">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    crearResumenHTML() {
        return `
            <div class="resumen-card">
                <h4>Resumen del Pedido</h4>
                
                <div class="resumen-linea">
                    <span>Subtotal:</span>
                    <span>$${this.carritoData.subtotal.toFixed(2)}</span>
                </div>
                
                <div class="resumen-linea">
                    <span>Envío:</span>
                    <span>Gratis</span>
                </div>
                
                <div class="resumen-linea total">
                    <span>Total:</span>
                    <span>$${this.carritoData.total.toFixed(2)}</span>
                </div>
                
                <button class="btn-pagar" id="btnPagar">
                    Proceder al Pago
                </button>
                
                <a href="/accesorios" class="btn-seguir-comprando">
                    <i class="fa-solid fa-arrow-left"></i> Seguir comprando
                </a>
            </div>
        `;
    }

    actualizarResumenCarrito() {
        // Actualizar contadores en otras partes de la página
        const contadores = document.querySelectorAll('.cart-count, .carrito-count, #carrito-contador');
        contadores.forEach(contador => {
            contador.textContent = this.carritoData.count;
            contador.style.display = this.carritoData.count > 0 ? 'inline' : 'none';
        });
    }

    initEventListeners() {
        // Delegación de eventos para los botones del carrito
        document.addEventListener('click', async (e) => {
            const target = e.target.closest('[data-item-id]');
            if (!target) return;

            const itemId = target.dataset.itemId;
            const item = this.carritoData.items.find(i => i.id == itemId);
            if (!item) return;

            if (target.classList.contains('btn-menos')) {
                await this.actualizarCantidad(itemId, item.cantidad - 1);
            } else if (target.classList.contains('btn-mas')) {
                await this.actualizarCantidad(itemId, item.cantidad + 1);
            } else if (target.classList.contains('btn-eliminar')) {
                await this.eliminarItem(itemId);
            }
        });

        // Botón de pagar
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btnPagar') {
                this.procederAlPago();
            }
        });
    }

    async actualizarCantidad(itemId, nuevaCantidad) {
        try {
            const response = await fetch(`/api/carrito/actualizar/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cantidad: nuevaCantidad
                })
            });

            const data = await response.json();

            if (data.success) {
                await this.cargarCarrito();
                this.actualizarVistaCarrito();
                
                // Actualizar el carrito simple también
                if (window.carritoSimple) {
                    window.carritoSimple.actualizarContadorCarrito();
                }
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarNotificacion('Error de conexión', 'error');
        }
    }

    async eliminarItem(itemId) {
        if (!confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
            return;
        }

        try {
            const response = await fetch(`/api/carrito/eliminar/${itemId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                await this.cargarCarrito();
                this.actualizarVistaCarrito();
                
                // Actualizar el carrito simple también
                if (window.carritoSimple) {
                    window.carritoSimple.actualizarContadorCarrito();
                }
                
                this.mostrarNotificacion('Producto eliminado del carrito', 'success');
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarNotificacion('Error de conexión', 'error');
        }
    }

    procederAlPago() {
        if (this.carritoData.count === 0) {
            this.mostrarNotificacion('Tu carrito está vacío', 'error');
            return;
        }
        window.location.href = '/pagar';
    }

    mostrarNotificacion(mensaje, tipo) {
        // Reutilizar el sistema de notificaciones del carrito simple
        if (window.carritoSimple && window.carritoSimple.mostrarNotificacion) {
            window.carritoSimple.mostrarNotificacion(mensaje, tipo);
        } else {
            alert(mensaje);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar en la página del carrito
    if (document.getElementById('carrito-container')) {
        window.carritoDinamico = new CarritoDinamico();
    }
});