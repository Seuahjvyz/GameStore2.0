// User menu functionality - ADMIN VERSION
document.addEventListener('DOMContentLoaded', function() {
    const userMenuBtn = document.getElementById('btn-menu-user');
    const userDropdown = document.getElementById('menu-user');
    
    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = userDropdown.style.display === 'block';
            userDropdown.style.display = isVisible ? 'none' : 'block';
            // Close accessibility panel if opening menu
            if (!isVisible && window.accessibilityManager && window.accessibilityManager.isOpen) {
                window.accessibilityManager.closePanel();
            }
            // Close chatbot if opening menu
            var ventanaChatbot = document.getElementById('ventana-chatbot');
            if (!isVisible && ventanaChatbot && ventanaChatbot.classList.contains('ventana-visible-chatbot')) {
                ventanaChatbot.classList.remove('ventana-visible-chatbot');
                ventanaChatbot.classList.add('ventana-oculto-chatbot');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            userDropdown.style.display = 'none';
        });

        // Prevent dropdown from closing when clicking inside
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Cargar información del usuario si está logueado
    cargarUsuarioActual();
});

async function cargarUsuarioActual() {
    try {
        const response = await fetch('/api/usuario/actual');
        if (response.ok) {
            const usuario = await response.json();
            if (usuario && usuario.id) {
                // Verificar si es administrador (role = 1)
                const esAdmin = usuario.role === 1;
                actualizarMenuUsuario(usuario, true, esAdmin);
            } else {
                actualizarMenuUsuario(null, false, false);
            }
        } else {
            actualizarMenuUsuario(null, false, false);
        }
    } catch (error) {
        console.error('Error al cargar usuario:', error);
        actualizarMenuUsuario(null, false, false);
    }
}

function actualizarMenuUsuario(usuario, estaLogueado, esAdmin) {
    const dropdownContent = document.querySelector('.contenido-menu-user');
    if (!dropdownContent) {
        console.error('No se encontró el elemento contenido-menu-user');
        return;
    }

    if (estaLogueado && usuario) {
        if (esAdmin) {
            // Menú para ADMINISTRADORES
            dropdownContent.innerHTML = `
                <a href="/admin/perfil-admin" class="dropdown-item">
                    <i class="fa-solid fa-user-gear"></i>
                    <span>Perfil</span>
                </a>
                <div class="dropdown-divider"></div>
                <a href="/logout" class="dropdown-item">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Cerrar Sesión</span>
                </a>
            `;
        } else {
            // Menú para USUARIOS NORMALES
            dropdownContent.innerHTML = `
                <a href="/perfil-usuario" class="dropdown-item">
                    <i class="fa-solid fa-user"></i>
                    <span>Mi Perfil</span>
                </a>
                <div class="dropdown-divider"></div>
                <a href="/logout" class="dropdown-item">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Cerrar Sesión</span>
                </a>
            `;
        }
    } else {
        // Menú para usuarios NO logueados
        dropdownContent.innerHTML = `
            <a href="/login" class="dropdown-item">
                <i class="fa-solid fa-right-to-bracket"></i>
                <span>Iniciar Sesión</span>
            </a>
            <a href="/registro" class="dropdown-item">
                <i class="fa-solid fa-user-plus"></i>
                <span>Registrarse</span>
            </a>
        `;
    }
    
    // Asegurar que el dropdown esté oculto inicialmente
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        userDropdown.style.display = 'none';
    }
}