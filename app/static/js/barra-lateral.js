const barra = document.querySelector('.barra-lateral');
const fondo = document.getElementById('fondo');
const boton = document.getElementById('btn-menu');

// Initialize ARIA attributes
if (boton) {
    boton.setAttribute('aria-expanded', 'false');
    boton.setAttribute('aria-controls', 'barra-lateral');
    boton.setAttribute('aria-label', 'Abrir menú de navegación');
}

if (barra) {
    barra.setAttribute('role', 'navigation');
    barra.setAttribute('aria-label', 'Barra de navegación principal');
    barra.setAttribute('aria-hidden', 'true');
}

boton.addEventListener('click', accionarMenu);

function accionarMenu() {
    const isOpen = barra.classList.toggle('mostrar');
    fondo.classList.toggle('activo');

    // Update ARIA attributes
    if (boton) {
        boton.setAttribute('aria-expanded', isOpen);
        boton.setAttribute('aria-label', isOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación');
    }
    if (barra) {
        barra.setAttribute('aria-hidden', !isOpen);
    }
    if (fondo) {
        fondo.setAttribute('aria-hidden', !isOpen);
    }

    // Focus management - focus first link when opened
    if (isOpen) {
        setTimeout(() => {
            const firstLink = barra.querySelector('.barra-lateral-link');
            if (firstLink) firstLink.focus();
        }, 100);
    }
}

fondo.addEventListener('click', accionarMenu);

// Close sidebar on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && barra.classList.contains('mostrar')) {
        accionarMenu();
        if (boton) boton.focus();
    }
});

// Detectar página actual y marcar enlace como activo
document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".barra-lateral-link");
    const rutaActual = window.location.pathname;

    links.forEach(link => {
        const href = link.getAttribute("href");

        // Add ARIA attributes to links
        link.setAttribute('role', 'menuitem');

        // Ignorar enlaces vacíos o con #
        if (href === "#" || !href) return;

        // Caso especial para la página de inicio
        if (href === "/" && rutaActual === "/") {
            link.classList.add("activo");
            link.setAttribute('aria-current', 'page');
        }
        // Para otras páginas
        else if (href !== "/" && rutaActual.startsWith(href)) {
            link.classList.add("activo");
            link.setAttribute('aria-current', 'page');
        }
    });

    // Set up keyboard navigation within sidebar
    const sidebarLinks = barra ? barra.querySelectorAll('.barra-lateral-link') : [];
    if (sidebarLinks.length > 0) {
        sidebarLinks.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextIndex = (index + 1) % sidebarLinks.length;
                    sidebarLinks[nextIndex].focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevIndex = (index - 1 + sidebarLinks.length) % sidebarLinks.length;
                    sidebarLinks[prevIndex].focus();
                }
            });
        });
    }
});
