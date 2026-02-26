// static/js/admin-pedidos.js
document.addEventListener('DOMContentLoaded', function () {
    let pedidos = [];
    let filtrosActuales = {};
    let pedidoSeleccionadoId = null;
    let clientes = [];
    let productos = [];
    let carritoTemporal = [];
    let clienteSeleccionado = null;
    let categorias = [];

    // Elementos DOM
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const filtroEstado = document.getElementById('filtroEstado');
    const filtroFechaInicio = document.getElementById('filtroFechaInicio');
    const filtroFechaFin = document.getElementById('filtroFechaFin');
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    const btnAgregarPedido = document.getElementById('btnAgregarPedido');
    const tbodyPedidos = document.getElementById('tbodyPedidos');
    //const contadorPedidos = document.getElementById('contadorPedidos');
    const loadingPedidos = document.getElementById('loadingPedidos');
    const tablaPedidosContainer = document.getElementById('tablaPedidosContainer');
    const noPedidos = document.getElementById('noPedidos');

    // Modales
    const modalDetalle = document.getElementById('modalDetallePedido');
    const modalEstado = document.getElementById('modalCambiarEstado');
    const modalNuevoPaso1 = document.getElementById('modalNuevoPedidoPaso1');
    const modalNuevoPaso2 = document.getElementById('modalNuevoPedidoPaso2');
    
    // Elementos de modales
    const modalCerrar = document.getElementById('modalCerrar');
    const modalEstadoCerrar = document.getElementById('modalEstadoCerrar');
    const modalNuevoPaso1Cerrar = document.getElementById('modalNuevoPaso1Cerrar');
    const modalNuevoPaso2Cerrar = document.getElementById('modalNuevoPaso2Cerrar');
    const btnCancelarCambio = document.getElementById('btnCancelarCambio');
    const btnConfirmarCambio = document.getElementById('btnConfirmarCambio');
    const btnCancelarNuevoPaso1 = document.getElementById('btnCancelarNuevoPaso1');
    const btnVolverPaso1 = document.getElementById('btnVolverPaso1');
    const btnSiguientePaso = document.getElementById('btnSiguientePaso');
    const btnCrearPedido = document.getElementById('btnCrearPedido');
    const selectNuevoEstado = document.getElementById('selectNuevoEstado');
    const selectCliente = document.getElementById('selectCliente');
    const estadoPedidoId = document.getElementById('estadoPedidoId');
    const clienteSeleccionadoSpan = document.getElementById('clienteSeleccionado');
    const buscarProducto = document.getElementById('buscarProducto');
    const filtroCategoriaProducto = document.getElementById('filtroCategoriaProducto');
    const productosGrid = document.getElementById('productosGrid');
    const carritoResumen = document.getElementById('carritoResumen');
    const carritoItems = document.getElementById('carritoItems');
    const carritoTotal = document.getElementById('carritoTotal');

    // Cargar datos al iniciar
    cargarPedidos();
    cargarClientes();
    cargarProductos();
    cargarCategorias();

    // Event listeners
    if (searchButton) {
        searchButton.addEventListener('click', aplicarFiltros);
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') aplicarFiltros();
        });
    }

    if (filtroEstado) {
        filtroEstado.addEventListener('change', aplicarFiltros);
    }
    
    if (filtroFechaInicio) {
        filtroFechaInicio.addEventListener('change', aplicarFiltros);
    }
    
    if (filtroFechaFin) {
        filtroFechaFin.addEventListener('change', aplicarFiltros);
    }
    
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', limpiarFiltros);
    }
    
    if (btnAgregarPedido) {
        btnAgregarPedido.addEventListener('click', mostrarModalNuevoPaso1);
    }

    // ============================================
    // EVENT LISTENERS PARA MODALES - CORREGIDOS
    // ============================================
    
    // Cerrar modales con la X
    if (modalCerrar) {
        modalCerrar.addEventListener('click', function() {
            cerrarModal(modalDetalle);
        });
    }
    
    if (modalEstadoCerrar) {
        modalEstadoCerrar.addEventListener('click', function() {
            cerrarModal(modalEstado);
        });
    }
    
    if (modalNuevoPaso1Cerrar) {
        modalNuevoPaso1Cerrar.addEventListener('click', function() {
            cerrarModal(modalNuevoPaso1);
        });
    }
    
    if (modalNuevoPaso2Cerrar) {
        modalNuevoPaso2Cerrar.addEventListener('click', function() {
            cerrarModal(modalNuevoPaso2);
        });
    }

    // Botones Cancelar
    if (btnCancelarCambio) {
        btnCancelarCambio.addEventListener('click', function() {
            cerrarModal(modalEstado);
        });
    }
    
    if (btnCancelarNuevoPaso1) {
        btnCancelarNuevoPaso1.addEventListener('click', function() {
            cerrarModal(modalNuevoPaso1);
        });
    }

    // Botón Volver
    if (btnVolverPaso1) {
        btnVolverPaso1.addEventListener('click', volverAPaso1);
    }
    
    // Botones Confirmar y Siguiente
    if (btnConfirmarCambio) {
        btnConfirmarCambio.addEventListener('click', confirmarCambioEstado);
    }
    
    if (btnSiguientePaso) {
        btnSiguientePaso.addEventListener('click', irAPaso2);
    }
    
    if (btnCrearPedido) {
        btnCrearPedido.addEventListener('click', crearPedido);
    }
    
    if (selectCliente) {
        selectCliente.addEventListener('change', function() {
            const clienteId = this.value;
            if (btnSiguientePaso) {
                btnSiguientePaso.disabled = !clienteId;
            }
            if (clienteId) {
                clienteSeleccionado = clientes.find(c => c.id == clienteId);
            }
        });
    }

    // Event listeners para búsqueda de productos
    if (buscarProducto) {
        buscarProducto.addEventListener('input', filtrarProductos);
    }
    
    if (filtroCategoriaProducto) {
        filtroCategoriaProducto.addEventListener('change', filtrarProductos);
    }

    // Cerrar modales con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (modalDetalle && modalDetalle.style.display === 'block') cerrarModal(modalDetalle);
            if (modalEstado && modalEstado.style.display === 'block') cerrarModal(modalEstado);
            if (modalNuevoPaso1 && modalNuevoPaso1.style.display === 'block') cerrarModal(modalNuevoPaso1);
            if (modalNuevoPaso2 && modalNuevoPaso2.style.display === 'block') cerrarModal(modalNuevoPaso2);
        }
    });

    // Cerrar modales haciendo clic fuera
    window.addEventListener('click', function(e) {
        if (e.target === modalDetalle) cerrarModal(modalDetalle);
        if (e.target === modalEstado) cerrarModal(modalEstado);
        if (e.target === modalNuevoPaso1) cerrarModal(modalNuevoPaso1);
        if (e.target === modalNuevoPaso2) cerrarModal(modalNuevoPaso2);
    });

    // Función para cerrar modal
    function cerrarModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            if (modal === modalNuevoPaso2) {
                limpiarCarritoTemporal();
            }
        }
    }

    function cargarPedidos(filtros = {}) {
        if (!loadingPedidos) return;
        
        loadingPedidos.style.display = 'block';
        if (tablaPedidosContainer) tablaPedidosContainer.style.display = 'none';
        if (noPedidos) noPedidos.style.display = 'none';

        let url = '/api/admin/pedidos?';
        const params = new URLSearchParams();

        if (filtros.search) params.append('search', filtros.search);
        if (filtros.estado) params.append('estado_pago', filtros.estado);
        if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio);
        if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin);

        fetch(url + params.toString())
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    pedidos = data.pedidos;
                    mostrarPedidos(pedidos);
                    actualizarContador(pedidos.length);
                } else {
                    throw new Error(data.error || 'Error al cargar pedidos');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarError(error.message);
            })
            .finally(() => {
                if (loadingPedidos) loadingPedidos.style.display = 'none';
            });
    }

    function cargarClientes() {
        fetch('/api/admin/usuarios?rol=2')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    clientes = data.usuarios;
                    actualizarSelectClientes();
                }
            })
            .catch(error => console.error('Error cargando clientes:', error));
    }

    function cargarProductos() {
        fetch('/api/admin/productos')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    productos = data.productos;
                }
            })
            .catch(error => console.error('Error cargando productos:', error));
    }

    function cargarCategorias() {
        fetch('/api/categorias')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    categorias = data.categorias;
                    actualizarSelectCategorias();
                }
            })
            .catch(error => console.error('Error cargando categorías:', error));
    }

    function actualizarSelectClientes() {
        if (!selectCliente) return;
        
        if (clientes.length === 0) {
            selectCliente.innerHTML = '<option value="">No hay clientes disponibles</option>';
            return;
        }

        let options = '<option value="">Seleccionar cliente</option>';
        clientes.forEach(cliente => {
            options += `<option value="${cliente.id}">${cliente.username} (${cliente.email})</option>`;
        });
        selectCliente.innerHTML = options;
    }

    function actualizarSelectCategorias() {
        if (!filtroCategoriaProducto) return;
        
        let options = '<option value="">Todas las categorías</option>';
        categorias.forEach(cat => {
            options += `<option value="${cat.id}">${cat.nombre}</option>`;
        });
        filtroCategoriaProducto.innerHTML = options;
    }

    function mostrarPedidos(pedidos) {
        if (!tbodyPedidos) return;

        tbodyPedidos.innerHTML = '';

        if (pedidos.length === 0) {
            if (noPedidos) noPedidos.style.display = 'block';
            if (tablaPedidosContainer) tablaPedidosContainer.style.display = 'none';
            return;
        }

        if (tablaPedidosContainer) tablaPedidosContainer.style.display = 'block';
        if (noPedidos) noPedidos.style.display = 'none';

        pedidos.forEach(pedido => {
            const fila = document.createElement('tr');

            fila.innerHTML = `
                <td><strong>${pedido.numero_pedido || '#' + pedido.id_pedido}</strong></td>
                <td>
                    <div class="cliente-info">
                        <strong>${pedido.cliente_nombre || 'Cliente'}</strong>
                        <small>${pedido.cliente_email || ''}</small>
                    </div>
                </td>
                <td class="total-cell">$${(pedido.total_pedido || 0).toFixed(2)}</td>
                <td>
                    <span class="status-badge ${pedido.estado_pago || 'pendiente'}">
                        ${pedido.estado_pago || 'pendiente'}
                    </span>
                </td>
                <td>${pedido.fecha_pedido || ''}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon ver-detalle" title="Ver detalle" data-pedido-id="${pedido.id_pedido}">
                            <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="btn-icon editar-estado" title="Cambiar estado" data-pedido-id="${pedido.id_pedido}">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                    </div>
                </td>
            `;

            tbodyPedidos.appendChild(fila);
        });

        // Event listeners a los botones
        document.querySelectorAll('.ver-detalle').forEach(btn => {
            btn.addEventListener('click', function () {
                const pedidoId = this.dataset.pedidoId;
                verDetallePedido(pedidoId);
            });
        });

        document.querySelectorAll('.editar-estado').forEach(btn => {
            btn.addEventListener('click', function () {
                const pedidoId = this.dataset.pedidoId;
                mostrarModalEstado(pedidoId);
            });
        });
    }

    function mostrarError(mensaje) {
        if (!tbodyPedidos) return;
        
        tbodyPedidos.innerHTML = `
            <tr>
                <td colspan="6" class="no-data">
                    <i class="fa-solid fa-exclamation-circle"></i>
                    <p>Error: ${mensaje}</p>
                    <button class="btn-reintentar" onclick="window.cargarPedidos()">
                        <i class="fa-solid fa-rotate"></i> Reintentar
                    </button>
                </td>
            </tr>
        `;
        if (tablaPedidosContainer) tablaPedidosContainer.style.display = 'block';
    }

    function aplicarFiltros() {
        filtrosActuales = {
            search: searchInput ? searchInput.value.trim() : '',
            estado: filtroEstado ? filtroEstado.value : '',
            fecha_inicio: filtroFechaInicio ? filtroFechaInicio.value : '',
            fecha_fin: filtroFechaFin ? filtroFechaFin.value : ''
        };
        cargarPedidos(filtrosActuales);
    }

    function limpiarFiltros() {
        if (searchInput) searchInput.value = '';
        if (filtroEstado) filtroEstado.value = '';
        if (filtroFechaInicio) filtroFechaInicio.value = '';
        if (filtroFechaFin) filtroFechaFin.value = '';
        filtrosActuales = {};
        cargarPedidos();
    }

    function actualizarContador(cantidad) {
       // contadorPedidos.textContent = `${cantidad} pedido${cantidad !== 1 ? 's' : ''}`;
    }

    function mostrarModalEstado(pedidoId) {
        const pedido = pedidos.find(p => p.id_pedido == pedidoId);
        if (pedido && modalEstado && estadoPedidoId && selectNuevoEstado) {
            pedidoSeleccionadoId = pedidoId;
            estadoPedidoId.textContent = pedido.numero_pedido || '#' + pedido.id_pedido;
            selectNuevoEstado.value = pedido.estado_pago || 'pendiente';
            modalEstado.style.display = 'block';
        }
    }

    function confirmarCambioEstado() {
        if (!pedidoSeleccionadoId) return;
        
        const nuevoEstado = selectNuevoEstado ? selectNuevoEstado.value : '';
        
        fetch('/api/admin/pedidos/estado', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pedido_id: pedidoSeleccionadoId,
                tipo_estado: 'pago',
                estado: nuevoEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacion(`Estado actualizado a ${nuevoEstado}`, 'success');
                cerrarModal(modalEstado);
                cargarPedidos(filtrosActuales);
            } else {
                throw new Error(data.error || 'Error al cambiar estado');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al cambiar estado: ' + error.message, 'error');
        });
    }

    function mostrarModalNuevoPaso1() {
        carritoTemporal = [];
        clienteSeleccionado = null;
        if (selectCliente) selectCliente.value = '';
        if (btnSiguientePaso) btnSiguientePaso.disabled = true;
        if (modalNuevoPaso1) modalNuevoPaso1.style.display = 'block';
    }

    function irAPaso2() {
        if (!clienteSeleccionado) {
            mostrarNotificacion('Debes seleccionar un cliente', 'error');
            return;
        }
        
        if (clienteSeleccionadoSpan) {
            clienteSeleccionadoSpan.textContent = `${clienteSeleccionado.username} (${clienteSeleccionado.email})`;
        }
        cerrarModal(modalNuevoPaso1);
        cargarProductosGrid();
        if (modalNuevoPaso2) modalNuevoPaso2.style.display = 'block';
    }

    function volverAPaso1() {
        cerrarModal(modalNuevoPaso2);
        limpiarCarritoTemporal();
        if (modalNuevoPaso1) modalNuevoPaso1.style.display = 'block';
    }

    function limpiarCarritoTemporal() {
        carritoTemporal = [];
        actualizarCarritoResumen();
    }

    function cargarProductosGrid() {
        if (!productosGrid) return;
        
        let productosFiltrados = [...productos];
        
        // Aplicar filtro de búsqueda
        if (buscarProducto && buscarProducto.value) {
            const termino = buscarProducto.value.toLowerCase();
            productosFiltrados = productosFiltrados.filter(p => 
                p.nombre.toLowerCase().includes(termino) || 
                (p.descripcion && p.descripcion.toLowerCase().includes(termino))
            );
        }
        
        // Aplicar filtro de categoría
        if (filtroCategoriaProducto && filtroCategoriaProducto.value) {
            const catId = parseInt(filtroCategoriaProducto.value);
            productosFiltrados = productosFiltrados.filter(p => p.categoria_id === catId);
        }
        
        if (productosFiltrados.length === 0) {
            productosGrid.innerHTML = '<p class="no-data">No hay productos disponibles</p>';
            return;
        }

        productosGrid.innerHTML = productosFiltrados.map(producto => {
            const enCarrito = carritoTemporal.find(item => item.id === producto.id);
            const sinStock = producto.stock === 0;
            
            return `
                <div class="producto-card ${enCarrito ? 'seleccionado' : ''} ${sinStock ? 'sin-stock' : ''}" 
                     data-id="${producto.id}" 
                     data-nombre="${producto.nombre}"
                     data-precio="${producto.precio}"
                     data-stock="${producto.stock}"
                     onclick="window.agregarAlCarritoTemporal(this, ${!sinStock})">
                    <img src="${producto.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${producto.nombre}" 
                         class="producto-imagen-mini"
                         onerror="this.src='/static/img/placeholder.jpg'">
                    <div class="producto-info">
                        <h4>${producto.nombre}</h4>
                        <p>${producto.descripcion ? producto.descripcion.substring(0, 50) + '...' : 'Sin descripción'}</p>
                        <p class="producto-precio">$${parseFloat(producto.precio).toFixed(2)}</p>
                        <p class="producto-stock ${producto.stock < 5 ? 'bajo' : ''}">
                            Stock: ${producto.stock}
                        </p>
                    </div>
                </div>
            `;
        }).join('');
    }

    function filtrarProductos() {
        cargarProductosGrid();
    }

    window.agregarAlCarritoTemporal = function(element, puedeAgregar) {
        if (!puedeAgregar) return;
        
        const productoId = parseInt(element.dataset.id);
        const producto = productos.find(p => p.id === productoId);
        
        if (!producto) return;
        
        const existente = carritoTemporal.findIndex(item => item.id === productoId);
        
        if (existente >= 0) {
            // Si ya existe, aumentar cantidad
            if (carritoTemporal[existente].cantidad < producto.stock) {
                carritoTemporal[existente].cantidad++;
            } else {
                mostrarNotificacion('No hay suficiente stock', 'error');
                return;
            }
        } else {
            // Si no existe, agregar nuevo
            carritoTemporal.push({
                id: producto.id,
                nombre: producto.nombre,
                precio: parseFloat(producto.precio),
                cantidad: 1,
                stock: producto.stock,
                imagen: producto.imagen
            });
        }
        
        actualizarCarritoResumen();
        cargarProductosGrid(); // Refrescar grid para actualizar clases
    };

    function actualizarCarritoResumen() {
        if (!carritoResumen || !carritoItems || !carritoTotal || !btnCrearPedido) return;
        
        if (carritoTemporal.length === 0) {
            carritoResumen.style.display = 'none';
            btnCrearPedido.disabled = true;
            return;
        }

        carritoResumen.style.display = 'block';
        btnCrearPedido.disabled = false;

        let total = 0;
        carritoItems.innerHTML = carritoTemporal.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            return `
                <div class="carrito-item-mini" data-id="${item.id}">
                    <div class="carrito-item-info">
                        <h5>${item.nombre}</h5>
                        <p>$${item.precio.toFixed(2)} c/u</p>
                    </div>
                    <div class="carrito-item-cantidad">
                        <button class="btn-icon" onclick="window.cambiarCantidad(${item.id}, -1)" ${item.cantidad <= 1 ? 'disabled' : ''}>
                            <i class="fa-solid fa-minus"></i>
                        </button>
                        <input type="number" value="${item.cantidad}" min="1" max="${item.stock}" 
                               onchange="window.cambiarCantidadInput(${item.id}, this.value)">
                        <button class="btn-icon" onclick="window.cambiarCantidad(${item.id}, 1)" ${item.cantidad >= item.stock ? 'disabled' : ''}>
                            <i class="fa-solid fa-plus"></i>
                        </button>
                        <button class="carrito-item-eliminar" onclick="window.eliminarDelCarritoTemporal(${item.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        carritoTotal.textContent = `$${total.toFixed(2)}`;
    }

    window.cambiarCantidad = function(productoId, delta) {
        const item = carritoTemporal.find(i => i.id === productoId);
        if (!item) return;
        
        const nuevaCantidad = item.cantidad + delta;
        if (nuevaCantidad < 1 || nuevaCantidad > item.stock) return;
        
        item.cantidad = nuevaCantidad;
        actualizarCarritoResumen();
        cargarProductosGrid();
    };

    window.cambiarCantidadInput = function(productoId, cantidad) {
        const item = carritoTemporal.find(i => i.id === productoId);
        if (!item) return;
        
        cantidad = parseInt(cantidad);
        if (isNaN(cantidad) || cantidad < 1) cantidad = 1;
        if (cantidad > item.stock) cantidad = item.stock;
        
        item.cantidad = cantidad;
        actualizarCarritoResumen();
        cargarProductosGrid();
    };

    window.eliminarDelCarritoTemporal = function(productoId) {
        carritoTemporal = carritoTemporal.filter(i => i.id !== productoId);
        actualizarCarritoResumen();
        cargarProductosGrid();
    };

    function crearPedido() {
        if (!clienteSeleccionado || carritoTemporal.length === 0) {
            mostrarNotificacion('Debes seleccionar productos', 'error');
            return;
        }

        const total = carritoTemporal.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
        
        const pedidoData = {
            usuario_id: clienteSeleccionado.id,
            items: carritoTemporal.map(item => ({
                producto_id: item.id,
                cantidad: item.cantidad,
                precio: item.precio
            })),
            total: total,
            metodo_pago: 'manual',
            estado: 'pendiente'
        };

        fetch('/api/pedidos/crear-manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(pedidoData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacion('Pedido creado exitosamente', 'success');
                cerrarModal(modalNuevoPaso2);
                cargarPedidos(filtrosActuales);
            } else {
                throw new Error(data.error || 'Error al crear pedido');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al crear pedido: ' + error.message, 'error');
        });
    }

    function verDetallePedido(pedidoId) {
        fetch(`/api/admin/pedidos/${pedidoId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarModalDetalle(data.pedido);
                } else {
                    throw new Error(data.error || 'Error al cargar detalle');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('Error al cargar el detalle: ' + error.message, 'error');
            });
    }

    function mostrarModalDetalle(pedido) {
        const modalNumeroPedido = document.getElementById('modalNumeroPedido');
        const modalBody = document.getElementById('modalBodyDetalle');

        if (!modalNumeroPedido || !modalBody) return;

        modalNumeroPedido.textContent = pedido.numero_pedido || '#' + pedido.id_pedido;

        let html = `
            <div class="detail-section">
                <h3 class="section-title">Información del Cliente</h3>
                <div class="detail-info">
                    <p><strong>Nombre:</strong> ${pedido.cliente?.nombre || 'Cliente'}</p>
                    <p><strong>Email:</strong> ${pedido.cliente?.email || ''}</p>
                    ${pedido.cliente?.telefono ? `<p><strong>Teléfono:</strong> ${pedido.cliente.telefono}</p>` : ''}
                </div>
            </div>
            
            <div class="detail-section">
                <h3 class="section-title">Detalles del Pedido</h3>
                <div class="detail-info">
                    <p><strong>Fecha:</strong> ${pedido.fecha_pedido || ''}</p>
                    <p><strong>Estado:</strong> <span class="status-badge ${pedido.estado_pago || 'pendiente'}">${pedido.estado_pago || 'pendiente'}</span></p>
                    <p><strong>Dirección de envío:</strong> ${pedido.direccion_envio || 'No especificada'}</p>
                    <p><strong>Método de pago:</strong> ${pedido.metodo_pago || 'No especificado'}</p>
                </div>
            </div>
            
            <div class="detail-section">
                <h3 class="section-title">Productos</h3>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Precio Unitario</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        if (pedido.items && pedido.items.length > 0) {
            pedido.items.forEach(item => {
                html += `
                    <tr>
                        <td>${item.producto_nombre || 'Producto'}</td>
                        <td>${item.cantidad || 0}</td>
                        <td>$${(item.precio_unitario || 0).toFixed(2)}</td>
                        <td>$${(item.total || 0).toFixed(2)}</td>
                    </tr>
                `;
            });
        } else {
            html += `
                <tr>
                    <td colspan="4" class="no-data">No hay productos en este pedido</td>
                </tr>
            `;
        }

        html += `
                        </tbody>
                    </table>
                </div>
                <div class="totals-section">
                    <p><strong>Total del pedido:</strong> $${(pedido.total || 0).toFixed(2)}</p>
                </div>
            </div>
        `;

        modalBody.innerHTML = html;
        if (modalDetalle) modalDetalle.style.display = 'block';
    }

    function mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.className = `notification-custom ${tipo}`;
        notificacion.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${mensaje}</span>
            </div>
        `;
        
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.parentNode.removeChild(notificacion);
                }
            }, 300);
        }, 3000);
    }

    // Hacer función global para reintentar
    window.cargarPedidos = cargarPedidos;
});