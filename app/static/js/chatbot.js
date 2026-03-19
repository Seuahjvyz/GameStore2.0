// chatbot.js - Versión con diagnóstico de enlaces

$(document).ready(function() {
    console.log("✅ Chatbot JS cargado");
    
    const btnChatbot = $('#btn-chatbot');
    const ventanaChatbot = $('#ventana-chatbot');
    const btnCerrar = $('#btn-cerrar-chatbot');
    const btnEnviar = $('#btn-enviar-mensaje-chatbot');
    const inputMensaje = $('#mensaje-input-chatbot');
    const contenedorMensajes = $('#mensajes-chatbot');
    
    let esperandoRespuesta = false;
    
    cargarHistorial();
    
    function cargarHistorial() {
        fetch('/chatbot/api/chat/historial')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.historial.length > 0) {
                    contenedorMensajes.empty();
                    data.historial.forEach(msg => {
                        if (msg.rol === 'user') {
                            agregarMensajeUsuario(msg.contenido, msg.hora);
                        } else {
                            agregarMensajeBot(msg.contenido, msg.hora);
                        }
                    });
                } else {
                    fetch('/chatbot/api/user-info')
                        .then(res => res.json())
                        .then(userData => {
                            if (userData.logged_in) {
                                agregarMensajeBot(`¡Hola ${userData.user.username}! 😊 Bienvenido a Game Store. ¿En qué puedo ayudarte?`);
                            } else {
                                agregarMensajeBot('¡Hola! 😊 Bienvenido a Game Store. ¿En qué puedo ayudarte?');
                            }
                        });
                }
            });
    }
    
    btnChatbot.on('click', function() {
        ventanaChatbot.removeClass('ventana-oculto-chatbot').addClass('ventana-visible-chatbot');
    });
    
    btnCerrar.on('click', function() {
        ventanaChatbot.removeClass('ventana-visible-chatbot').addClass('ventana-oculto-chatbot');
    });
    
    inputMensaje.on('keypress', function(e) {
        if (e.which === 13 && !esperandoRespuesta) {
            enviarMensaje();
        }
    });
    
    btnEnviar.on('click', function() {
        if (!esperandoRespuesta) {
            enviarMensaje();
        }
    });
    
    function enviarMensaje() {
        const mensaje = inputMensaje.val().trim();
        
        if (mensaje === '' || esperandoRespuesta) return;
        
        agregarMensajeUsuario(mensaje);
        inputMensaje.val('');
        mostrarEscribiendo();
        
        fetch('/chatbot/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: mensaje })
        })
        .then(response => response.json())
        .then(data => {
            quitarEscribiendo();
            if (data.success) {
                agregarMensajeBot(data.respuesta);
            } else {
                agregarMensajeBot('Lo siento, tuve un problema. 😕');
            }
        })
        .catch(error => {
            quitarEscribiendo();
            agregarMensajeBot('Error de conexión. 🌐');
            console.error('Error:', error);
        });
    }
    
    function agregarMensajeUsuario(mensaje, hora = null) {
        const horaActual = hora || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const mensajeHTML = `
            <div class="mensaje mensaje-usuario">
                <div class="mensaje-contenido">
                    ${escapeHTML(mensaje)}
                    <span class="mensaje-hora">${horaActual}</span>
                </div>
            </div>
        `;
        contenedorMensajes.append(mensajeHTML);
        scrollToBottom();
    }
    
    function agregarMensajeBot(mensaje, hora = null) {
        const horaActual = hora || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // 🔍 DIAGNÓSTICO: Ver el mensaje original
        console.log("📨 Mensaje original del bot:", mensaje);
        
        const mensajeFormateado = formatearMensaje(mensaje);
        
        // 🔍 DIAGNÓSTICO: Ver el mensaje después de formatear
        console.log("🎨 Mensaje formateado:", mensajeFormateado);
        
        const mensajeHTML = `
            <div class="mensaje mensaje-bot">
                <div class="mensaje-contenido bot">
                    ${mensajeFormateado}
                    <span class="mensaje-hora">${horaActual}</span>
                </div>
            </div>
        `;
        contenedorMensajes.append(mensajeHTML);
        scrollToBottom();
    }
    
    function formatearMensaje(texto) {
        if (!texto) return '';
        
        console.log("🔧 Formateando mensaje...");
        
        // Escapar HTML primero para evitar inyecciones
        let text = escapeHTML(texto);
        
        // 1. Convertir URLs completas (https://...) a enlaces
        text = text.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #8b5cf6; text-decoration: underline; font-weight: 500;">$1</a>');
        
        // 2. 🔥 CONVERTIR RUTAS RELATIVAS (/algo) A ENLACES - VERSIÓN SIMPLE 🔥
        // Busca cualquier palabra que empiece con / y que pueda tener letras, números, guiones
        text = text.replace(/\/[a-zA-Z0-9\-_]+/g, function(match) {
            console.log("🔗 Ruta encontrada:", match);
            return `<a href="${match}" style="color: #8b5cf6; text-decoration: underline; font-weight: 500; cursor: pointer;" onclick="event.preventDefault(); window.location.href='${match}';">${match}</a>`;
        });
        
        // 3. Convertir saltos de línea a <br>
        text = text.replace(/\n/g, '<br>');
        
        // 4. Formatear precios en negrita ($123)
        text = text.replace(/\$(\d+(?:[.,]\d+)?)/g, '<strong>$$$1</strong>');
        
        return text;
    }
    
    function mostrarEscribiendo() {
        esperandoRespuesta = true;
        const escribiendoHTML = `
            <div class="mensaje mensaje-bot" id="escribiendo-indicador">
                <div class="mensaje-contenido bot">
                    <div class="escribiendo"><span></span><span></span><span></span></div>
                </div>
            </div>
        `;
        contenedorMensajes.append(escribiendoHTML);
        scrollToBottom();
    }
    
    function quitarEscribiendo() {
        $('#escribiendo-indicador').remove();
        esperandoRespuesta = false;
    }
    
    function scrollToBottom() {
        contenedorMensajes.scrollTop(contenedorMensajes[0].scrollHeight);
    }
    
    function escapeHTML(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    window.limpiarChat = function() {
        if (confirm('¿Limpiar conversación?')) {
            fetch('/chatbot/api/chat/limpiar', { method: 'POST' })
                .then(() => {
                    contenedorMensajes.empty();
                    agregarMensajeBot('Conversación reiniciada.');
                });
        }
    };
});