// app/static/js/productos-dinamicos.js
class ProductosDinamicos {
    constructor() {
        this.init();
    }

    async init() {
        // Determinar categoría según la página
        const categoriaId = this.obtenerCategoriaId();
        await this.cargarProductos(categoriaId);
    }

    obtenerCategoriaId() {
        const path = window.location.pathname;
        if (path.includes('accesorios')) return 1;
        if (path.includes('juegos')) return 2;
        if (path.includes('consolas')) return 3;
        if (path.includes('controles')) return 4;
        return null; // Todos los productos
    }

    async cargarProductos(categoriaId = null) {
        try {
            let url = '/api/productos';
            if (categoriaId) {
                url = `/api/productos/categoria/${categoriaId}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.mostrarProductos(data.productos);
            } else {
                this.mostrarError('Error cargando productos: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error de conexión al cargar productos');
        }
    }

    mostrarProductos(productos) {
        const container = document.getElementById('productos-container');
        if (!container) return;

        if (productos.length === 0) {
            container.innerHTML = `
                <div class="no-products">
                    <i class="fa-solid fa-box-open"></i>
                    <h3>No hay productos disponibles</h3>
                    <p>Pronto agregaremos nuevos productos</p>
                </div>
            `;
            return;
        }

        container.innerHTML = productos.map(producto => this.crearProductoHTML(producto)).join('');
    }

    crearProductoHTML(producto) {
        return `
            <div class="producto" data-producto-id="${producto.id}">
                <div class="imagenes_producto">
                    <img class="imagen_producto" 
                         src="${producto.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${producto.nombre}"
                         onerror="this.src='/static/img/placeholder.jpg'">
                </div>
                <h3 class="product-title">${this.formatearNombre(producto.nombre)}</h3>
                <p class="product-category">${producto.categoria || 'Accesorios'}</p>
                <div class="product-price-section">
                    <span class="product-price">$${this.formatearPrecio(producto.precio)}</span>
                </div>
                <button class="btn_carrito" 
                        data-producto-id="${producto.id}"
                        ${producto.stock === 0 ? 'disabled' : ''}>
                    <i class="fa-solid fa-cart-shopping"></i> 
                    ${producto.stock === 0 ? 'Sin Stock' : 'Añadir al Carrito'}
                </button>
            </div>
        `;
    }

    formatearNombre(nombre) {
        // Convertir a mayúsculas como en tu diseño
        return nombre.toUpperCase();
    }

    formatearPrecio(precio) {
        return new Intl.NumberFormat('es-MX', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(precio);
    }

    mostrarError(mensaje) {
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="error-container">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <h3>Error</h3>
                    <p>${mensaje}</p>
                    <button onclick="window.location.reload()">Reintentar</button>
                </div>
            `;
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ProductosDinamicos();
});