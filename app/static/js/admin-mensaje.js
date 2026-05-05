// static/js/admin-mensajes.js
document.addEventListener('DOMContentLoaded', function() {
    console.log(' admin-mensajes.js cargado correctamente');
    
    let mensajesActuales = [];
    let mensajeSeleccionado = null;
    
    const tbody = document.getElementById('mensajes-body');
    const buscar = document.getElementById('buscar');
    const filtroLeido = document.getElementById('filtro-leido');
    const filtroRespondido = document.getElementById('filtro-respondido');
    const fechaDesde = document.getElementById('fecha-desde');
    const fechaHasta = document.getElementById('fecha-hasta');
    const btnLimpiar = document.getElementById('btn-limpiar');
    const searchBtn = document.getElementById('search-btn');
    
    // Todos los filtros automáticos
    const autoFilters = document.querySelectorAll('.auto-filter');
    
    // Modales
    const modalMensaje = document.getElementById('modal-mensaje');
    const modalBody = document.getElementById('modal-body-content');
    
    // Verificar que todos los elementos existan
    console.log('Elementos del DOM:', {
        tbody: !!tbody,
        buscar: !!buscar,
        filtroLeido: !!filtroLeido,
        filtroRespondido: !!filtroRespondido,
        fechaDesde: !!fechaDesde,
        fechaHasta: !!fechaHasta,
        btnLimpiar: !!btnLimpiar,
        searchBtn: !!searchBtn,
        modalMensaje: !!modalMensaje,
        modalBody: !!modalBody
    });
    
    if (!tbody) {
        console.error(' No se encontró el elemento tbody');
        return;
    }
    
    // Cargar mensajes iniciales
    cargarMensajes();
    
    // Event listeners para filtros automáticos
    autoFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            console.log('Filtro cambiado:', this.id, this.value);
            cargarMensajes();
        });
    });
    
    // Búsqueda con botón
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            console.log('Botón búsqueda clickeado');
            cargarMensajes();
        });
    }
    
    // Búsqueda con Enter
    if (buscar) {
        buscar.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('⏎ Enter presionado en búsqueda');
                cargarMensajes();
            }
        });
    }
    
    // Botón limpiar
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', function() {
            console.log(' Botón limpiar clickeado');
            limpiarFiltros();
        });
    }
    
    // Cerrar modales
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            console.log(' Cerrando modal');
            if (modalMensaje) modalMensaje.style.display = 'none';
        });
    });
    
    // Setup keyboard navigation for message modal
    setupModalKeyboardNav(modalMensaje);
    setupModalClickOutside(modalMensaje);
    setupModalCloseButtons(modalMensaje, ['.close-modal', '.btn-secondary']);
    
    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', (e) => {
        if (e.target === modalMensaje) {
            console.log(' Clic fuera del modal');
            modalMensaje.style.display = 'none';
        }
    });
    
    function limpiarFiltros() {
        if (buscar) buscar.value = '';
        if (filtroLeido) filtroLeido.value = '';
        if (filtroRespondido) filtroRespondido.value = '';
        if (fechaDesde) fechaDesde.value = '';
        if (fechaHasta) fechaHasta.value = '';
        cargarMensajes();
    }
    
    async function cargarMensajes() {
        try {
            console.log('Cargando mensajes...');
            if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="text-center">Cargando mensajes...</td></tr>';
            
            const params = new URLSearchParams();
            if (buscar && buscar.value) params.append('search', buscar.value);
            if (filtroLeido && filtroLeido.value !== '') params.append('leido', filtroLeido.value);
            if (filtroRespondido && filtroRespondido.value !== '') params.append('respondido', filtroRespondido.value);
            if (fechaDesde && fechaDesde.value) params.append('fecha_desde', fechaDesde.value);
            if (fechaHasta && fechaHasta.value) params.append('fecha_hasta', fechaHasta.value);
            
            console.log('Fetching con params:', params.toString());
            const response = await fetch(`/api/admin/contacto/mensajes?${params}`);
            const data = await response.json();
            
            console.log('Respuesta:', data);
            
            if (data.success) {
                mensajesActuales = data.mensajes;
                actualizarEstadisticas(data.stats);
                renderizarTabla(data.mensajes);
            } else {
                if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center error">Error: ${data.error}</td></tr>`;
            }
        } catch (error) {
            console.error('Error:', error);
            if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="text-center error">Error al cargar mensajes</td></tr>';
        }
    }
    
    function actualizarEstadisticas(stats) {
        const totalEl = document.getElementById('total-mensajes');
        const noLeidosEl = document.getElementById('no-leidos');
        const noRespondidosEl = document.getElementById('no-respondidos');
        
        if (totalEl) totalEl.textContent = stats.total || 0;
        if (noLeidosEl) noLeidosEl.textContent = stats.no_leidos || 0;
        if (noRespondidosEl) noRespondidosEl.textContent = stats.no_respondidos || 0;
        
        console.log('Estadísticas actualizadas:', stats);
    }
    
    function renderizarTabla(mensajes) {
        if (!tbody) return;
        
        console.log('Renderizando tabla con', mensajes.length, 'mensajes');
        
        if (mensajes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No hay mensajes</td></tr>';
            return;
        }
        
        let html = '';
        mensajes.forEach(m => {
            const estadoLeido = m.leido ? 'Leído' : 'No leído';
            const estadoRespondido = m.respondido ? 'Respondido' : 'No respondido';
            
            html += `
                <tr class="${!m.leido ? 'no-leido' : ''}">
                    <td>#${m.id}</td>
                    <td>${m.fecha_envio || 'N/A'}</td>
                    <td>${escapeHtml(m.nombre)}</td>
                    <td>${escapeHtml(m.email)}</td>
                    <td>${escapeHtml(m.asunto)}</td>
                    <td>
                        <span class="estado-leido">${estadoLeido}</span><br>
                        <span class="estado-respondido">${estadoRespondido}</span>
                    </td>
                    <td>
                        <button onclick="verDetalle(event, ${m.id})" class="btn-small btn-primary">Ver</button>
                        <button onclick="eliminarMensaje(event, ${m.id})" class="btn-small btn-danger">Eliminar</button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    window.verDetalle = async function(event, mensajeId) {
        event.stopPropagation();
        console.log('Ver detalle de mensaje ID:', mensajeId);
        
        try {
            const response = await fetch(`/api/admin/contacto/mensajes/${mensajeId}`);
            const data = await response.json();
            
            console.log(' Detalle del mensaje:', data);
            
            if (data.success) {
                mensajeSeleccionado = data.mensaje;
                mostrarDetalle(mensajeSeleccionado);
                if (modalMensaje) {
                    modalMensaje.style.display = 'flex';
                    console.log('Modal abierto');
                }
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cargar detalle');
        }
    };
    
    function mostrarDetalle(m) {
        if (!modalBody) return;
        
        const telefono = m.telefono ? escapeHtml(m.telefono) : 'No proporcionado';
        const mensajeTexto = escapeHtml(m.mensaje).replace(/\n/g, '<br>');
        
        modalBody.innerHTML = `
            <div class="detalle-mensaje">
                <p><strong>ID:</strong> #${m.id}</p>
                <p><strong>Fecha:</strong> ${m.fecha_envio || 'N/A'}</p>
                <p><strong>Nombre:</strong> ${escapeHtml(m.nombre)}</p>
                <p><strong>Email:</strong> <a href="mailto:${escapeHtml(m.email)}" style="color: #8b5cf6;">${escapeHtml(m.email)}</a></p>
                <p><strong>Teléfono:</strong> ${telefono}</p>
                <p><strong>Asunto:</strong> ${escapeHtml(m.asunto)}</p>
                <p><strong>Estado:</strong> ${m.leido ? 'Leído' : ' No leído'} | ${m.respondido ? 'Respondido' : ' No respondido'}</p>
                <hr style="border-color: #3a3a3a;">
                <p><strong>Mensaje:</strong></p>
                <div class="mensaje-texto">${mensajeTexto}</div>
            </div>
        `;
        
        const marcarLeido = document.getElementById('marcar-leido');
        const marcarRespondido = document.getElementById('marcar-respondido');
        const eliminarBtn = document.getElementById('eliminar-mensaje');
        
        if (marcarLeido) {
            marcarLeido.onclick = () => cambiarEstado('leido', !m.leido);
        }
        if (marcarRespondido) {
            marcarRespondido.onclick = () => cambiarEstado('respondido', !m.respondido);
        }
        if (eliminarBtn) {
            eliminarBtn.onclick = () => eliminarMensaje(null, m.id);
        }
    }
    
    async function cambiarEstado(tipo, valor) {
        if (!mensajeSeleccionado) return;
        
        console.log(`Cambiando estado ${tipo} a ${valor} para mensaje ${mensajeSeleccionado.id}`);
        
        try {
            const response = await fetch(`/api/admin/contacto/mensajes/${mensajeSeleccionado.id}/estado`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({[tipo]: valor})
            });
            
            const data = await response.json();
            
            if (data.success) {
                mensajeSeleccionado[tipo] = valor;
                mostrarDetalle(mensajeSeleccionado);
                cargarMensajes();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error(' Error:', error);
            alert('Error al actualizar estado');
        }
    }
    
    window.eliminarMensaje = async function(event, mensajeId) {
        if (event) event.stopPropagation();
        
        console.log('Eliminando mensaje ID:', mensajeId);
        
        if (!confirm('¿Estás seguro de eliminar este mensaje? Esta acción no se puede deshacer.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/admin/contacto/mensajes/${mensajeId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (modalMensaje) modalMensaje.style.display = 'none';
                cargarMensajes();
                alert(' Mensaje eliminado correctamente');
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar mensaje');
        }
    };
});