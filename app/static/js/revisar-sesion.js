// static/js/revisar-sesion.js

function checkUserStatus() {
    fetch('/api/verify-user-status')
        .then(response => {
            if (response.status === 401) {
                return response.json().then(data => {
                    handleSessionInvalid(data.message || 'Sesión no válida');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data && !data.valid) {
                handleSessionInvalid(data.message || 'Sesión no válida');
            }
        })
        .catch(error => {
            console.error('Error verificando usuario:', error);
            // Opcional: si hay error de red, no hacer nada
        });
}

function handleSessionInvalid(message) {
    // Evitar redirecciones múltiples
    if (window.sessionInvalidRedirect) return;
    window.sessionInvalidRedirect = true;
    
    const currentPath = window.location.pathname;
    const publicPaths = ['/login', '/registro', '/', '/sobre-nosotros', '/contacto', '/juegos', '/consolas', '/controles', '/accesorios'];
    
    // Solo redirigir si no estamos ya en una página pública
    if (!publicPaths.includes(currentPath)) {
        // Mostrar mensaje si existe
        if (message) {
            sessionStorage.setItem('logout_message', message);
        }
        window.location.href = '/login?expired=true';
    } else {
        // Si estamos en página pública, solo resetear el flag
        window.sessionInvalidRedirect = false;
    }
}

// Limpiar flag al recargar la página
window.addEventListener('beforeunload', function() {
    window.sessionInvalidRedirect = false;
});

// Verificar cada 8 segundos
setInterval(checkUserStatus, 8000);

// También al cargar la página
document.addEventListener('DOMContentLoaded', checkUserStatus);

// Interceptar peticiones fetch
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    return originalFetch(url, options).then(response => {
        if (response.status === 401) {
            response.clone().json().then(data => {
                if (data.message) {
                    handleSessionInvalid(data.message);
                } else {
                    handleSessionInvalid('Sesión expirada');
                }
            }).catch(() => {
                handleSessionInvalid('Sesión expirada');
            });
            throw new Error('Sesión inválida');
        }
        return response;
    });
};