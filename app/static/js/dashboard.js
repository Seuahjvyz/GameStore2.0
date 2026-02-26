// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Inicializando Dashboard...');
    
    // Cargar todas las gráficas
    cargarResumenEstadisticas();
    cargarProductosMasVendidos();
    cargarVentasPorMes();
    
    // Configurar actualización automática cada 5 minutos
    setInterval(() => {
        console.log('🔄 Actualizando dashboard...');
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

// Función para mostrar las tarjetas de resumen
function mostrarResumen(resumen) {
    // Crear contenedor si no existe
    let resumenContainer = document.getElementById('resumen-estadisticas');
    
    if (!resumenContainer) {
        // Insertar después del h1
        const contenido = document.querySelector('.contenido');
        const h1 = contenido.querySelector('h1');
        
        resumenContainer = document.createElement('div');
        resumenContainer.id = 'resumen-estadisticas';
        resumenContainer.className = 'resumen-cards';
        
        h1.insertAdjacentElement('afterend', resumenContainer);
    }
    
    // Formatear moneda
    const formatter = new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2
    });
    
    resumenContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: #3b82f6;">
                <i class="fa-solid fa-box"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.total_productos}</span>
                <span class="stat-label">Productos</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">
                <i class="fa-solid fa-users"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.total_usuarios}</span>
                <span class="stat-label">Clientes</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(236, 72, 153, 0.1); color: #ec4899;">
                <i class="fa-solid fa-shopping-cart"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.total_pedidos}</span>
                <span class="stat-label">Pedidos</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(34, 197, 94, 0.1); color: #22c55e;">
                <i class="fa-solid fa-check-circle"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.pedidos_completados}</span>
                <span class="stat-label">Completados</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.1); color: #f59e0b;">
                <i class="fa-solid fa-clock"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.pedidos_pendientes}</span>
                <span class="stat-label">Pendientes</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1); color: #ef4444;">
                <i class="fa-solid fa-times-circle"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.pedidos_cancelados}</span>
                <span class="stat-label">Cancelados</span>
            </div>
        </div>
        
        <div class="stat-card stat-card-large">
            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.1); color: #10b981;">
                <i class="fa-solid fa-chart-line"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${formatter.format(resumen.ventas_semana)}</span>
                <span class="stat-label">Ventas (7 días)</span>
            </div>
        </div>
        
        <div class="stat-card stat-card-large">
            <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">
                <i class="fa-solid fa-calendar"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${formatter.format(resumen.ventas_mes)}</span>
                <span class="stat-label">Ventas del mes</span>
            </div>
        </div>
        
        <div class="stat-card stat-card-large">
            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.1); color: #f59e0b;">
                <i class="fa-solid fa-calendar-alt"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${formatter.format(resumen.ventas_ano)}</span>
                <span class="stat-label">Ventas del año</span>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1); color: #ef4444;">
                <i class="fa-solid fa-exclamation-triangle"></i>
            </div>
            <div class="stat-info">
                <span class="stat-value">${resumen.stock_bajo}</span>
                <span class="stat-label">Stock bajo</span>
            </div>
        </div>
    `;
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
                <span class="producto-top-porcentaje">${porcentaje}% de ingresos</span>
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
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: '#8b5cf6',
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
        nuevoContainer.style.height = '400px';
        
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
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                pointBackgroundColor: '#8b5cf6',
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