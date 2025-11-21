// User menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = userDropdown.style.display === 'block';
            userDropdown.style.display = isVisible ? 'none' : 'block';
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
                actualizarMenuUsuario(usuario, true); // Usuario logueado
            } else {
                actualizarMenuUsuario(null, false); // Usuario NO logueado
            }
        } else {
            actualizarMenuUsuario(null, false); // Usuario NO logueado
        }
    } catch (error) {
        console.error('Error al cargar usuario:', error);
        actualizarMenuUsuario(null, false); // Usuario NO logueado en caso de error
    }
}

function actualizarMenuUsuario(usuario, estaLogueado) {
    const dropdownContent = document.querySelector('.dropdown-content');
    if (!dropdownContent) {
        console.error('No se encontró el elemento dropdown-content');
        return;
    }

    if (estaLogueado && usuario) {
        // Menú para usuarios logueados
        dropdownContent.innerHTML = `
            <div class="dropdown-user-info">
                <i class="fa-solid fa-user"></i>
                <span>Hola, ${usuario.username || 'Usuario'}</span>
            </div>
            <div class="dropdown-divider"></div>
            <a href="/perfil" class="dropdown-item">
                <i class="fa-solid fa-user"></i>
                <span>Mi Perfil</span>
            </a>
            <a href="/pedidos" class="dropdown-item">
                <i class="fa-solid fa-box"></i>
                <span>Mis Pedidos</span>
            </a>
            <div class="dropdown-divider"></div>
            <a href="/logout" class="dropdown-item">
                <i class="fa-solid fa-right-from-bracket"></i>
                <span>Cerrar Sesión</span>
            </a>
        `;
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