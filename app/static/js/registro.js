// Modelo de Usuario para Backbone
var Usuario = Backbone.Model.extend({
    defaults: {
        username: '',
        email: '',
        password: '',
        confirm_password: ''
    },

    url: '/api/registro',

    validate: function (attrs) {
        var errors = [];

        if (!attrs.username || attrs.username.length < 6) {
            errors.push('El nombre de usuario debe tener al menos 6 caracteres');
        }

        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!attrs.email || !emailRegex.test(attrs.email)) {
            errors.push('Ingresa un email válido');
        }

        // Validación de contraseña segura
        var passwordErrors = validarPasswordSegura(attrs.password);
        if (passwordErrors.length > 0) {
            errors.push.apply(errors, passwordErrors);
        }

        if (attrs.password !== attrs.confirm_password) {
            errors.push('Las contraseñas no coinciden');
        }

        return errors.length > 0 ? errors : undefined;
    }
});

// ✅ Función para validar contraseña segura
function validarPasswordSegura(password) {
    var errors = [];

    if (!password || password.length < 8) {
        errors.push('La contraseña debe tener al menos 8 caracteres');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Debe contener al menos 1 mayúscula');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('Debe contener al menos 1 minúscula');
    }
    if (!/[0-9]/.test(password)) {
        errors.push('Debe contener al menos 1 número');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push('Debe contener al menos 1 carácter especial (!@#$%^&*)');
    }

    return errors;
}

