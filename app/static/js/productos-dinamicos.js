const ProductosController = {
    // Inicializar el controlador
    init: function () {
        console.log('🎮 Inicializando ProductosController...');
        this.cargarProductos();
        this.agregarEventListenersGlobales(); // Esta función debe existir
    },

    // Cargar productos desde la API
    cargarProductos: function () {
        console.log('📥 Iniciando carga de productos...');

        // Mostrar loading
        this.mostrarLoading();

        // Determinar la categoría actual desde la URL
        const categoria = this.obtenerCategoriaActual();
        const url = categoria ? `/api/productos?categoria=${encodeURIComponent(categoria)}` : '/api/productos';

        console.log(`📡 Solicitando productos desde: ${url}`);

        fetch(url)
            .then(response => {
                console.log('✅ Respuesta recibida, status:', response.status);
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('📊 Datos completos recibidos:', data);

                if (!data) {
                    console.error('❌ data es null o undefined');
                    this.mostrarError('No se recibieron datos del servidor');
                    return;
                }

                if (!data.success) {
                    console.error('❌ success es false:', data.error);
                    this.mostrarError(data.error || 'Error en BD');
                    return;
                }

                const productos = data.productos;
                console.log(`🔍 ${productos.length} productos extraídos`);

                if (!productos) {
                    console.error('❌ data.productos no existe');
                    this.mostrarError('Formato de datos incorrecto');
                    return;
                }

                if (!Array.isArray(productos)) {
                    console.error('❌ productos no es un array:', typeof productos, productos);
                    this.mostrarError('Error en formato de productos');
                    return;
                }

                console.log(`🎯 ${productos.length} productos listos para mostrar`);

                if (productos.length === 0) {
                    this.mostrarMensaje('No hay productos disponibles en esta categoría');
                    return;
                }

                this.mostrarProductos(productos);
            })
            .catch(error => {
                console.error('❌ Error en cargarProductos:', error);
                this.mostrarError('Error al cargar los productos: ' + error.message);
            });
    },

    // Obtener categoría actual desde la URL
    obtenerCategoriaActual: function () {
        const path = window.location.pathname;
        console.log(`📍 Ruta actual: ${path}`);
        
        if (path.includes('/juegos')) return 'Juegos';
        if (path.includes('/consolas')) return 'Consolas';
        if (path.includes('/controles')) return 'Controles';
        if (path.includes('/accesorios')) return 'Accesorios';
        if (path.includes('/')) return null;
        
        console.log('No se detectó categoría específica, cargando todos los productos');
        return null;
    },

    mostrarProductos: function (productos) {
        try {
            console.log('🎨 Mostrando productos...');
            const container = document.getElementById('productos-container');

            if (!container) {
                console.error('❌ No se encontró el container con id "productos-container"');
                return;
            }

            if (productos.length === 0) {
                container.innerHTML = `
                    <div class="no-products">
                        <i class="fa-solid fa-box-open"></i>
                        <h3>No hay productos disponibles</h3>
                        <p>Pronto agregaremos nuevos productos a esta categoría</p>
                    </div>
                `;
                return;
            }

            // Generar HTML para cada producto
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
                    
                    ${producto.stock > 0 ? 
                        `<button class="btn-agregar-carrito" 
                                data-id="${producto.id}">
                            <i class="fa-solid fa-cart-arrow-down"></i>Agregar al Carrito
                        </button>` :
                        `<button class="btn-sin-stock" disabled>
                            <i class="fa-solid fa-times"></i>Sin Stock
                        </button>`
                    }
                </div>
            `).join('');

            console.log('✅ Productos renderizados correctamente');
            this.agregarEventListeners();

            // Sincronizar favoritos después de renderizar
            setTimeout(() => {
                if (window.favoritosManager) {
                    window.favoritosManager.marcarFavoritosExistentes();
                }
            }, 500);

        } catch (error) {
            console.error('❌ Error en mostrarProductos:', error);
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
                this.agregarAlCarrito(productoId, boton);
            });
        });
    },

    // Agregar event listeners globales - FUNCIÓN QUE FALTABA
    agregarEventListenersGlobales: function () {
        console.log('🌍 Agregando event listeners globales...');
        
        // Buscador global si existe
        const buscador = document.getElementById('btn-buscar');
        const buscarInput = document.getElementById('buscar-input');
        
        if (buscador && buscarInput) {
            buscador.addEventListener('click', () => {
                this.buscarProductos(buscarInput.value);
            });
            
            buscarInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.buscarProductos(buscarInput.value);
                }
            });
        }
        
        // Filtros de categoría si existen
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

    // Función de búsqueda
    buscarProductos: function(termino) {
        if (!termino || termino.trim() === '') {
            this.cargarProductos();
            return;
        }
        
        console.log(`🔍 Buscando: ${termino}`);
        this.mostrarLoading();
        
        // Aquí puedes implementar la búsqueda si tu API la soporta
        // Por ahora recargamos todos y filtramos en el cliente
        this.cargarProductos();
    },

    // Filtrar productos por categoría
    filtrarPorCategoria: function (categoriaId) {
        console.log(`🎯 Filtrando por categoría ID: ${categoriaId}`);
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
                console.error('❌ Error filtrando productos:', error);
                this.mostrarError('Error al filtrar productos');
            });
    },

    // Agregar producto al carrito - CORREGIDO
    agregarAlCarrito: function (productoId, button) {
        console.log(`🛒 Intentando agregar producto ${productoId} al carrito`);
        
        // Verificar autenticación de manera más robusta
        this.verificarAutenticacion()
            .then(autenticado => {
                if (!autenticado) {
                    return;
                }

                if (button && button.disabled) {
                    console.log('⏳ Botón ya en proceso, ignorando click');
                    return;
                }

                console.log(`✅ Usuario autenticado, procediendo con producto ${productoId}`);

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
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('📨 Respuesta del servidor:', data);
                    
                    if (button) {
                        button.disabled = false;
                        const tieneStock = data.success && !data.error?.includes('Stock insuficiente');
                        if (tieneStock) {
                            button.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> AGREGAR AL CARRITO';
                        } else {
                            button.innerHTML = 'SIN STOCK';
                            button.disabled = true;
                        }
                    }
                    
                    if (data.success) {
                        this.mostrarNotificacion(data.message || 'Producto agregado al carrito');
                        this.actualizarContadorCarrito(data.carrito_count);
                    } else {
                        this.mostrarNotificacion(data.error || 'Error al agregar al carrito', 'error');
                    }
                })
                .catch(error => {
                    console.error('❌ Error agregando al carrito:', error);
                    this.mostrarNotificacion('Error de conexión al servidor', 'error');
                    
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> AGREGAR AL CARRITO';
                    }
                });
            })
            .catch(error => {
                console.error('❌ Error verificando autenticación:', error);
                this.mostrarNotificacion('Error al verificar autenticación', 'error');
            });
    },

    // Verificar autenticación de manera más robusta
    verificarAutenticacion: function() {
        return new Promise((resolve) => {
            // Primero verificar si hay sesión en localStorage/sessionStorage
            if (localStorage.getItem('user_id') || sessionStorage.getItem('user_id')) {
                resolve(true);
                return;
            }
            
            // Si no, hacer una llamada a la API para verificar
            fetch('/api/user-info')
                .then(response => response.json())
                .then(data => {
                    resolve(data.logged_in || false);
                })
                .catch(() => {
                    resolve(false);
                });
        });
    },

    actualizarContadorCarrito: function (count) {
        if (window.actualizarContadorCarrito) {
            window.actualizarContadorCarrito(count);
        } else {
            const contador = document.querySelector('.carrito-count');
            if (contador) {
                contador.textContent = count;
                contador.style.display = count > 0 ? 'inline' : 'none';
            }
        }
    },

    mostrarNotificacion: function (mensaje, tipo = 'success') {
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion ${tipo}`;
        notificacion.innerHTML = `
            <div class="notificacion-contenido">
                <i class="fa-solid fa-${tipo === 'success' ? 'check' : 'exclamation-triangle'}"></i>
                <span>${mensaje}</span>
            </div>
        `;

        notificacion.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${tipo === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            animation: fadeIn 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;

        document.body.appendChild(notificacion);

        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.parentNode.removeChild(notificacion);
            }
        }, 3000);
    },

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

    mostrarError: function (mensaje) {
        console.error('❌ Mostrando error:', mensaje);
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="error">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <h3>¡Ocurrió un error!</h3>
                    <p>${mensaje}</p>
                    <button onclick="ProductosController.cargarProductos()" class="btn-reintentar">
                        <i class="fa-solid fa-refresh"></i> Reintentar
                    </button>
                </div>
            `;
        }
    },

    mostrarMensaje: function (mensaje) {
        console.log('ℹ️ Mostrando mensaje:', mensaje);
        const container = document.getElementById('productos-container');
        if (container) {
            container.innerHTML = `
                <div class="info-message">
                    <i class="fa-solid fa-info-circle"></i>
                    <h3>Información</h3>
                    <p>${mensaje}</p>
                </div>
            `;
        }
    }
};

// Inicializar cuando el DOM esté listo - CORREGIDO
document.addEventListener('DOMContentLoaded', function () {
    console.log('📄 DOM cargado, inicializando ProductosController...');
    // Esperar un poco para evitar conflictos con otros scripts
    setTimeout(() => {
        ProductosController.init();
    }, 100);
});

// Evitar inicialización múltiple
if (window.ProductosControllerInicializado) {
    console.log('⚠️ ProductosController ya fue inicializado');
} else {
    window.ProductosControllerInicializado = true;
    window.ProductosController = ProductosController;
}

console.log('✅ productos-dinamicos.js cargado correctamente');