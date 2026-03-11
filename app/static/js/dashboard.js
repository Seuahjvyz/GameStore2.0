// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    console.log(' Inicializando Dashboard...');
    
    // Cargar todas las gráficas
    cargarResumenEstadisticas();
    cargarProductosMasVendidos();
    cargarVentasPorMes();
    
    // Configurar actualización automática cada 5 minutos
    setInterval(() => {
        console.log('Actualizando dashboard...');
        cargarResumenEstadisticas();
        cargarProductosMasVendidos();
        cargarVentasPorMes();
    }, 5 * 60 * 1000);
});

// Función para cargar el resumen de estadísticas
function cargarResumenEstadisticas() {
    fetch('/api/admin/estadisticas/resumen')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarResumen(data.resumen);
            }
        })
        .catch(error => console.error('Error cargando resumen:', error));
}

// Función para cargar productos más vendidos
function cargarProductosMasVendidos() {
    fetch('/api/admin/estadisticas/productos-mas-vendidos?limite=8')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarProductosMasVendidos(data.productos, data.total_ingresos);
            }
        })
        .catch(error => console.error('Error cargando productos:', error));
}

// Función para mostrar la gráfica de productos más vendidos
function mostrarProductosMasVendidos(productos, totalIngresos) {
    const container = document.getElementById('grafica-productos');
    if (!container) return;
    
    // Limpiar container
    container.innerHTML = '';
    
    // Crear título
    const titulo = document.createElement('h2');
    titulo.textContent = 'Productos Más Vendidos';
    titulo.style.marginBottom = '20px';
    titulo.style.color = 'white';
    container.appendChild(titulo);
    
    if (productos.length === 0) {
        container.innerHTML += '<p class="no-data">No hay datos de ventas disponibles</p>';
        return;
    }
    
    // Crear grid de productos
    const grid = document.createElement('div');
    grid.className = 'productos-top-grid';
    
    productos.forEach((producto, index) => {
        const porcentaje = ((producto.total_ingresos / totalIngresos) * 100).toFixed(1);
        
        const card = document.createElement('div');
        card.className = 'producto-top-card';
        card.innerHTML = `
            <div class="producto-top-posicion">#${index + 1}</div>
            <img src="${producto.imagen}" alt="${producto.nombre}" class="producto-top-imagen">
            <div class="producto-top-info">
                <h4>${producto.nombre}</h4>
                <div class="producto-top-stats">
                    <span class="producto-top-cantidad">
                        <i class="fa-solid fa-cube"></i> ${producto.total_vendido} uds
                    </span>
                    <span class="producto-top-ingresos">
                        $${producto.total_ingresos.toFixed(2)}
                    </span>
                </div>
                <div class="producto-top-barra">
                    <div class="producto-top-barra-progreso" style="width: ${porcentaje}%"></div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    
    container.appendChild(grid);
    
    // Crear canvas para gráfica de barras
    const canvasContainer = document.createElement('div');
    canvasContainer.style.marginTop = '30px';
    canvasContainer.style.height = '300px';
    
    const canvas = document.createElement('canvas');
    canvas.id = 'chart-productos-vendidos';
    canvasContainer.appendChild(canvas);
    container.appendChild(canvasContainer);
    
    // Crear gráfica de barras
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: productos.map(p => p.nombre.length > 15 ? p.nombre.substring(0, 15) + '...' : p.nombre),
            datasets: [{
                label: 'Unidades vendidas',
                data: productos.map(p => p.total_vendido),
                backgroundColor: 'rgba(92, 246, 177, 0.7)',
                borderColor: '#5cf67d',
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const producto = productos[context.dataIndex];
                            return [
                                `Ingresos: $${producto.total_ingresos.toFixed(2)}`,
                                `Participación: ${((producto.total_ingresos / totalIngresos) * 100).toFixed(1)}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#a0a0a0' }
                },
                x: {
                    grid: { display: false },
                    ticks: { 
                        color: '#a0a0a0',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Función para cargar ventas por mes
function cargarVentasPorMes() {
    fetch('/api/admin/estadisticas/ventas-por-mes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarVentasPorMes(data.labels, data.datos);
            }
        })
        .catch(error => console.error('Error cargando ventas:', error));
}

// Función para mostrar gráfica de ventas por mes
function mostrarVentasPorMes(labels, datos) {
    const container = document.getElementById('grafica-ventas-mes');
    
    // Si no existe el contenedor, crearlo
    if (!container) {
        const contenido = document.querySelector('.contenido');
        const nuevoContainer = document.createElement('div');
        nuevoContainer.id = 'grafica-ventas-mes';
        nuevoContainer.style.marginTop = '40px';
        nuevoContainer.style.height = '300px';
        
        // Insertar después de la gráfica de productos
        const graficaProductos = document.getElementById('grafica-productos');
        if (graficaProductos) {
            graficaProductos.insertAdjacentElement('afterend', nuevoContainer);
        } else {
            contenido.appendChild(nuevoContainer);
        }
        
        // Crear título
        const titulo = document.createElement('h2');
        titulo.textContent = 'Ventas por Mes';
        titulo.style.marginBottom = '20px';
        titulo.style.color = 'white';
        nuevoContainer.appendChild(titulo);
        
        // Crear canvas
        const canvas = document.createElement('canvas');
        canvas.id = 'chart-ventas-mes';
        nuevoContainer.appendChild(canvas);
        
        renderizarGraficaVentas(canvas, labels, datos);
    } else {
        const canvas = document.getElementById('chart-ventas-mes');
        if (canvas) {
            renderizarGraficaVentas(canvas, labels, datos);
        }
    }
}

function renderizarGraficaVentas(canvas, labels, datos) {
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas',
                data: datos,
                borderColor: '#f44040',
                backgroundColor: '#f65c5c',
                borderWidth: 3,
                pointBackgroundColor: '#f72c2c',
                pointBorderColor: 'white',
                pointRadius: 5,
                pointHoverRadius: 7,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                        color: '#a0a0a0',
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a0a0' }
                }
            }
        }
    });
}