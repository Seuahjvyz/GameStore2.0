// static/js/chatbot.js - Versión para Groq

$(document).ready(function() {
    console.log("✅ Chatbot JS cargado (versión Groq)");
    
    // Elementos del DOM
    const btnChatbot = $('#btn-chatbot');
    const ventanaChatbot = $('#ventana-chatbot');
    const btnCerrar = $('#btn-cerrar-chatbot');
    const btnEnviar = $('#btn-enviar-mensaje-chatbot');
    const inputMensaje = $('#mensaje-input-chatbot');
    const contenedorMensajes = $('#mensajes-chatbot');
    
    // Estado del chatbot
    let esperandoRespuesta = false;
    let usuarioLogueado = false;
    let nombreUsuario = 'Usuario';
    let modeloActual = 'llama3-70b-8192';
    
    // Cargar historial al iniciar
    cargarHistorial();
    verificarSesion();
    
    // Cargar modelos disponibles
    fetch('/chatbot/api/chat/modelos')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('📚 Modelos disponibles:', data.modelos);
            }
        });
    
    function verificarSesion() {
        fetch('/chatbot/api/user-info')
            .then(res => res.json())
            .then(data => {
                usuarioLogueado = data.logged_in;
                if (usuarioLogueado) {
                    nombreUsuario = data.user.username;
                }
            })
            .catch(() => console.log("⚠️ No se pudo verificar sesión"));
    }
    
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
                }
            })
            .catch(() => console.log("⚠️ No se pudo cargar historial"));
    }
    
    // Mostrar/ocultar chatbot
    btnChatbot.on('click', function() {
        ventanaChatbot.removeClass('ventana-oculto-chatbot').addClass('ventana-visible-chatbot');
        
        // Si no hay mensajes, mostrar bienvenida
        if (contenedorMensajes.children().length === 0) {
            const saludo = usuarioLogueado 
                ? `¡Hola ${nombreUsuario}! 😊 Soy el asistente de Game Store. ¿En qué puedo ayudarte?`
                : '¡Hola! 😊 Soy el asistente de Game Store. ¿En qué puedo ayudarte?';
            agregarMensajeBot(saludo);
        }
    });
    
    btnCerrar.on('click', function() {
        ventanaChatbot.removeClass('ventana-visible-chatbot').addClass('ventana-oculto-chatbot');
    });
    
    // Enviar mensaje con Enter
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
        
        // Agregar mensaje del usuario
        agregarMensajeUsuario(mensaje);
        
        // Limpiar input
        inputMensaje.val('');
        
        // Mostrar indicador de escritura
        mostrarEscribiendo();
        
        // Enviar a Groq
        fetch('/chatbot/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mensaje: mensaje,
                modelo: modeloActual
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            quitarEscribiendo();
            
            if (data.success) {
                agregarMensajeBot(data.respuesta);
                console.log(`🤖 Modelo usado: ${data.modelo}`);
            } else {
                agregarMensajeBot('Lo siento, tuve un problema. Por favor intenta de nuevo. 😕');
            }
        })
        .catch(error => {
            quitarEscribiendo();
            agregarMensajeBot('Error de conexión. Verifica tu internet e intenta de nuevo. 🌐');
            console.error('Error:', error);
        });
    }
    
    function agregarMensajeUsuario(mensaje, hora = null) {
        const horaActual = hora || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const mensajeHTML = `
            <div class="mensaje mensaje-usuario">
                <div class="mensaje-contenido">
                    <p>${escapeHTML(mensaje)}</p>
                    <span class="mensaje-hora">${horaActual}</span>
                </div>
            </div>
        `;
        contenedorMensajes.append(mensajeHTML);
        scrollToBottom();
    }
    
    function agregarMensajeBot(mensaje, hora = null) {
        const horaActual = hora || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Procesar enlaces en la respuesta
        let mensajeFormateado = formatearMensaje(mensaje);
        
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
        // Escapar HTML primero
        let text = escapeHTML(texto);
        
        // Convertir URLs en enlaces clickeables
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="chat-link">$1</a>');
        
        // Convertir saltos de línea
        text = text.replace(/\n/g, '<br>');
        
        // Poner en negrita los precios
        text = text.replace(/\$(\d+(\.\d{2})?)/g, '<strong>$$$1</strong>');
        
        return text;
    }
    
    function mostrarEscribiendo() {
        esperandoRespuesta = true;
        const escribiendoHTML = `
            <div class="mensaje mensaje-bot" id="escribiendo-indicador">
                <div class="mensaje-contenido bot">
                    <div class="escribiendo">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
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
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Botón para limpiar conversación (opcional)
    window.limpiarChat = function() {
        if (confirm('¿Limpiar la conversación?')) {
            fetch('/chatbot/api/chat/limpiar', {method: 'POST'})
                .then(() => {
                    contenedorMensajes.empty();
                    agregarMensajeBot('Conversación reiniciada. ¿En qué puedo ayudarte?');
                });
        }
    };
});