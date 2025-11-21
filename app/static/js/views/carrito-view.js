const ProductoCarritoView = Backbone.View.extend({
    tagName: 'div',
    className: 'producto',
    
    template: _.template(`
        <div class="imagenes_producto">
            <img class="imagen_producto" src="<%= imagen %>" alt="<%= nombre %>">
        </div>
        <h3 class="product-title"><%= nombre %></h3>
        <p class="product-category"><%= categoria %></p>
        <p class="product-price">$<%= (precio * cantidad).toFixed(2) %></p>
        <div class="controles-cantidad">
            <button class="btn-disminuir" data-id="<%= id %>">-</button>
            <span class="cantidad"><%= cantidad %></span>
            <button class="btn-aumentar" data-id="<%= id %>">+</button>
        </div>
        <button class="btn_eliminar" data-id="<%= id %>">
            <i class="fa-solid fa-trash-can"></i> Eliminar
        </button>
    `),
    
    events: {
        'click .btn_eliminar': 'eliminarProducto',
        'click .btn-aumentar': 'aumentarCantidad',
        'click .btn-disminuir': 'disminuirCantidad'
    },
    
    initialize: function() {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
    },
    
    render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    },
    
    eliminarProducto: function() {
        this.model.destroy();
    },
    
    aumentarCantidad: function() {
        const nuevaCantidad = this.model.get('cantidad') + 1;
        this.model.set('cantidad', nuevaCantidad);
    },
    
    disminuirCantidad: function() {
        const cantidadActual = this.model.get('cantidad');
        if (cantidadActual > 1) {
            this.model.set('cantidad', cantidadActual - 1);
        } else {
            this.eliminarProducto();
        }
    }
});

const CarritoView = Backbone.View.extend({
    el: '.carrito',
    
    events: {
        'click .enlace_seguir_comprando': 'seguirComprando',
        'click .enlace_pagar': 'irAPagar'
    },
    
    initialize: function() {
        this.listaProductos = this.$('.productos');
        this.subtotalElement = this.$('#subtotal');
        this.totalElement = this.$('#total');
        
        this.listenTo(this.collection, 'add', this.agregarProducto);
        this.listenTo(this.collection, 'remove', this.actualizarTotales);
        this.listenTo(this.collection, 'change', this.actualizarTotales);
        this.listenTo(this.collection, 'reset', this.render);
        
        this.render();
    },
    
    render: function() {
        // Limpiar lista actual
        this.listaProductos.empty();
        
        // Renderizar cada producto
        this.collection.each(function(producto) {
            this.agregarProducto(producto);
        }, this);
        
        this.actualizarTotales();
        
        return this;
    },
    
    agregarProducto: function(producto) {
        const vistaProducto = new ProductoCarritoView({ model: producto });
        this.listaProductos.append(vistaProducto.render().el);
    },
    
    actualizarTotales: function() {
        const subtotal = this.collection.obtenerSubtotal();
        const total = this.collection.obtenerTotal();
        
        this.subtotalElement.text('$' + subtotal.toFixed(2));
        this.totalElement.text('$' + total.toFixed(2));
    },
    
    seguirComprando: function(e) {
        e.preventDefault();
        // Ya está enlazado al home por el href
    },
    
    irAPagar: function(e) {
        e.preventDefault();
        if (this.collection.length === 0) {
            alert('Tu carrito está vacío');
            return;
        }
        window.location.href = '/pagar';
    }
});