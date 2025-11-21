// User menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.style.display = userDropdown.style.display === 'block' ? 'none' : 'block';
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
            if (usuario && usuario.id_usuario) {
                actualizarMenuUsuario(usuario);
            }
        }
    } catch (error) {
        console.error('Error al cargar usuario:', error);
    }
}

function actualizarMenuUsuario(usuario) {
    const dropdownContent = document.getElementById('dropdownContent') || document.querySelector('.dropdown-content');
    if (dropdownContent && usuario) {
        dropdownContent.innerHTML = `
            <div class="dropdown-user-info">
                <i class="fa-solid fa-user"></i>
                <span>Hola, ${usuario.nombre || usuario.nombre_usuario}</span>
            </div>
            <div class="dropdown-divider"></div>
            <a href="/perfil" class="dropdown-item">
                <i class="fa-solid fa-user"></i>
                <span>Mi Perfil</span>
            </a>
            <a href="/carrito" class="dropdown-item">
                <i class="fa-solid fa-cart-shopping"></i>
                <span>Carrito</span>
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
    }
}