// app/static/js/productos.js

class ProductManager {
    constructor() {
        this.carrito = this.obtenerCarritoLocal();
    }

    // Cargar productos desde la API
    async cargarProductos(categoriaId = null) {
        try {
            let url = '/api/productos';
            if (categoriaId) {
                url = `/api/productos/${categoriaId}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.mostrarProductos(data.productos);
            } else {
                console.error('Error cargando productos:', data.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Mostrar productos en el HTML
    mostrarProductos(productos) {
        const container = document.getElementById('productos-container');
        if (!container) return;

        container.innerHTML = '';

        productos.forEach(producto => {
            const productCard = this.crearProductCard(producto);
            container.appendChild(productCard);
        });
    }

    // Crear tarjeta de producto
    crearProductCard(producto) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';

        col.innerHTML = `
            <div class="card product-card h-100">
                <img src="${producto.imagen || '/static/images/placeholder.jpg'}" 
                     class="card-img-top" 
                     alt="${producto.nombre}"
                     style="height: 200px; object-fit: cover;">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${producto.nombre}</h5>
                    <p class="card-text flex-grow-1">${producto.descripcion || 'Sin descripción'}</p>
                    <div class="mt-auto">
                        <p class="card-text">
                            <strong>Precio: $${producto.precio.toFixed(2)}</strong>
                        </p>
                        <p class="card-text">
                            <small class="text-muted">Stock: ${producto.stock}</small>
                        </p>
                        <button class="btn btn-primary btn-agregar-carrito" 
                                data-producto-id="${producto.id}"
                                ${producto.stock === 0 ? 'disabled' : ''}>
                            ${producto.stock === 0 ? 'Sin Stock' : 'Agregar al Carrito'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Agregar evento al botón
        const btn = col.querySelector('.btn-agregar-carrito');
        if (btn && producto.stock > 0) {
            btn.addEventListener('click', () => this.agregarAlCarrito(producto));
        }

        return col;
    }

    // Agregar producto al carrito
    async agregarAlCarrito(producto) {
        try {
            const response = await fetch('/api/carrito/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    producto_id: producto.id,
                    cantidad: 1
                })
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarMensaje('Producto agregado al carrito', 'success');
                this.actualizarContadorCarrito();
            } else {
                this.mostrarMensaje(data.error || 'Error al agregar al carrito', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarMensaje('Error de conexión', 'error');
        }
    }

    // Mostrar mensajes
    mostrarMensaje(mensaje, tipo) {
        // Implementar toast o alert según tu diseño
        alert(mensaje); // Temporal - puedes usar un toast mejor
    }

    // Actualizar contador del carrito
    actualizarContadorCarrito() {
        const contador = document.getElementById('carrito-contador');
        if (contador) {
            this.carrito = this.obtenerCarritoLocal();
            contador.textContent = this.carrito.length;
            contador.style.display = this.carrito.length > 0 ? 'inline' : 'none';
        }
    }

    // Obtener carrito del localStorage (temporal)
    obtenerCarritoLocal() {
        return JSON.parse(localStorage.getItem('carrito')) || [];
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const productManager = new ProductManager();
    
    // Cargar productos según la página
    const path = window.location.pathname;
    
    if (path.includes('accesorios')) {
        productManager.cargarProductos(1); // ID de categoría para accesorios
    } else if (path.includes('juegos')) {
        productManager.cargarProductos(2); // ID de categoría para juegos
    } else if (path.includes('consolas')) {
        productManager.cargarProductos(3); // ID de categoría para consolas
    } else if (path.includes('controles')) {
        productManager.cargarProductos(4); // ID de categoría para controles
    } else {
        productManager.cargarProductos(); // Todos los productos
    }
});