document.addEventListener('DOMContentLoaded', function () {

    const configComun = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    font: {
                        size: 12,
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                    },
                    padding: 15,
                    color: '#333'
                }
            }
        }
    };

    fetch('/Gio/Front-end/views/admin/estadisticas_citas.php')
        .then(response => response.json())
        .then(data => {

            const ctxCanceladas = document.getElementById('grafica-productos');
            if (!ctxCanceladas) {
                console.log('Gráfica 1: Canvas no encontrado');
                return;
            }

            new Chart(ctxCanceladas, {
                type: 'bar',
                data: {
                    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                    datasets: [{
                        label: 'Citas Canceladas',
                        data: Array.from({ length: 12 }, (_, i) => data.canceladas[i + 1] ?? 0),
                        backgroundColor: 'rgba(220, 53, 69, 0.6)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 2,
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    ...configComun,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                padding: 8,
                                font: { size: 11 }
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                padding: 10,
                                font: { size: 12 }
                            }
                        }
                    },
                    plugins: {
                        ...configComun.plugins,
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: { size: 13 },
                            bodyFont: { size: 13 },
                            padding: 10
                        }
                    }
                }
            });

            console.log('Gráfica 1: Citas Canceladas - CARGADA CON DATOS REALES');
        })
        .catch(error => {
            console.error('Error al cargar estadísticas:', error);
        });
});
