// app/static/js/carrito-dinamico.js - VERSIÓN CORREGIDA
class CarritoDinamico {
    constructor() {
        this.carritoData = null;
        this.pedidoPendienteId = null;
        this.paypalButtons = null;
        this.paypalSDKCargado = false;
        this.init();
    }

    async init() {
        await this.cargarCarrito();
        this.actualizarVistaCarrito();
        this.initEventListeners();

        // Precargar PayPal SDK
        this.preloadPayPalSDK();
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
                <a href="/" class="btn btn-primary">Descubrir productos</a>
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
                
                <div class="resumen-linea total">
                    <strong>Total:</strong>
                    <strong>$${this.carritoData.total.toFixed(2)}</strong>
                </div>
                
                <button class="btn-pagar" id="btnPagar">
                    <i class="fa-brands fa-paypal"></i> Pagar con PayPal
                </button>
                
                <a href="/" class="btn-seguir-comprando">
                    <i class="fa-solid fa-arrow-left"></i> Seguir comprando
                </a>
            </div>
        `;
    }

    actualizarResumenCarrito() {
        const contadores = document.querySelectorAll('.cart-count, .carrito-count, #carrito-contador');
        contadores.forEach(contador => {
            contador.textContent = this.carritoData.count;
            contador.style.display = this.carritoData.count > 0 ? 'inline' : 'none';
        });
    }

    initEventListeners() {
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

    async agregarAlCarrito(productoId) {
        console.log(`🛒 Agregando producto ${productoId} al carrito`);

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

            if (data.success) {
                console.log('✅ Producto agregado/actualizado en carrito:', data);
                this.mostrarNotificacion(data.message, 'success');

                this.actualizarContadorCarrito(data.carrito_count);

                if (document.getElementById('carrito-container')) {
                    await this.cargarCarrito();
                    this.actualizarVistaCarrito();
                }
            } else {
                console.error('❌ Error al agregar al carrito:', data.error);
                this.mostrarNotificacion(data.error || 'Error al agregar al carrito', 'error');
            }
        } catch (error) {
            console.error('❌ Error agregando al carrito:', error);
            this.mostrarNotificacion('Error de conexión', 'error');
        }
    }

    actualizarContadorCarrito(count) {
        console.log('🔄 Actualizando contador del carrito:', count);

        if (window.actualizarContadorCarrito) {
            window.actualizarContadorCarrito(count);
        }

        const contadores = document.querySelectorAll('.carrito-count, .cart-count, #carrito-contador');
        contadores.forEach(contador => {
            contador.textContent = count;
            contador.style.display = count > 0 ? 'flex' : 'none';
            contador.style.position = 'absolute';
            contador.style.top = '-8px';
            contador.style.right = '-8px';
            contador.style.zIndex = '1001';
        });

        if (window.carritoSync) {
            window.carritoSync.notificarActualizacion();
        } else {
            localStorage.setItem('carritoUpdate', Date.now().toString());
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
        container.innerHTML = this.crearSeccionPagoHTML();
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
                            <div class="linea-total total-final">
                                <strong>Total:</strong>
                                <strong>$${this.carritoData.total.toFixed(2)}</strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metodo-pago-seccion">
                        <h3>Método de Pago</h3>
                        
                        <div class="paypal-buttons-container" id="paypal-button-container">
                            <div class="loading-paypal">
                                <i class="fa-solid fa-spinner fa-spin"></i> Inicializando PayPal...
                            </div>
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
        document.getElementById('btnVolverCarrito').addEventListener('click', () => {
            this.actualizarVistaCarrito();
        });

        this.inicializarPayPal();
    }

    // Precargar PayPal SDK al inicio - CONFIGURADO PARA SANDBOX
    preloadPayPalSDK() {
        if (window.paypal || this.paypalSDKCargado) {
            return;
        }

        console.log('📥 Precargando PayPal SDK de forma segura...');

        this.cargarPayPalDeFormaSegura();
    }

    async cargarPayPalDeFormaSegura() {
        try {
            // 1. Obtener configuración del backend
            const config = await this.obtenerConfiguracionPayPal();

            if (!config || !config.client_id) {
                throw new Error('Configuración de PayPal no disponible');
            }

            console.log('🔐 Configuración PayPal obtenida:', {
                client_id: config.client_id.substring(0, 10) + '...',
                mode: config.mode
            });

            // 2. Determinar la URL correcta (sandbox vs live)
            const baseUrl = config.mode === 'live'
                ? 'https://www.paypal.com'
                : 'https://www.sandbox.paypal.com';

            // 3. Cargar SDK
            const script = document.createElement('script');
            script.src = `${baseUrl}/sdk/js?client-id=${config.client_id}&currency=USD&intent=capture`;

            script.onload = () => {
                console.log('✅ PayPal SDK cargado exitosamente');
                this.paypalSDKCargado = true;
            };

            script.onerror = (error) => {
                console.error('❌ Error cargando PayPal SDK:', error);
                this.mostrarErrorPayPal('No se pudo cargar PayPal. Verifica tu conexión.');
            };

            document.body.appendChild(script);

        } catch (error) {
            console.error('❌ Error en carga segura de PayPal:', error);
            this.mostrarErrorPayPal('Error de configuración: ' + error.message);
        }
    }

    async obtenerConfiguracionPayPal() {
        try {
            const response = await fetch('/api/paypal/config');

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                return data;
            } else {
                throw new Error(data.error || 'Error del servidor');
            }
        } catch (error) {
            console.error('Error obteniendo configuración PayPal:', error);
            return null;
        }
    }

    mostrarErrorPayPal(mensaje) {
        this.mostrarNotificacion(mensaje, 'error');

        // También mostrar en la consola para debugging
        console.error('🔴 Error PayPal:', mensaje);
    }

    async inicializarPayPal() {
        console.log('🔄 Inicializando PayPal (Sandbox)...');

        try {
            // Esperar a que PayPal esté disponible
            await this.waitForPayPal();
            this.renderPayPalButtons();  // ← LLAMA DIRECTAMENTE A renderPayPalButtons

        } catch (error) {
            console.error('❌ Error inicializando PayPal:', error);
            this.mostrarErrorPayPal('Error al inicializar PayPal: ' + error.message);
        }
    }

    async waitForPayPal() {
        return new Promise((resolve, reject) => {
            if (window.paypal) {
                console.log('✅ PayPal SDK listo');
                resolve();
                return;
            }

            console.log('⏳ Esperando a que PayPal SDK esté disponible...');
            let attempts = 0;
            const maxAttempts = 40;

            const checkPayPal = setInterval(() => {
                attempts++;

                if (window.paypal) {
                    clearInterval(checkPayPal);
                    console.log('✅ PayPal SDK disponible después de ' + (attempts * 500) + 'ms');
                    resolve();
                    return;
                }

                if (attempts >= maxAttempts) {
                    clearInterval(checkPayPal);
                    reject(new Error('Timeout: PayPal SDK no se cargó después de 20 segundos'));
                    return;
                }
            }, 500);
        });
    }

    renderPayPalButtons() {
        console.log('🎨 Renderizando botones PayPal');

        if (!window.paypal) {
            console.error('❌ PayPal SDK no disponible');
            this.mostrarErrorPayPal('PayPal SDK no se cargó correctamente');
            return;
        }

        const container = document.getElementById('paypal-button-container');
        if (!container) {
            console.error('❌ Contenedor PayPal no encontrado');
            return;
        }

        try {
            // Limpiar container
            container.innerHTML = '';

            // Verificar que no haya botones ya renderizados
            if (this.paypalButtons) {
                try {
                    this.paypalButtons.close();
                } catch (e) {
                    // Ignorar error si no se puede cerrar
                }
            }

            this.paypalButtons = paypal.Buttons({
                style: {
                    layout: 'vertical',
                    color: 'gold',
                    shape: 'rect',
                    label: 'paypal',
                    height: 55,
                    tagline: false
                },

                createOrder: (data, actions) => {
                    console.log('💰 Creando orden PayPal con total:', this.carritoData.total);
                    return actions.order.create({
                        purchase_units: [{
                            amount: {
                                value: this.carritoData.total.toFixed(2),
                                currency_code: 'USD'
                            },
                            description: `Pedido GameStore - ${this.carritoData.count} productos`
                        }],
                        application_context: {
                            shipping_preference: 'NO_SHIPPING'
                        }
                    });
                },

                onApprove: async (data, actions) => {
    console.log('✅ Orden PayPal aprobada:', data);
    
    // Mostrar mensaje de procesamiento
    const container = document.getElementById('paypal-button-container');
    if (container) {
        container.innerHTML = '<div class="processing-payment"><i class="fa-solid fa-spinner fa-spin"></i> Procesando pago...</div>';
    }
    
    try {
        // ✅ YA NO CAPTURAMOS AQUÍ - Solo enviamos el order_id al backend
        console.log('📦 Enviando order_id al backend:', data.orderID);
        
        const response = await fetch('/api/pedidos/procesar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                metodo_pago: 'paypal',
                order_id: data.orderID  // Solo enviamos el ID
            })
        });

        const result = await response.json();
        console.log('📦 Respuesta del backend:', result);

        if (result.success) {
            console.log('✅ Pedido procesado exitosamente en BD:', result);
            
            // Limpiar carrito del localStorage
            localStorage.removeItem('carrito');
            
            // Actualizar contador del carrito a 0
            this.actualizarContadorCarrito(0);
            
            // Redirigir a página de éxito
            window.location.href = `/pago-exitoso?pedido_id=${result.pedido_id}`;
        } else {
            throw new Error(result.error || 'Error al procesar el pedido');
        }
        
    } catch (error) {
        console.error('❌ Error en onApprove:', error);
        this.mostrarNotificacion('Error al procesar el pago: ' + error.message, 'error');
        this.actualizarVistaCarrito();
    }
},

                onError: (err) => {
                    console.error('❌ Error PayPal:', err);
                    let errorMsg = 'Error en el proceso de PayPal';

                    if (err && err.message) {
                        errorMsg += ': ' + err.message;
                    }

                    this.mostrarNotificacion(errorMsg, 'error');
                    this.mostrarErrorPayPal(errorMsg);
                },

                onCancel: (data) => {
                    console.log('❌ Pago cancelado por usuario');
                    this.mostrarNotificacion('Pago cancelado. Puedes intentarlo nuevamente cuando lo desees.', 'warning');
                    this.actualizarVistaCarrito();
                }

            });

            this.paypalButtons.render('#paypal-button-container').then(() => {
                console.log('✅ Botones PayPal renderizados exitosamente');
                const loading = container.querySelector('.loading-paypal');
                if (loading) loading.remove();
            }).catch(error => {
                console.error('❌ Error renderizando botones PayPal:', error);
                this.mostrarErrorPayPal('Error al crear botones de PayPal: ' + error.message);
            });

        } catch (error) {
            console.error('❌ Error en renderPayPalButtons:', error);
            this.mostrarErrorPayPal('Error inesperado: ' + error.message);
        }
    }

    mostrarErrorPayPal(mensaje = 'Error con PayPal') {
        const container = document.getElementById('paypal-button-container');
        if (container) {
            container.innerHTML = `
                <div class="paypal-error">
                    <div class="error-icon">
                        <i class="fa-solid fa-exclamation-triangle"></i>
                    </div>
                    <h4>Error con PayPal</h4>
                    <p>${mensaje}</p>
                    <div class="error-actions">
                        <button class="btn-reintentar" onclick="carritoDinamico.reintentarPayPal()">
                            <i class="fa-solid fa-rotate"></i> Reintentar
                        </button>
                        <button class="btn-volver" onclick="carritoDinamico.actualizarVistaCarrito()">
                            <i class="fa-solid fa-arrow-left"></i> Volver al Carrito
                        </button>
                    </div>
                </div>
            `;
        }
    }

    reintentarPayPal() {
        console.log('🔄 Reintentando PayPal...');
        this.inicializarPayPal();
    }

    mostrarNotificacion(mensaje, tipo = 'info') {
        if (window.carritoSimple && window.carritoSimple.mostrarNotificacion) {
            window.carritoSimple.mostrarNotificacion(mensaje, tipo);
            return;
        }

        const notification = document.createElement('div');
        notification.className = `notification-custom ${tipo}`;

        let icon = 'info';
        if (tipo === 'success') icon = 'check';
        if (tipo === 'error') icon = 'exclamation-triangle';
        if (tipo === 'warning') icon = 'exclamation';

        notification.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid fa-${icon}"></i>
                <span>${mensaje}</span>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${tipo === 'success' ? '#4CAF50' : tipo === 'error' ? '#f44336' : tipo === 'warning' ? '#ff9800' : '#2196F3'};
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Función global para agregar al carrito
window.agregarAlCarritoGlobal = function (productoId) {
    if (window.carritoDinamico) {
        window.carritoDinamico.agregarAlCarrito(productoId);
    } else {
        fetch('/api/carrito/agregar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto_id: parseInt(productoId),
                cantidad: 1
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const contadores = document.querySelectorAll('.carrito-count, .cart-count');
                    contadores.forEach(contador => {
                        contador.textContent = data.carrito_count;
                        contador.style.display = data.carrito_count > 0 ? 'inline' : 'none';
                    });
                }
            });
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('carrito-container')) {
        window.carritoDinamico = new CarritoDinamico();
    }
});