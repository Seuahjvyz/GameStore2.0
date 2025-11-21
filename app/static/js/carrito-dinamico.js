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
        this.mostrarSeccionPago();
}

mostrarSeccionPago() {
    const container = document.getElementById('carrito-container');
    
    // Ocultar el carrito y mostrar la sección de pago
    container.innerHTML = this.crearSeccionPagoHTML();
    
    // Agregar event listeners para los botones de la sección de pago
    this.initEventListenersPago();
}

crearSeccionPagoHTML() {
    return `
        <div class="pago-contenedor">
            <div class="pago-header">
                <button class="btn-volver-carrito" id="btnVolverCarrito">
                    <i class="fa-solid fa-arrow-left"></i> Volver al Carrito
                </button>
                <h2>Finalizar Compra</h2>
            </div>
            
            <div class="pago-contenido">
                <div class="resumen-pedido-pago">
                    <h3>Resumen de tu Pedido</h3>
                    <div class="productos-pago">
                        ${this.carritoData.items.map(item => this.crearProductoPagoHTML(item)).join('')}
                    </div>
                    <div class="total-pago">
                        <div class="linea-total">
                            <span>Subtotal:</span>
                            <span>$${this.carritoData.subtotal.toFixed(2)}</span>
                        </div>
                        <div class="linea-total">
                            <span>Envío:</span>
                            <span>Gratis</span>
                        </div>
                        <div class="linea-total total-final">
                            <span>Total:</span>
                            <span>$${this.carritoData.total.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="metodo-pago-seccion">
                    <h3>Método de Pago</h3>
                    <div class="opciones-pago">
                        <label class="opcion-pago">
                            <input type="radio" name="metodo-pago" value="paypal" checked>
                            <i class="fa-brands fa-paypal"></i>
                            <span>PayPal</span>
                        </label>
                    </div>
                    
                    <div class="datos-tarjeta">
                        <h4>Datos de Pago</h4>
                        <form id="formPago">
                            <div class="form-group">
                                <label for="titular-tarjeta">Titular de la tarjeta</label>
                                <input type="text" id="titular-tarjeta" placeholder="Nombre del titular" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="numero-tarjeta">Número de tarjeta</label>
                                <input type="text" id="numero-tarjeta" placeholder="1234 5678 9012 3456" maxlength="19" required>
                            </div>
                            
                            <div class="form-fila">
                                <div class="form-group">
                                    <label for="fecha-vencimiento">Fecha de vencimiento</label>
                                    <input type="text" id="fecha-vencimiento" placeholder="MM/AA" maxlength="5" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="cvv">CVV</label>
                                    <input type="text" id="cvv" placeholder="123" maxlength="3" required>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn-confirmar-pago">
                                <i class="fa-solid fa-lock"></i>
                                Confirmar Pago
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
}

crearProductoPagoHTML(item) {
    return `
        <div class="producto-pago">
            <img src="${item.imagen || '/static/img/placeholder.jpg'}" alt="${item.nombre}">
            <div class="info-producto-pago">
                <h4>${item.nombre}</h4>
                <p>$${item.precio_unitario.toFixed(2)} x ${item.cantidad}</p>
            </div>
            <span class="subtotal-producto">$${item.total.toFixed(2)}</span>
        </div>
    `;
}

initEventListenersPago() {
    // Botón volver al carrito
    document.getElementById('btnVolverCarrito').addEventListener('click', () => {
        this.actualizarVistaCarrito();
    });
    
    // Formulario de pago
    document.getElementById('formPago').addEventListener('submit', (e) => {
        e.preventDefault();
        this.procesarPago();
    });
    
    // Formatear número de tarjeta
    document.getElementById('numero-tarjeta').addEventListener('input', (e) => {
        e.target.value = this.formatearNumeroTarjeta(e.target.value);
    });
    
    // Formatear fecha de vencimiento
    document.getElementById('fecha-vencimiento').addEventListener('input', (e) => {
        e.target.value = this.formatearFechaVencimiento(e.target.value);
    });
}

formatearNumeroTarjeta(valor) {
    return valor.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim();
}

formatearFechaVencimiento(valor) {
    return valor.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2');
}

async procesarPago() {
    try {
        // Aquí iría la lógica para procesar el pago con tu backend
        const response = await fetch('/api/pagos/procesar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                carrito_id: this.carritoData.id,
                metodo_pago: document.querySelector('input[name="metodo-pago"]:checked').value,
                // otros datos del formulario...
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.mostrarConfirmacionCompra();
        } else {
            this.mostrarNotificacion(data.error, 'error');
        }
    } catch (error) {
        console.error('Error procesando pago:', error);
        this.mostrarNotificacion('Error al procesar el pago', 'error');
    }
}

mostrarConfirmacionCompra() {
    const container = document.getElementById('carrito-container');
    container.innerHTML = `
        <div class="compra-exitosa">
            <div class="icono-exito">
                <i class="fa-solid fa-check-circle"></i>
            </div>
            <h2>¡Compra Exitosa!</h2>
            <p>Tu pedido ha sido procesado correctamente</p>
            <p>Número de orden: #${Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
            <div class="acciones-compra">
                <a href="/pedidos" class="btn-ver-pedidos">Ver mis pedidos</a>
                <a href="/" class="btn-seguir-comprando">Seguir comprando</a>
            </div>
        </div>
    `;
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