// ✅ Función para verificar requisitos individuales
function verificarRequisitos(password) {
    return {
        longitud: password.length >= 8,
        mayuscula: /[A-Z]/.test(password),
        minuscula: /[a-z]/.test(password),
        numero: /[0-9]/.test(password),
        especial: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
}

// ✅ Actualizar la lista visual de requisitos (con iconos)
function actualizarListaRequisitos(password) {
    var requisitos = verificarRequisitos(password);

    // Actualizar cada requisito con su icono
    actualizarRequisito('req-longitud', requisitos.longitud);
    actualizarRequisito('req-mayuscula', requisitos.mayuscula);
    actualizarRequisito('req-minuscula', requisitos.minuscula);
    actualizarRequisito('req-numero', requisitos.numero);
    actualizarRequisito('req-especial', requisitos.especial);
}

// ✅ Actualizar un requisito individual con el icono correspondiente
function actualizarRequisito(id, cumplido) {
    var $elemento = $('#' + id);
    var $icono = $elemento.find('i');

    if (cumplido) {
        $elemento.removeClass('invalid').addClass('valid');
        $icono.removeClass('fa-circle fa-x').addClass('fa-check');
    } else {
        $elemento.removeClass('valid').addClass('invalid');
        // ✅ CORREGIDO: usar passwordActual en lugar de password
        if (passwordActual.length === 0) {
            $icono.removeClass('fa-check fa-x').addClass('fa-circle');
        } else {
            $icono.removeClass('fa-circle fa-check').addClass('fa-x');
        }
    }
}

// Variable global para la contraseña actual
var passwordActual = '';

// Vista del Formulario de Registro
var RegistroView = Backbone.View.extend({
    el: '#registro-form',

    events: {
        'submit': 'registrarUsuario',
        'input #username': 'limpiarError',
        'input #email': 'limpiarError',
        'input #password': 'validarPasswordTiempoReal',
        'input #confirm-password': 'validarConfirmacion'
    },

    initialize: function () {
        this.usuario = new Usuario();
        this.listenTo(this.usuario, 'invalid', this.mostrarErrores);
        this.listenTo(this.usuario, 'sync', this.registroExitoso);
        this.listenTo(this.usuario, 'error', this.registroFallido);

        //  Inicializar todos los requisitos como círculos
        $('.requisito-item i').removeClass('fa-check fa-x').addClass('fa-circle');

        //  LIMPIAR FORMULARIO AL CARGAR LA PÁGINA
        this.$('#username').val('');
        this.$('#email').val('');
        this.$('#password').val('');
        this.$('#confirm-password').val('');
        passwordActual = '';
        $('#confirm-error').html('');
    },

    //  Validar contraseña en tiempo real
    validarPasswordTiempoReal: function (e) {
        passwordActual = $(e.target).val();
        actualizarListaRequisitos(passwordActual);

        // Validar confirmación si ya tiene texto
        var confirmPassword = this.$('#confirm-password').val();
        if (confirmPassword) {
            this.validarConfirmacion();
        }
    },

    //  Validar confirmación en tiempo real
    validarConfirmacion: function () {
        var password = this.$('#password').val();
        var confirmPassword = this.$('#confirm-password').val();
        var $confirmInput = this.$('#confirm-password');
        var $confirmError = $('#confirm-error');

        if (confirmPassword.length > 0) {
            if (password === confirmPassword) {
                $confirmInput.removeClass('error-input');
                $confirmError.html('<i class="fa-solid fa-check-circle"></i> Contraseñas coinciden').css('color', '#2ecc71');
            } else {
                $confirmInput.addClass('error-input');
                $confirmError.html('<i class="fa-solid fa-times-circle"></i> Las contraseñas no coinciden').css('color', '#e74c3c');
            }
        } else {
            $confirmInput.removeClass('error-input');
            $confirmError.html('');
        }
    },

    registrarUsuario: function (e) {
        e.preventDefault();

        // Validación extra antes de enviar
        var password = this.$('#password').val();
        var requisitos = verificarRequisitos(password);
        var todosRequisitos = Object.values(requisitos).every(Boolean);

        if (!todosRequisitos) {
            this.mostrarErrorGeneral(' La contraseña no cumple con todos los requisitos de seguridad');
            return;
        }

        var datos = {
            username: this.$('#username').val(),
            email: this.$('#email').val(),
            password: password,
            confirm_password: this.$('#confirm-password').val()
        };

        this.limpiarTodosErrores();
        this.usuario.set(datos);

        if (this.usuario.isValid()) {
            this.mostrarCargando(true);
            this.usuario.save();
        }
    },

    mostrarErrores: function (model, errors) {
        this.mostrarCargando(false);
        errors.forEach(function (error) {
            this.mostrarErrorGeneral(error);
        }.bind(this));
    },

    mostrarErrorGeneral: function (mensaje) {
        var $errorDiv = $('<div class="error-alerta">').html('<i class="fa-solid fa-circle-exclamation"></i> ' + mensaje);
        this.$('.register-btn').before($errorDiv);

        setTimeout(function () {
            $errorDiv.fadeOut(300, function () {
                $(this).remove();
            });
        }, 5000);
    },

    registroExitoso: function (model, response) {
        this.mostrarCargando(false);

        var email = this.$('#email').val();
        var mensaje = response.message || '¡Cuenta creada exitosamente!';

        this.mostrarExito(`
        <i class="fa-solid fa-envelope"></i> 
        ${mensaje}
        <br><br>
        <small>Se ha enviado un correo de verificación a: <strong>${email}</strong></small>
        <br>
        <small>Revisa tu bandeja de entrada y la carpeta de SPAM.</small>
    `);

        // ✅ LIMPIAR FORMULARIO MANUALMENTE (más efectivo que reset())
        this.$('#username').val('');
        this.$('#email').val('');
        this.$('#password').val('');
        this.$('#confirm-password').val('');

        // ✅ Resetear variable global de contraseña
        passwordActual = '';

        // ✅ Resetear los requisitos visuales a círculos
        $('.requisito-item i').removeClass('fa-check fa-x').addClass('fa-circle');
        $('.requisito-item').removeClass('valid invalid');

        // ✅ Limpiar mensaje de confirmación
        $('#confirm-error').html('');

        // ✅ Remover clases de error
        this.limpiarTodosErrores();

        // ✅ Quitar focus de los campos (opcional)
        this.$('#username').blur();
        this.$('#email').blur();
        this.$('#password').blur();
        this.$('#confirm-password').blur();
    },

    registroFallido: function (model, response) {
        this.mostrarCargando(false);
        var mensaje = response.responseJSON && response.responseJSON.error
            ? response.responseJSON.error
            : 'Error en el servidor. Intenta nuevamente.';
        this.mostrarErrorGeneral(mensaje);
    },

    mostrarCargando: function (mostrar) {
        var $btn = this.$('#registro-btn');
        if (mostrar) {
            $btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Creando cuenta...');
            $btn.prop('disabled', true);
        } else {
            $btn.html('<i class="fa-solid fa-user-plus"></i> Crear Cuenta');
            $btn.prop('disabled', false);
        }
    },

    mostrarExito: function (mensaje) {
        var $exitoDiv = $('<div class="exito-alerta">').html(mensaje);
        this.$('#registro-btn').before($exitoDiv);
    },

    limpiarError: function (e) {
        var $input = $(e.target);
        $input.removeClass('error-input');
        $input.siblings('.error-message').text('');
    },

    limpiarTodosErrores: function () {
        this.$('.error-alerta').remove();
        this.$('.error-input').removeClass('error-input');
        this.$('.error-message').text('');
    }
});

// Inicializar cuando el DOM esté listo
$(document).ready(function () {
    new RegistroView();
});