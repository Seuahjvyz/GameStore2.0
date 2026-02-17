const barra = document.querySelector('.barra-lateral'); // Trae por clase
const fondo = document.getElementById('fondo');         // Trae por ID
const boton = document.getElementById('btn-menu');      // Trae por ID

boton.addEventListener('click', accionarMenu)

function accionarMenu() {
    barra.classList.toggle('mostrar');
    fondo.classList.toggle('activo');
}
fondo.addEventListener('click', accionarMenu);

// Detectar página actual y marcar enlace como activo
document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".barra-lateral-link");
    const rutaActual = window.location.pathname;
    
    links.forEach(link => {
        const href = link.getAttribute("href");
        
        // Ignorar enlaces vacíos o con #
        if (href === "#" || !href) return;
        
        // Caso especial para la página de inicio
        if (href === "/" && rutaActual === "/") {
            link.classList.add("activo");
        }
        // Para otras páginas
        else if (href !== "/" && rutaActual.startsWith(href)) {
            link.classList.add("activo");
        }
    });
});