// user-menu.js - Controlador del menú de usuario
class UserMenu {
    constructor() {
        this.userMenuBtn = document.getElementById('userMenuBtn');
        this.userDropdown = document.getElementById('userDropdown');
        
        if (this.userMenuBtn && this.userDropdown) {
            this.init();
        }
    }
    
    init() {
        // Toggle del menú desplegable
        this.userMenuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Cerrar menú al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!this.userDropdown.contains(e.target) && !this.userMenuBtn.contains(e.target)) {
                this.hideDropdown();
            }
        });
        
        // Prevenir que el menú se cierre al hacer click dentro
        this.userDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    toggleDropdown() {
        this.userDropdown.classList.toggle('show');
        this.userMenuBtn.classList.toggle('active');
    }
    
    hideDropdown() {
        this.userDropdown.classList.remove('show');
        this.userMenuBtn.classList.remove('active');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new UserMenu();
});