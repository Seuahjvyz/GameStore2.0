// static/js/pedidos.js - VERSIÓN CORREGIDA

class GestorPedidos {
    constructor() {
        this.pedidos = [];
        this.init();
    }
    
    async init() {
        await this.cargarPedidos();
        this.configurarActualizacionAutomatica();
    }
    
    // En pedidos.js, dentro de cargarPedidos(), antes del fetch
async cargarPedidos() {
    const contenedor = document.querySelector('.lista-pedidos');
    if (!contenedor) return;
    
    // Mostrar loading
    contenedor.innerHTML = `
        <div class="loading">
            <i class="fa-solid fa-spinner fa-spin"></i>
            Cargando tus pedidos...
        </div>
    `;
    
    try {
        // 🔥 DEBUG: Verificar usuario actual
        const userResponse = await fetch('/api/usuario/actual');
        const userData = await userResponse.json();
        console.log('👤 Usuario actual:', userData);
        
        console.log('📡 Solicitando pedidos a /api/pedidos/mis-pedidos');
        const respuesta = await fetch('/api/pedidos/mis-pedidos');
        console.log('📥 Respuesta recibida, status:', respuesta.status);
        
        const data = await respuesta.json();
        console.log('📊 Datos de pedidos recibidos:', data);
        
        if (data.success) {
            this.pedidos = data.pedidos;
            console.log(`✅ ${this.pedidos.length} pedidos cargados`);
            this.renderizarPedidos();
        } else {
            throw new Error(data.error || 'Error al cargar pedidos');
        }
    } catch (error) {
        console.error('❌ Error en cargarPedidos:', error);
        // ... resto del código
    }
}
    
    renderizarPedidos() {
        const contenedor = document.querySelector('.lista-pedidos');
        if (!contenedor) return;
        
        if (this.pedidos.length === 0) {
            contenedor.innerHTML = `
                <div class="no-pedidos">
                    <i class="fa-solid fa-box-open"></i>
                    <h2>No tienes pedidos aún</h2>
                    <p>Cuando realices una compra, podrás ver el estado de tus pedidos aquí.</p>
                    <a href="/" class="btn-seguir-comprando">Seguir comprando</a>
                </div>
            `;
            return;
        }
        
        let html = '';
        this.pedidos.forEach(pedido => {
            html += this.renderizarPedido(pedido);
        });
        
        contenedor.innerHTML = html;
        
        // Agregar event listeners para botones de cancelar
        document.querySelectorAll('.btn-cancelar-pedido').forEach(btn => {
            btn.addEventListener('click', (e) => this.cancelarPedido(e));
        });
    }
    
    renderizarPedido(pedido) {
        const fechaCompra = pedido.fecha_pedido ? new Date(pedido.fecha_pedido).toLocaleDateString('es-MX', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'Fecha no disponible';
        
        const fechaEntrega = pedido.fecha_entrega_estimada ? 
            new Date(pedido.fecha_entrega_estimada).toLocaleDateString('es-MX', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            }) : 'Por determinar';
        
        // Generar HTML de productos
        let productosHTML = '';
        if (pedido.items && pedido.items.length > 0) {
            pedido.items.forEach(item => {
                productosHTML += `
                    <div class="pedido-producto">
                        <img src="${item.imagen || '/static/img/default-product.png'}" 
                             alt="${item.nombre}"
                             onerror="this.src='/static/img/default-product.png'">
                        <div class="producto-info">
                            <h4 class="nombre-producto">${item.nombre}</h4>
                            <p class="pedido-precio">$${item.precio_unitario.toFixed(2)} c/u</p>
                            <p class="pedido-cantidad">Cantidad: ${item.cantidad}</p>
                            <p class="pedido-precio-total">Subtotal: $${item.subtotal.toFixed(2)}</p>
                        </div>
                    </div>
                `;
            });
        }
        
        const puedeCancelar = pedido.puede_cancelar && 
            pedido.estado_seguimiento !== 'cancelado' && 
            pedido.estado_seguimiento !== 'entregado';
        
        const botonCancelar = puedeCancelar ? 
            `<button class="btn-cancelar-pedido" data-pedido-id="${pedido.id_pedido}">
                <i class="fa-solid fa-ban"></i> Cancelar pedido
            </button>` : '';
        
        const estadoClass = this.getEstadoClass(pedido.estado_seguimiento);
        const estadoTexto = this.getEstadoTexto(pedido.estado_seguimiento);
        
        return `
            <div class="pedido-item" data-pedido-id="${pedido.id_pedido}">
                <div class="pedido-info">
                    <div class="pedido-header">
                        <h3 class="product-title">Pedido ${pedido.numero_pedido}</h3>
                        <span class="pedido-fecha">${fechaCompra}</span>
                    </div>
                    
                    <div class="pedido-fechas">
                        <p><strong>Fecha de compra:</strong> ${fechaCompra}</p>
                        <p><strong>Fecha estimada de entrega:</strong> ${fechaEntrega}</p>
                    </div>
                    
                    <div class="pedido-estado">
                        <span class="estado-badge ${estadoClass}">
                            ${estadoTexto}
                        </span>
                    </div>
                    
                    <div class="pedido-total">
                        <strong>Total:</strong> $${pedido.total.toFixed(2)}
                    </div>
                    
                    <div class="pedidos-contenedor-producto">
                        ${productosHTML}
                    </div>
                    
                    <div class="pedido-acciones">
                        ${botonCancelar}
                    </div>
                </div>
            </div>
        `;
    }
    
    getEstadoClass(estado) {
        const clases = {
            'procesando': 'estado-procesando',
            'enviado': 'estado-enviado',
            'entregado': 'estado-entregado',
            'cancelado': 'estado-cancelado'
        };
        return clases[estado] || 'estado-procesando';
    }
    
    getEstadoTexto(estado) {
        const textos = {
            'procesando': 'Procesando',
            'enviado': 'Enviado',
            'entregado': 'Entregado',
            'cancelado': 'Cancelado'
        };
        return textos[estado] || 'Procesando';
    }
    
    async cancelarPedido(event) {
        const btn = event.currentTarget;
        const pedidoId = btn.dataset.pedidoId;
        
        if (!confirm('¿Estás seguro de cancelar este pedido? Esta acción no se puede deshacer.')) {
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Cancelando...';
        
        try {
            const respuesta = await fetch(`/api/pedidos/${pedidoId}/cancelar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await respuesta.json();
            
            if (data.success) {
                this.mostrarNotificacion('Pedido cancelado exitosamente', 'success');
                await this.cargarPedidos(); // Recargar la lista
            } else {
                throw new Error(data.error || 'Error al cancelar pedido');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarNotificacion(error.message, 'error');
            await this.cargarPedidos(); // Recargar para mostrar estado actual
        }
    }
    
    mostrarNotificacion(mensaje, tipo) {
        // Usar la misma función que en carrito-dinamico.js
        const notification = document.createElement('div');
        notification.className = `notification-custom ${tipo}`;
        
        let icon = 'info-circle';
        if (tipo === 'success') icon = 'check-circle';
        if (tipo === 'error') icon = 'exclamation-circle';
        
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
            background: ${tipo === 'success' ? '#4CAF50' : tipo === 'error' ? '#f44336' : '#2196F3'};
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
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    configurarActualizacionAutomatica() {
        // Actualizar cada 5 minutos para ver cambios de estado
        setInterval(() => this.cargarPedidos(), 5 * 60 * 1000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si estamos en la página de pedidos
    if (document.querySelector('.lista-pedidos')) {
        window.gestorPedidos = new GestorPedidos();
    }
});