class AdminInventario {
    constructor() {
        this.productos = [];
        this.categorias = [];
        this.init();
    }

    async init() {
        await this.cargarCategorias();
        await this.cargarProductos();
        this.initEventListeners();
        this.actualizarEstadisticas();
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/api/categorias');
            const data = await response.json();
            
            if (data.success) {
                this.categorias = data.categorias;
                this.actualizarSelectCategorias();
            }
        } catch (error) {
            console.error('Error cargando categorías:', error);
        }
    }

    async cargarProductos(filtros = {}) {
        try {
            let url = '/api/admin/productos';
            const params = new URLSearchParams();
            
            if (filtros.search) params.append('search', filtros.search);
            if (filtros.categoria) params.append('categoria', filtros.categoria);
            if (filtros.estado) params.append('estado', filtros.estado);
            
            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.productos = data.productos;
                this.mostrarProductos();
                this.actualizarEstadisticas();
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            this.mostrarError('Error al cargar los productos');
        }
    }

    mostrarProductos() {
        const tbody = document.getElementById('productos-body');
        
        if (this.productos.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-data">
                        <i class="fa-solid fa-box-open"></i>
                        <p>No se encontraron productos</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.productos.map(producto => `
            <tr data-id="${producto.id}">
                <td class="producto-imagen">
                    <img src="${producto.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${producto.nombre}"
                         onerror="this.src='/static/img/placeholder.jpg'">
                </td>
                <td class="producto-nombre">
                    <strong>${producto.nombre}</strong>
                    <small>${producto.descripcion || 'Sin descripción'}</small>
                </td>
                <td class="producto-categoria">${producto.categoria}</td>
                <td class="producto-precio">$${parseFloat(producto.precio).toFixed(2)}</td>
                <td class="producto-stock">
                    <span class="stock-badge ${producto.stock < 10 ? 'bajo' : producto.stock < 20 ? 'medio' : 'alto'}">
                        ${producto.stock}
                    </span>
                </td>
                <td class="producto-estado">
                    <span class="estado-badge ${producto.activo ? 'activo' : 'inactivo'}">
                        ${producto.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="producto-acciones">
                    <button class="btn-editar" onclick="adminInventario.editarProducto(${producto.id})">
                        <i class="fa-solid fa-edit"></i> Editar
                    </button>
                    <button class="btn-${producto.activo ? 'desactivar' : 'activar'}" 
                            onclick="adminInventario.toggleEstado(${producto.id}, ${!producto.activo})">
                        <i class="fa-solid fa-${producto.activo ? 'eye-slash' : 'eye'}"></i>
                        ${producto.activo ? 'Desactivar' : 'Activar'}
                    </button>
                    <button class="btn-eliminar" onclick="adminInventario.eliminarProducto(${producto.id})">
                        <i class="fa-solid fa-trash"></i> Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    }

    actualizarEstadisticas() {
        const total = this.productos.length;
        const activos = this.productos.filter(p => p.activo).length;
        const inactivos = total - activos;
        const stockBajo = this.productos.filter(p => p.stock < 10).length;

        document.getElementById('total-productos').textContent = total;
        document.getElementById('productos-activos').textContent = activos;
        document.getElementById('productos-inactivos').textContent = inactivos;
        document.getElementById('stock-bajo').textContent = stockBajo;
    }

    actualizarSelectCategorias() {
        const selectCategoria = document.getElementById('producto-categoria');
        const filtroCategoria = document.getElementById('filtro-categoria');
        
        const options = '<option value="">Seleccionar categoría</option>' +
            this.categorias.map(cat => 
                `<option value="${cat.id}">${cat.nombre}</option>`
            ).join('');
        
        selectCategoria.innerHTML = options;
        filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>' + 
            this.categorias.map(cat => 
                `<option value="${cat.id}">${cat.nombre}</option>`
            ).join('');
    }

    initEventListeners() {
    console.log('🔄 Inicializando event listeners...');
    
    // Esperar a que el DOM esté completamente listo
    setTimeout(() => {
        // Botón agregar producto
        const btnAgregar = document.getElementById('btn-agregar-producto');
        console.log('🔘 Botón agregar producto encontrado:', btnAgregar);
        
        if (btnAgregar) {
            btnAgregar.addEventListener('click', () => {
                console.log('🎯 Click en agregar producto');
                this.mostrarModal();
            });
        } else {
            console.error('❌ No se encontró el botón btn-agregar-producto. Buscando en el DOM...');
            // Buscar alternativas
            const alternativeBtn = document.querySelector('[onclick*="openAddProductModal"]') || 
                                 document.querySelector('.btn-primary') ||
                                 document.querySelector('button');
            console.log('🔍 Botón alternativo encontrado:', alternativeBtn);
        }

        // Buscador
        const searchBtn = document.getElementById('search-btn-admin');
        const searchInput = document.getElementById('search-admin');
        
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => {
                this.aplicarFiltros();
            });

            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.aplicarFiltros();
                }
            });
        } else {
            console.warn('⚠️ Elementos de búsqueda no encontrados');
        }

        // Filtros
        const filtroCategoria = document.getElementById('filtro-categoria');
        const filtroEstado = document.getElementById('filtro-estado');
        
        if (filtroCategoria) {
            filtroCategoria.addEventListener('change', () => {
                this.aplicarFiltros();
            });
        }
        
        if (filtroEstado) {
            filtroEstado.addEventListener('change', () => {
                this.aplicarFiltros();
            });
        }

        // Modal
        const modalCerrar = document.getElementById('modal-cerrar');
        const btnCancelar = document.getElementById('btn-cancelar');
        const formProducto = document.getElementById('form-producto');
        
        if (modalCerrar) {
            modalCerrar.addEventListener('click', () => {
                this.ocultarModal();
            });
        }
        
        if (btnCancelar) {
            btnCancelar.addEventListener('click', () => {
                this.ocultarModal();
            });
        }
        
        if (formProducto) {
            formProducto.addEventListener('submit', (e) => {
                e.preventDefault();
                this.guardarProducto();
            });
        }

        // Subida de imágenes
        const btnSubirImagen = document.getElementById('btn-subir-imagen');
        const inputImagenFile = document.getElementById('producto-imagen-file');
        const inputImagen = document.getElementById('producto-imagen');
        
        if (btnSubirImagen && inputImagenFile) {
            btnSubirImagen.addEventListener('click', () => {
                inputImagenFile.click();
            });

            inputImagenFile.addEventListener('change', (e) => {
                this.subirImagen(e.target.files[0]);
            });
        }
        
        if (inputImagen) {
            inputImagen.addEventListener('input', (e) => {
                this.mostrarVistaPrevia(e.target.value);
            });
        }

        // Limpiar stock cero
        const btnLimpiarStock = document.getElementById('btn-limpiar-stock');
        if (btnLimpiarStock) {
            btnLimpiarStock.addEventListener('click', () => {
                this.limpiarStockCero();
            });
        }

        console.log('✅ Event listeners inicializados correctamente');
    }, 100);
}



    aplicarFiltros() {
        const search = document.getElementById('search-admin').value;
        const categoria = document.getElementById('filtro-categoria').value;
        const estado = document.getElementById('filtro-estado').value;

        this.cargarProductos({ search, categoria, estado });
    }

    mostrarModal(producto = null) {
        const modal = document.getElementById('modal-producto');
        const titulo = document.getElementById('modal-titulo');
        const form = document.getElementById('form-producto');
        
        if (producto) {
            titulo.textContent = 'Editar Producto';
            this.cargarDatosFormulario(producto);
        } else {
            titulo.textContent = 'Agregar Producto';
            form.reset();
            document.getElementById('producto-id').value = '';
        }
        
        modal.style.display = 'block';
    }

    ocultarModal() {
        document.getElementById('modal-producto').style.display = 'none';
    }

    cargarDatosFormulario(producto) {
        document.getElementById('producto-id').value = producto.id;
        document.getElementById('producto-nombre').value = producto.nombre;
        document.getElementById('producto-descripcion').value = producto.descripcion || '';
        document.getElementById('producto-precio').value = parseFloat(producto.precio).toFixed(2);
        document.getElementById('producto-stock').value = producto.stock;
        document.getElementById('producto-categoria').value = producto.categoria_id;
        document.getElementById('producto-imagen').value = producto.imagen || '';
        document.getElementById('producto-activo').checked = producto.activo;
    }

    async guardarProducto() {
    const formData = {
        id: document.getElementById('producto-id').value || null,
        nombre: document.getElementById('producto-nombre').value,
        descripcion: document.getElementById('producto-descripcion').value,
        precio: parseFloat(document.getElementById('producto-precio').value),
        stock: parseInt(document.getElementById('producto-stock').value),
        categoria_id: parseInt(document.getElementById('producto-categoria').value),
        imagen: document.getElementById('producto-imagen').value,
        activo: document.getElementById('producto-activo').checked
    };

    // Validaciones
    if (!formData.nombre || formData.nombre.trim() === '') {
        this.mostrarNotificacion('El nombre del producto es requerido', 'error');
        return;
    }

    if (!formData.precio || formData.precio <= 0) {
        this.mostrarNotificacion('El precio debe ser mayor a 0', 'error');
        return;
    }

    if (formData.stock < 0) {
        this.mostrarNotificacion('El stock no puede ser negativo', 'error');
        return;
    }

    if (!formData.categoria_id) {
        this.mostrarNotificacion('Debe seleccionar una categoría', 'error');
        return;
    }

    // ✅ PREVENIR ACTIVACIÓN CON STOCK 0
    if (formData.activo && formData.stock === 0) {
        this.mostrarNotificacion('No se puede activar un producto con stock 0', 'error');
        return;
    }

    try {
        const url = formData.id ? '/api/admin/productos/editar' : '/api/admin/productos/agregar';
        const method = formData.id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            this.mostrarNotificacion(
                formData.id ? 'Producto actualizado correctamente' : 'Producto agregado correctamente',
                'success'
            );
            this.ocultarModal();
            await this.cargarProductos();
        } else {
            this.mostrarNotificacion(data.error, 'error');
        }
    } catch (error) {
        console.error('Error guardando producto:', error);
        this.mostrarNotificacion('Error al guardar el producto', 'error');
    }
}

    async editarProducto(id) {
        const producto = this.productos.find(p => p.id === id);
        if (producto) {
            this.mostrarModal(producto);
        }
    }

    async toggleEstado(id, nuevoEstado) {
        try {
            const response = await fetch('/api/admin/productos/estado', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    activo: nuevoEstado
                })
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion(
                    nuevoEstado ? 'Producto activado correctamente' : 'Producto desactivado correctamente',
                    'success'
                );
                await this.cargarProductos();
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('Error cambiando estado:', error);
            this.mostrarNotificacion('Error al cambiar el estado', 'error');
        }
    }

    async eliminarProducto(id) {
        if (!confirm('¿Estás seguro de que quieres eliminar este producto? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/productos/eliminar/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion('Producto eliminado correctamente', 'success');
                await this.cargarProductos();
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('Error eliminando producto:', error);
            this.mostrarNotificacion('Error al eliminar el producto', 'error');
        }
    }

    mostrarNotificacion(mensaje, tipo) {
        // Implementar sistema de notificaciones similar al que ya tienes
        const notificacion = document.createElement('div');
        notificacion.className = `notification-custom ${tipo}`;
        notificacion.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid fa-${tipo === 'success' ? 'check' : 'exclamation'}"></i>
                <span>${mensaje}</span>
            </div>
        `;
        
        document.body.appendChild(notificacion);
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.parentNode.removeChild(notificacion);
            }
        }, 3000);
    }

    mostrarError(mensaje) {
        this.mostrarNotificacion(mensaje, 'error');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.adminInventario = new AdminInventario();
});