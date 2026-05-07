// chatbot.js - Versión con diagnóstico de enlaces

$(document).ready(function () {
    console.log("✅ Chatbot JS cargado");

    const btnChatbot = $('#btn-chatbot');
    const ventanaChatbot = $('#ventana-chatbot');
    const btnCerrar = $('#btn-cerrar-chatbot');
    const btnEnviar = $('#btn-enviar-mensaje-chatbot');
    const inputMensaje = $('#mensaje-input-chatbot');
    const contenedorMensajes = $('#mensajes-chatbot');

    let esperandoRespuesta = false;

    // Al abrir el chat siempre muestra el saludo (el historial se borra al cerrar)
    function mostrarSaludo() {
        fetch('/chatbot/api/user-info')
            .then(res => res.json())
            .then(userData => {
                contenedorMensajes.empty();
                if (userData.logged_in) {
                    agregarMensajeBot(`¡Hola **${userData.user.username}**! 😊 Bienvenido a **Game Store**. ¿En qué puedo ayudarte hoy? 🎮`);
                } else {
                    agregarMensajeBot('¡Hola! 😊 Bienvenido a **Game Store**. ¿En qué puedo ayudarte hoy? 🎮');
                }
            })
            .catch(() => {
                contenedorMensajes.empty();
                agregarMensajeBot('¡Hola! 😊 Bienvenido a **Game Store**. ¿En qué puedo ayudarte hoy? 🎮');
            });
    }

    btnChatbot.on('click', function () {
        ventanaChatbot.removeClass('ventana-oculto-chatbot').addClass('ventana-visible-chatbot');
        mostrarSaludo();
        // Cerrar panel de accesibilidad si está abierto
        if (window.accessibilityManager && window.accessibilityManager.isOpen) {
            window.accessibilityManager.closePanel();
        }
        inputMensaje.focus();
    });

    btnCerrar.on('click', function () {
        // Limpiar el historial en el servidor cuando se cierra el panel
        fetch('/chatbot/api/chat/cerrar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).then(() => {
            // Limpiar también el contenedor de mensajes local
            contenedorMensajes.empty();
            console.log("🧹 Chat limpiado al cerrar panel");
        }).catch(error => {
            console.error("Error al limpiar chat:", error);
        });

        // Cerrar la ventana
        ventanaChatbot.removeClass('ventana-visible-chatbot').addClass('ventana-oculto-chatbot');
    });

    inputMensaje.on('keypress', function (e) {
        if (e.which === 13 && !esperandoRespuesta) {
            enviarMensaje();
        }
    });

    btnEnviar.on('click', function () {
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
                    agregarMensajeBot(data.respuesta || 'Lo siento, tuve un problema. 😕');
                }
            })
            .catch(error => {
                quitarEscribiendo();
                agregarMensajeBot('Error de conexión. 🌐');
                console.error('Error:', error);
            });
    }

    function agregarMensajeUsuario(mensaje, hora = null) {
        const horaActual = hora || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
        const horaActual = hora || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const mensajeFormateado = formatearMensaje(mensaje);
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

        let text = texto;

        // 1. Rutas relativas PRIMERO — solo las que van precedidas de espacio, inicio de línea,
        //    paréntesis, dos puntos o coma. Así no captura /strong ni /a dentro de HTML.
        //    La ruta debe ir seguida de espacio, fin de línea, puntuación o fin de cadena.
        text = text.replace(/(^|[\s(,:>])(\/(juegos|consolas|controles|accesorios|carrito|favoritos|pedidos|perfil-usuario|contacto|sobre-nosotros|login|registro))([\s),.<\n]|$)/g,
            function (match, pre, ruta, nombre, post) {
                return `${pre}<a href="${ruta}" style="color:#8b5cf6;text-decoration:underline;font-weight:500;">${ruta}</a>${post}`;
            }
        );

        // 2. URLs completas → enlaces
        text = text.replace(/(https?:\/\/[^\s<")\]]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer" style="color:#8b5cf6;text-decoration:underline;font-weight:500;">$1</a>'
        );

        // 3. Negritas markdown **texto** → <strong> (al final, cuando ya no hay rutas que contaminar)
        text = text.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');

        // 4. Saltos de línea → <br>
        text = text.replace(/\n/g, '<br>');

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

    window.limpiarChat = function () {
        if (confirm('¿Limpiar conversación?')) {
            fetch('/chatbot/api/chat/limpiar', { method: 'POST' })
                .then(() => {
                    contenedorMensajes.empty();
                    agregarMensajeBot('Conversación reiniciada.');
                });
        }
    };
});