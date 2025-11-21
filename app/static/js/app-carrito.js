$(document).ready(function() {
    // El carrito ahora se inicializa desde agregar-carrito.js
    // Esta parte es principalmente para la página del carrito
    
    if (typeof Carrito !== 'undefined' && $('.carrito').length) {
        const carrito = new Carrito();
        const carritoView = new CarritoView({ collection: carrito });
    }
});