const ProductosController = {
    // Inicializar el controlador
    init: function () {
        console.log('Inicializando ProductosController...');
        this.cargarProductos();
        this.agregarEventListenersGlobales();
    },

    // Cargar productos desde la API
    cargarProductos: function () {
        console.log('Iniciando carga de productos...');

        // Mostrar loading
        this.mostrarLoading();

        // Determinar la categoría actual desde la URL
        const categoria = this.obtenerCategoriaActual();
        const url = categoria ? `/api/productos?categoria=${categoria}` : '/api/productos';

        console.log(`📡 Solicitando productos desde: ${url}`);

        fetch(url)
            .then(response => {
                console.log(' Respuesta recibida, status:', response.status);
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Datos completos recibidos:', data);

                if (!data) {
                    console.error(' data es null o undefined');
                    this.mostrarError('No se recibieron datos del servidor');
                    return;
                }

                if (!data.success) {
                    console.error(' success es false:', data.error);
                    this.mostrarError(data.error || 'Error en BD');
                    return;
                }

                const productos = data.productos;
                console.log('🔍 Productos extraídos:', productos);

                if (!productos) {
                    console.error(' data.productos no existe');
                    this.mostrarError('Formato de datos incorrecto');
                    return;
                }

                if (!Array.isArray(productos)) {
                    console.error(' productos no es un array:', typeof productos, productos);
                    this.mostrarError('Error en formato de productos');
                    return;
                }

                console.log(` ${productos.length} productos listos para mostrar`);

                if (productos.length === 0) {
                    this.mostrarMensaje('No hay productos disponibles en este momento');
                    return;
                }

                this.mostrarProductos(productos);
            })
            .catch(error => {
                console.error(' Error en cargarProductos:', error);
                this.mostrarError('Error al cargar los productos: ' + error.message);
            });
    },

    // Obtener categoría actual desde la URL
    obtenerCategoriaActual: function () {
        const path = window.location.pathname;
        if (path.includes('/juegos')) return 'Juegos';
        if (path.includes('/consolas')) return 'Consolas';
        if (path.includes('/controles')) return 'Controles';
        if (path.includes('/accesorios')) return 'Accesorios';
        return null;
    },

    mostrarProductos: function (productos) {
        try {
            console.log('🎨 Mostrando productos...');
            const container = document.getElementById('productos-container');

            if (!container) {
                console.error(' No se encontró el container con id "productos-container"');
                return;
            }

            if (productos.length === 0) {
                container.innerHTML = '<div class="error">No hay productos disponibles</div>';
                return;
            }

            // Generar HTML para cada producto CON BOTÓN DE FAVORITOS
            container.innerHTML = productos.map(producto => `
                <div class="producto" data-id="${producto.id}">
                    <button class="favorito-btn" 
                            data-product-id="${producto.id}">
                        <i class="fa-regular fa-heart"></i>
                    </button>
                    
                    <img src="${producto.imagen}" alt="${producto.nombre}" 
                         onerror="this.src='/static/img/placeholder.jpg'">
                    <h3>${producto.nombre}</h3>
                    <p class="categoria">${producto.categoria}</p>
                    <p class="descripcion">${producto.descripcion}</p>
                    <p class="precio">$${typeof producto.precio === 'number' ? producto.precio.toFixed(2) : '0.00'}</p>
                    <button class="btn-agregar-carrito" 
                            data-id="${producto.id}"
                            ${producto.stock === 0 ? 'disabled' : ''}>
                        ${producto.stock === 0 ? 'Sin Stock' : '<i class="fa-solid fa-cart-shopping"></i>Agregar al Carrito'}
                    </button>
                </div>
            `).join('');

            console.log('Productos renderizados correctamente');
            this.agregarEventListeners();

            // Sincronizar favoritos después de renderizar
            setTimeout(() => {
                if (window.favoritosManager) {
                    window.favoritosManager.marcarFavoritosExistentes();
                }
            }, 500);

        } catch (error) {
            console.error(' Error en mostrarProductos:', error);
            this.mostrarError('Error al mostrar los productos');
        }
    },

    // Agregar event listeners a los botones
agregarEventListeners: function () {
    const botones = document.querySelectorAll('.btn-agregar-carrito');
    console.log(`🔘 Agregando listeners a ${botones.length} botones`);

    botones.forEach(boton => {
        boton.addEventListener('click', (e) => {
            e.preventDefault();
            const productoId = boton.getAttribute('data-id');
            console.log(`🖱️ Click en botón para producto ${productoId}`);
            this.agregarAlCarrito(productoId, boton); // Pasar el botón como parámetro
        });
    });
},

    // Agregar event listeners globales
    agregarEventListenersGlobales: function () {
        // Listeners para filtros de categoría si existen
        const filtrosCategoria = document.querySelectorAll('.filtro-categoria');
        if (filtrosCategoria.length > 0) {
            filtrosCategoria.forEach(filtro => {
                filtro.addEventListener('click', (e) => {
                    e.preventDefault();
                    const categoriaId = filtro.getAttribute('data-categoria-id');
                    this.filtrarPorCategoria(categoriaId);
                });
            });
        }
    },

    // Filtrar productos por categoría
    filtrarPorCategoria: function (categoriaId) {
        console.log(` Filtrando por categoría: ${categoriaId}`);

        this.mostrarLoading();

        fetch(`/api/productos/categoria/${categoriaId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && Array.isArray(data.productos)) {
                    this.mostrarProductos(data.productos);
                } else {
                    this.mostrarError('Error al filtrar productos');
                }
            })
            .catch(error => {
                console.error('Error filtrando productos:', error);
                this.mostrarError('Error al filtrar productos');
            });
    },


    // Agregar producto al carrito
agregarAlCarrito: function (productoId, button) {

    if (!this.estaAutenticado()) {
        this.mostrarNotificacion('Inicia sesión para poder agregar productos al carrito', 'error');
        return;
    }


    // Si se pasa el botón, prevenir múltiples clicks
    if (button && button.disabled) {
        console.log('⏳ Botón ya en proceso, ignorando click');
        return;
    }
    
    console.log(`🛒 Agregando producto ${productoId} al carrito`);

    // Guardar el texto original del botón
    let originalText = '';
    if (button) {
        originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AGREGANDO...';
    }

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
        console.log('📨 Respuesta del servidor:', data);
        
        // ✅ IMPORTANTE: Restaurar el botón independientemente del resultado
        if (button) {
            button.disabled = false;
            // Verificar si el producto sigue teniendo stock
            const tieneStock = data.success && !data.error?.includes('Stock insuficiente');
            if (tieneStock) {
                button.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> AGREGAR AL CARRITO';
            } else {
                button.innerHTML = 'SIN STOCK';
                button.disabled = true;
            }
        }
        
        if (data.success) {
            this.mostrarNotificacion(data.message);
            this.actualizarContadorCarrito(data.carrito_count);
        } else {
            this.mostrarError(data.error || 'Error al agregar al carrito');
        }
    })
    .catch(error => {
        console.error('❌ Error agregando al carrito:', error);
        this.mostrarError('Error de conexión');
        
        // ✅ RESTAURAR BOTÓN EN CASO DE ERROR TAMBIÉN
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> AGREGAR AL CARRITO';
        }
    });
},

    // Actualizar contador del carrito
actualizarContadorCarrito: function (count) {
    if (window.actualizarContadorCarrito) {
        window.actualizarContadorCarrito(count);
    } else {
        // Fallback
        const contador = document.querySelector('.carrito-count');
        if (contador) {
            contador.textContent = count;
            contador.style.display = count > 0 ? 'inline' : 'none';
        }
    }
},

    // Mostrar notificación
    mostrarNotificacion: function (mensaje) {
        // Crear notificación temporal
        const notificacion = document.createElement('div');
        notificacion.className = 'notificacion';
        notificacion.innerHTML = `
            <div class="notificacion-contenido">
                <span>${mensaje}</span>
            </div>
        `;

        // Estilos básicos para la notificación
        notificacion.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            animation: fadeIn 0.3s;
        `;

        document.body.appendChild(notificacion);

        // Remover después de 3 segundos
        setTimeout(() => {
            notificacion.remove();
        }, 3000);
    },

    // Mostrar estado de loading
    mostrarLoading: function () {
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="loading">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    <p>Cargando productos...</p>
                </div>
            `;
        }
    },

    // Mostrar mensaje de error
    mostrarError: function (mensaje) {
        console.error(' Mostrando error:', mensaje);
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="error">
                    <h3> Ocurrió un error</h3>
                    <p>${mensaje}</p>
                    <button onclick="ProductosController.cargarProductos()" class="btn-reintentar">
                        Reintentar
                    </button>
                </div>
            `;
        }
    },

    // Mostrar mensaje informativo
    mostrarMensaje: function (mensaje) {
        console.log(' Mostrando mensaje:', mensaje);
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="info-message">
                    <h3>Información</h3>
                    <p>${mensaje}</p>
                </div>
            `;
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    console.log(' DOM cargado, inicializando ProductosController...');
    ProductosController.init();
});

// También inicializar si el DOM ya está listo (para cargas posteriores)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        ProductosController.init();
    });
} else {
    ProductosController.init();
}

// Hacer disponible globalmente para debugging
window.ProductosController = ProductosController;
console.log(' productos-dinamicos.js cargado correctamente');