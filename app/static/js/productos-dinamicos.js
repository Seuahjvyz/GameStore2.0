// Script para cargar productos dinámicamente desde la API
class ProductosController {
    constructor() {
        this.apiUrl = '/api/productos';
        this.currentCategory = this.getCurrentCategory();
        this.init();
    }

    init() {
        this.cargarProductos();
        this.agregarEventListenersGlobales();
        this.actualizarContadorCarrito();
    }

    getCurrentCategory() {
        const path = window.location.pathname;
        if (path.includes('/juegos')) return 'Juegos';
        if (path.includes('/accesorios')) return 'Accesorios';
        if (path.includes('/consolas')) return 'Consolas';
        if (path.includes('/controles')) return 'Controles';
        return 'Todos';
    }

    async cargarProductos() {
        try {
            const container = document.getElementById('productos-container');
            if (!container) return;

            container.innerHTML = `
                <div class="loading">
                    <i class="fa-solid fa-spinner fa-spin"></i> Cargando productos...
                </div>
            `;

            let url = this.apiUrl;
            if (this.currentCategory !== 'Todos') {
                url += `?categoria=${encodeURIComponent(this.currentCategory)}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Error al cargar productos');

            const productos = await response.json();

            if (productos.length === 0) {
                container.innerHTML = `
                    <div class="no-products">
                        <i class="fa-solid fa-box-open"></i>
                        <p>No hay productos disponibles en esta categoría</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = productos.map(producto => this.crearProductoHTML(producto)).join('');
            this.agregarEventListeners();

        } catch (error) {
            console.error('Error:', error);
            const container = document.getElementById('productos-container');
            if (container) {
                container.innerHTML = `
                    <div class="error">
                        <i class="fa-solid fa-exclamation-triangle"></i>
                        <p>Error al cargar los productos</p>
                    </div>
                `;
            }
        }
    }

    crearProductoHTML(producto) {
        return `
            <div class="producto" data-producto-id="${producto.id_producto}">
                <div class="imagenes_producto">
                    <img class="imagen_producto" src="${producto.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${producto.nombre}" onerror="this.src='/static/img/placeholder.jpg'">
                </div>
                <h3 class="product-title">${producto.nombre}</h3>
                <p class="product-category">${producto.nombre_categoria}</p>
                <div class="product-price-section">
                    <span class="product-price">$${parseFloat(producto.precio).toLocaleString('es-MX', {minimumFractionDigits: 2})}</span>
                </div>
                <button class="btn_carrito" data-producto-id="${producto.id_producto}">
                    <i class="fa-solid fa-cart-shopping"></i> Añadir al Carrito
                </button>
            </div>
        `;
    }

    agregarEventListeners() {
        document.querySelectorAll('.btn_carrito').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const productoId = e.target.closest('.btn_carrito').dataset.productoId;
                this.agregarAlCarrito(productoId);
            });
        });
    }

    agregarEventListenersGlobales() {
        // Filtros en index
        document.querySelectorAll('.filtro-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoria = e.target.dataset.categoria;
                this.filtrarProductos(categoria);
            });
        });

        // Búsqueda
        const btnBuscar = document.getElementById('btn-buscar');
        const inputBuscar = document.getElementById('buscar-input');
        
        if (btnBuscar && inputBuscar) {
            btnBuscar.addEventListener('click', () => this.buscarProductos());
            inputBuscar.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.buscarProductos();
            });
        }
    }

    async filtrarProductos(categoria) {
        try {
            const container = document.getElementById('productos-container');
            if (!container) return;

            container.innerHTML = `
                <div class="loading">
                    <i class="fa-solid fa-spinner fa-spin"></i> Cargando productos...
                </div>
            `;

            const response = await fetch(`/api/productos?categoria=${encodeURIComponent(categoria)}`);
            if (!response.ok) throw new Error('Error al filtrar productos');

            const productos = await response.json();
            container.innerHTML = productos.map(producto => this.crearProductoHTML(producto)).join('');
            
            this.agregarEventListeners();

            // Actualizar botones activos
            document.querySelectorAll('.filtro-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');

        } catch (error) {
            console.error('Error:', error);
        }
    }

    async buscarProductos() {
        const termino = document.getElementById('buscar-input').value.trim();
        if (!termino) return;

        try {
            const container = document.getElementById('productos-container');
            if (!container) return;

            container.innerHTML = `
                <div class="loading">
                    <i class="fa-solid fa-spinner fa-spin"></i> Buscando productos...
                </div>
            `;

            const response = await fetch(`/api/productos?buscar=${encodeURIComponent(termino)}`);
            if (!response.ok) throw new Error('Error en la búsqueda');

            const productos = await response.json();
            
            if (productos.length === 0) {
                container.innerHTML = `
                    <div class="no-products">
                        <i class="fa-solid fa-search"></i>
                        <p>No se encontraron productos para "${termino}"</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = productos.map(producto => this.crearProductoHTML(producto)).join('');
            this.agregarEventListeners();

        } catch (error) {
            console.error('Error:', error);
        }
    }

    async agregarAlCarrito(productoId) {
        try {
            const carritoResponse = await fetch('/api/carrito/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    producto_id: parseInt(productoId),
                    cantidad: 1
                })
            });

            if (carritoResponse.ok) {
                this.mostrarNotificacion('Producto agregado al carrito', 'success');
                this.actualizarContadorCarrito();
            } else if (carritoResponse.status === 401) {
                // No autenticado - redirigir al login
                window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
            } else {
                throw new Error('Error al agregar al carrito');
            }

        } catch (error) {
            console.error('Error:', error);
            this.mostrarNotificacion('Error al agregar al carrito', 'error');
        }
    }

    mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion ${tipo}`;
        notificacion.innerHTML = `
            <i class="fa-solid fa-${tipo === 'success' ? 'check' : 'exclamation'}"></i>
            <span>${mensaje}</span>
        `;

        document.body.appendChild(notificacion);

        setTimeout(() => {
            notificacion.remove();
        }, 3000);
    }

    async actualizarContadorCarrito() {
        try {
            const response = await fetch('/api/carrito/cantidad');
            if (response.ok) {
                const data = await response.json();
                const contadores = document.querySelectorAll('.carrito-count');
                contadores.forEach(contador => {
                    contador.textContent = data.cantidad;
                });
            }
        } catch (error) {
            console.error('Error al actualizar contador:', error);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ProductosController();
});