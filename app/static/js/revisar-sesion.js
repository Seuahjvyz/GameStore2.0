// revisar-sesion.js - Versión optimizada
let sesionVerificada = false;
let timeoutVerificacion = null;

async function checkUserStatus() {
    // Evitar múltiples verificaciones simultáneas
    if (sesionVerificada) return;
    
    try {
        const response = await fetch('/api/verify-user-status');
        const data = await response.json();
        
        if (!data.valid) {
            console.log('Sesión no válida');
            // Solo redirigir si es necesario y no estamos ya en login
            if (!window.location.pathname.includes('/login') && 
                !window.location.pathname.includes('/registro')) {
                // No redirigir automáticamente, solo mostrar notificación si es necesario
                if (data.message) {
                    console.warn(data.message);
                }
            }
        } else {
            sesionVerificada = true;
            console.log('Sesión válida');
        }
    } catch (error) {
        console.error('Error checking user status:', error);
    } finally {
        // Programar próxima verificación solo si es necesario
        if (timeoutVerificacion) {
            clearTimeout(timeoutVerificacion);
        }
        // Verificar cada 30 segundos
        timeoutVerificacion = setTimeout(checkUserStatus, 60000);
    }
}

// Iniciar verificación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar 2 segundos antes de la primera verificación
    setTimeout(checkUserStatus, 2000);
});

// También verificar cuando la ventana recupera el foco
window.addEventListener('focus', function() {
    if (timeoutVerificacion) {
        clearTimeout(timeoutVerificacion);
    }
    checkUserStatus();
});