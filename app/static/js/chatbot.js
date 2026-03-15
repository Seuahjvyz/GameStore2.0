// chatbot.js - Versión mejorada con sesiones individuales

$(document).ready(function() {
    console.log("✅ Chatbot JS cargado (versión sesiones)");
    
    // Elementos del DOM
    const btnChatbot = $('#btn-chatbot');
    const ventanaChatbot = $('#ventana-chatbot');
    const btnCerrar = $('#btn-cerrar-chatbot');
    const btnEnviar = $('#btn-enviar-mensaje-chatbot');
    const inputMensaje = $('#mensaje-input-chatbot');
    const contenedorMensajes = $('#mensajes-chatbot');
    
    // Estado del chatbot
    let esperandoRespuesta = false;
    let sessionId = null;
    
    // Cargar información de sesión al inicio
    cargarInfoSesion();
    cargarHistorial();
    cargarModelos();
    
    function cargarInfoSesion() {
        fetch('/chatbot/api/chat/sesion-info')
            .then(res => res.json())
            .then(data => {
                sessionId = data.session_id;
                console.log(`🔐 Sesión ID: ${sessionId}`);
                console.log(`👤 Usuario ${data.is_authenticated ? 'logueado' : 'anónimo'}`);
            })
            .catch(error => console.error('Error cargando sesión:', error));
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
                            agregarMensajeBot(msg.contenido, msg.hora, false);
                        }
                    });
                    console.log(`📜 Historial cargado: ${data.historial.length} mensajes`);
                } else {
                    // Mensaje de bienvenida personalizado
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
            })
            .catch(() => console.log("⚠️ No se pudo cargar historial"));
    }
    
    function cargarModelos() {
        fetch('/chatbot/api/chat/modelos')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    console.log('📚 Modelos disponibles:', data.modelos);
                }
            });
    }
    
    // Mostrar/ocultar chatbot
    btnChatbot.on('click', function() {
        ventanaChatbot.removeClass('ventana-oculto-chatbot').addClass('ventana-visible-chatbot');
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
        
        // Enviar a la API
        fetch('/chatbot/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mensaje: mensaje })
        })
        .then(response => {
            if (!response.ok) throw new Error(`Error ${response.status}`);
            return response.json();
        })
        .then(data => {
            quitarEscribiendo();
            
            if (data.success) {
                agregarMensajeBot(data.respuesta, null, data.fuente === 'base_datos');
                console.log(`🤖 Modelo usado: ${data.modelo || 'BD'}`);
                console.log(`🔐 Sesión: ${data.session_id}`);
            } else {
                agregarMensajeBot('Lo siento, tuve un problema. Intenta de nuevo. 😕');
            }
        })
        .catch(error => {
            quitarEscribiendo();
            agregarMensajeBot('Error de conexión. Verifica tu internet. 🌐');
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
    
    function agregarMensajeBot(mensaje, hora = null, esDeBD = false) {
        const horaActual = hora || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const claseBD = esDeBD ? 'mensaje-bd' : '';
        
        const mensajeHTML = `
            <div class="mensaje mensaje-bot">
                <div class="mensaje-contenido bot ${claseBD}">
                    ${formatearMensaje(mensaje)}
                    <span class="mensaje-hora">${horaActual}</span>
                </div>
            </div>
        `;
        contenedorMensajes.append(mensajeHTML);
        scrollToBottom();
    }
    
    function formatearMensaje(texto) {
        let text = escapeHTML(texto);
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        text = text.replace(/\n/g, '<br>');
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
    
    // Función para limpiar chat (opcional)
    window.limpiarChat = function() {
        if (confirm('¿Limpiar tu conversación?')) {
            fetch('/chatbot/api/chat/limpiar', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    contenedorMensajes.empty();
                    agregarMensajeBot('Conversación reiniciada. ¿En qué puedo ayudarte?');
                    console.log('🧹 Chat limpiado, sesión:', data.session_id);
                });
        }
    };
});