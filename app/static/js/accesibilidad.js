// ========================
// ACCESIBILIDAD AVANZADA
// ========================

(function () {
    "use strict";

    function AccessibilityManager() {
        this.state = {
            grayscale: false,
            highContrast: false,
            invertColors: false,
            readingMask: false,
            readingGuide: false,
            highlightLinks: false,
            dyslexicFont: false,
            lightTheme: false,
            lineSpacing: 1.5,
            letterSpacing: 0,
            fontSize: 16,
            textScale: 100,
            screenReader: false,
            skipToContent: false,
            keyboardNav: false
        };
        this.panel = null;
        this.isOpen = false;
        this.speechSynthesis = window.speechSynthesis;
        this.screenReaderActive = false;
        this.textScaleOptions = [50, 100, 150, 200];
        this.currentScaleIndex = 1;
        this.isInitialLoad = true;
        this.init();
    }

    AccessibilityManager.prototype.init = function () {
        this.loadSettings();
        this.createPanel();
        this.applyAllSettings();
        this.syncCheckboxes();
        this.setupEventListeners();
        this.improveAriaAttributes();
        this.setupEscapeKeyHandler();
        // Mark initial load as complete so future toggles trigger reading
        this.isInitialLoad = false;
    };

    AccessibilityManager.prototype.createPanel = function () {
        var self = this;
        if (!document.querySelector(".btn-accesibilidad")) {
            var btnChatbot = document.querySelector(".btn-chatbot");
            var btn = document.createElement("button");
            btn.className = "btn-accesibilidad";
            btn.setAttribute("aria-label", "Abrir panel de accesibilidad");
            btn.setAttribute("aria-expanded", "false");
            btn.innerHTML = '<i class="fa-solid fa-universal-access"></i>';
            if (btnChatbot && btnChatbot.parentNode) {
                btnChatbot.parentNode.insertBefore(btn, btnChatbot);
            } else {
                document.body.appendChild(btn);
            }
            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                self.togglePanel();
            });
        }
        if (!document.querySelector(".accesibilidad-panel")) {
            var panel = document.createElement("div");
            panel.className = "accesibilidad-panel";
            panel.setAttribute("role", "dialog");
            panel.setAttribute("aria-label", "Panel de opciones de accesibilidad");

            var panelHTML = '<div class="accesibilidad-panel-header"><i class="fa-solid fa-universal-access"></i><h3>Opciones de Accesibilidad</h3><button class="btn-cerrar-panel" aria-label="Cerrar panel"><i class="fa-solid fa-times"></i></button></div>';
            panelHTML += '<div class="accesibilidad-panel-body" style="padding: 1rem 1.25rem;">';

            // Section: Visual
            panelHTML += '<div class="accesibilidad-seccion">';
            panelHTML += '<h4><i class="fa-solid fa-eye"></i> Visual</h4>';
            var visualOptions = [
                { id: 'acc-grayscale', icon: 'fa-palette', color: '#8b5cf6', label: 'Escala de grises', prop: 'grayscale' },
                { id: 'acc-highContrast', icon: 'fa-circle-half-stroke', color: '#f59e0b', label: 'Alto contraste', prop: 'highContrast' },
                { id: 'acc-invertColors', icon: 'fa-adjust', color: '#10b981', label: 'Invertir colores', prop: 'invertColors' }/*,
                { id: 'acc-lightTheme', icon: 'fa-sun', color: '#fbbf24', label: self.state.lightTheme ? 'Modo oscuro' : 'Modo claro', prop: 'lightTheme' }*/
            ];
            visualOptions.forEach(function (opt) {
                panelHTML += '<div class="accesibilidad-option">';
                panelHTML += '<div class="option-info">';
                panelHTML += '<i class="fa-solid ' + opt.icon + '" style="color:' + opt.color + '; margin-right:10px;"></i>';
                panelHTML += '<span>' + opt.label + '</span>';
                panelHTML += '</div>';
                panelHTML += '<label class="toggle-switch">';
                panelHTML += '<input type="checkbox" id="' + opt.id + '" ' + (self.state[opt.prop] ? 'checked' : '') + '>';
                panelHTML += '<span class="toggle-slider"></span>';
                panelHTML += '</label>';
                panelHTML += '</div>';
            });
            panelHTML += '</div>';

            // Section: Lectura
            panelHTML += '<div class="accesibilidad-seccion">';
            panelHTML += '<h4><i class="fa-solid fa-book-open"></i> Lectura</h4>';
            var readingOptions = [
                { id: 'acc-readingMask', icon: 'fa-mask', color: '#06b6d4', label: 'Mascara de lectura', prop: 'readingMask' },
                { id: 'acc-readingGuide', icon: 'fa-ruler-horizontal', color: '#3b82f6', label: 'Guia de lectura', prop: 'readingGuide' },
                { id: 'acc-dyslexicFont', icon: 'fa-font', color: '#a855f7', label: 'Fuente para dislexia', prop: 'dyslexicFont' }
            ];
            readingOptions.forEach(function (opt) {
                panelHTML += '<div class="accesibilidad-option">';
                panelHTML += '<div class="option-info">';
                panelHTML += '<i class="fa-solid ' + opt.icon + '" style="color:' + opt.color + '; margin-right:10px;"></i>';
                panelHTML += '<span>' + opt.label + '</span>';
                panelHTML += '</div>';
                panelHTML += '<label class="toggle-switch">';
                panelHTML += '<input type="checkbox" id="' + opt.id + '" ' + (self.state[opt.prop] ? 'checked' : '') + '>';
                panelHTML += '<span class="toggle-slider"></span>';
                panelHTML += '</label>';
                panelHTML += '</div>';
            });
            // Espaciado vertical y horizontal for dyslexia
            panelHTML += '<div class="accesibilidad-option">';
            panelHTML += '<div class="option-info">';
            panelHTML += '<i class="fa-solid fa-arrows-up-down" style="color:#a855f7; margin-right:10px;"></i>';
            panelHTML += '<span>Espaciado Vertical: ' + self.state.lineSpacing + '</span>';
            panelHTML += '</div>';
            panelHTML += '<button id="acc-lineSpacing" class="text-scale-btn">' + self.state.lineSpacing + '</button>';
            panelHTML += '</div>';
            panelHTML += '<div class="accesibilidad-option">';
            panelHTML += '<div class="option-info">';
            panelHTML += '<i class="fa-solid fa-arrows-left-right" style="color:#a855f7; margin-right:10px;"></i>';
            panelHTML += '<span>Espaciado Horizontal: ' + self.state.letterSpacing + '</span>';
            panelHTML += '</div>';
            panelHTML += '<button id="acc-letterSpacing" class="text-scale-btn">' + self.state.letterSpacing + '</button>';
            panelHTML += '</div>';
            panelHTML += '</div>';

            // Section: Navegacion y Ayudas
            panelHTML += '<div class="accesibilidad-seccion">';
            panelHTML += '<h4><i class="fa-solid fa-compass"></i> Navegacion y Ayudas</h4>';
            var navOptions = [
                { id: 'acc-highlightLinks', icon: 'fa-link', color: '#ec4899', label: 'Resaltar enlaces', prop: 'highlightLinks' },
                { id: 'acc-screenReader', icon: 'fa-volume-high', color: '#ef4444', label: 'Lector de pantalla', prop: 'screenReader' }
            ];
            navOptions.forEach(function (opt) {
                panelHTML += '<div class="accesibilidad-option">';
                panelHTML += '<div class="option-info">';
                panelHTML += '<i class="fa-solid ' + opt.icon + '" style="color:' + opt.color + '; margin-right:10px;"></i>';
                panelHTML += '<span>' + opt.label + '</span>';
                panelHTML += '</div>';
                panelHTML += '<label class="toggle-switch">';
                panelHTML += '<input type="checkbox" id="' + opt.id + '" ' + (self.state[opt.prop] ? 'checked' : '') + '>';
                panelHTML += '<span class="toggle-slider"></span>';
                panelHTML += '</label>';
                panelHTML += '</div>';
            });
            panelHTML += '</div>';

            // Text scale button
            panelHTML += '<div class="accesibilidad-option">';
            panelHTML += '<div class="option-info">';
            panelHTML += '<i class="fa-solid fa-text-height" style="color:#f59e0b; margin-right:10px;"></i>';
            panelHTML += '<span>Tamaño de texto</span>';
            panelHTML += '</div>';
            panelHTML += '<button id="acc-textScale" class="text-scale-btn">' + self.state.textScale + '%</button>';
            panelHTML += '</div>';

            // Reset button
            panelHTML += '<div class="accesibilidad-option reset-option">';
            panelHTML += '<button id="resetAccessibility" class="reset-btn"><i class="fa-solid fa-rotate-left"></i> Restablecer todo</button>';
            panelHTML += '</div>';

            panelHTML += '</div>';
            panel.innerHTML = panelHTML;
            document.body.appendChild(panel);
        }
        this.panel = document.querySelector(".accesibilidad-panel");
        var closeBtn = this.panel.querySelector(".btn-cerrar-panel");
        if (closeBtn) {
            closeBtn.addEventListener("click", function () { self.closePanel(); });
        }
    };

    AccessibilityManager.prototype.syncCheckboxes = function () {
        var self = this;
        var toggles = [
            { id: "acc-grayscale", prop: "grayscale" },
            { id: "acc-highContrast", prop: "highContrast" },
            { id: "acc-invertColors", prop: "invertColors" },
            { id: "acc-lightTheme", prop: "lightTheme" },
            { id: "acc-readingMask", prop: "readingMask" },
            { id: "acc-readingGuide", prop: "readingGuide" },
            { id: "acc-dyslexicFont", prop: "dyslexicFont" },
            { id: "acc-highlightLinks", prop: "highlightLinks" },
            { id: "acc-screenReader", prop: "screenReader" }
        ];
        toggles.forEach(function (item) {
            var checkbox = document.getElementById(item.id);
            if (checkbox) {
                checkbox.checked = self.state[item.prop];
            }
        });
        // Update light theme label
        var label = document.querySelector("#acc-lightTheme");
        if (label) {
            var span = label.parentNode.parentNode.querySelector(".option-info span");
            if (span) {
                span.textContent = self.state.lightTheme ? "Modo oscuro" : "Modo claro";
            }
        }
    };

    AccessibilityManager.prototype.togglePanel = function () {
        if (this.isOpen) { this.closePanel(); } else { this.openPanel(); }
    };

    AccessibilityManager.prototype.openPanel = function () {
        // Close chatbot if open
        this.closeChatbot();
        // Close user menu if open
        this.closeUserMenu();
        this.panel.classList.add("active");
        this.isOpen = true;
        var btn = document.querySelector(".btn-accesibilidad");
        if (btn) { btn.setAttribute("aria-expanded", "true"); }
        // Focus first focusable element in panel
        setTimeout(function () {
            var firstFocusable = self.panel.querySelector('button, input, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) firstFocusable.focus();
        }, 100);
    };

    AccessibilityManager.prototype.closePanel = function () {
        this.panel.classList.remove("active");
        this.isOpen = false;
        var btn = document.querySelector(".btn-accesibilidad");
        if (btn) { btn.setAttribute("aria-expanded", "false"); btn.focus(); }
    };

    AccessibilityManager.prototype.closeChatbot = function () {
        var ventanaChatbot = document.getElementById('ventana-chatbot');
        if (ventanaChatbot) {
            ventanaChatbot.classList.remove('ventana-visible-chatbot');
            ventanaChatbot.classList.add('ventana-oculto-chatbot');
        }
    };

    AccessibilityManager.prototype.closeUserMenu = function () {
        var userDropdown = document.getElementById('menu-user');
        if (userDropdown) {
            userDropdown.style.display = 'none';
        }
    };

    AccessibilityManager.prototype.setupEscapeKeyHandler = function () {
        var self = this;
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                // Close accessibility panel if open
                if (self.isOpen) {
                    e.preventDefault();
                    self.closePanel();
                    return;
                }
                // Close chatbot if open
                var ventanaChatbot = document.getElementById('ventana-chatbot');
                if (ventanaChatbot && ventanaChatbot.classList.contains('ventana-visible-chatbot')) {
                    e.preventDefault();
                    ventanaChatbot.classList.remove('ventana-visible-chatbot');
                    ventanaChatbot.classList.add('ventana-oculto-chatbot');
                    var btnChatbot = document.querySelector('.btn-chatbot');
                    if (btnChatbot) btnChatbot.focus();
                    return;
                }
                // Close user menu if open
                var userDropdown = document.getElementById('menu-user');
                if (userDropdown && userDropdown.style.display === 'block') {
                    e.preventDefault();
                    userDropdown.style.display = 'none';
                    var btnUser = document.getElementById('btn-menu-user');
                    if (btnUser) btnUser.focus();
                    return;
                }
            }
        });
    };

    AccessibilityManager.prototype.setupEventListeners = function () {
        var self = this;
        var toggles = [
            { id: "acc-grayscale", prop: "grayscale" },
            { id: "acc-highContrast", prop: "highContrast" },
            { id: "acc-invertColors", prop: "invertColors" },
            { id: "acc-lightTheme", prop: "lightTheme" },
            { id: "acc-readingMask", prop: "readingMask" },
            { id: "acc-readingGuide", prop: "readingGuide" },
            { id: "acc-dyslexicFont", prop: "dyslexicFont" },
            { id: "acc-highlightLinks", prop: "highlightLinks" },
            { id: "acc-screenReader", prop: "screenReader" }
        ];
        toggles.forEach(function (item) {
            var element = document.getElementById(item.id);
            if (element) {
                element.addEventListener("change", function (e) {
                    self.state[item.prop] = e.target.checked;
                    self.applySetting(item.prop);
                    self.saveSettings();
                    // Update light theme label dynamically
                    if (item.prop === "lightTheme") {
                        var label = document.querySelector("#acc-lightTheme");
                        if (label) {
                            var span = label.parentNode.parentNode.querySelector(".option-info span");
                            if (span) {
                                span.textContent = self.state.lightTheme ? "Modo oscuro" : "Modo claro";
                            }
                        }
                    }
                });
                // Allow keyboard activation with Space/Enter
                element.addEventListener("keydown", function (e) {
                    if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        element.checked = !element.checked;
                        element.dispatchEvent(new Event("change"));
                    }
                });
            }
        });
        var textScaleBtn = document.getElementById("acc-textScale");
        if (textScaleBtn) {
            textScaleBtn.addEventListener("click", function () {
                self.currentScaleIndex = (self.currentScaleIndex + 1) % self.textScaleOptions.length;
                self.state.textScale = self.textScaleOptions[self.currentScaleIndex];
                self.applySetting("textScale");
                self.saveSettings();
                textScaleBtn.textContent = self.state.textScale + "%";
            });
        }
        var lineSpacingBtn = document.getElementById("acc-lineSpacing");
        if (lineSpacingBtn) {
            lineSpacingBtn.addEventListener("click", function () {
                var options = [1.0, 1.5, 2.0, 2.5];
                var currentIndex = options.indexOf(self.state.lineSpacing);
                currentIndex = (currentIndex + 1) % options.length;
                self.state.lineSpacing = options[currentIndex];
                self.applySpacing();
                self.saveSettings();
                lineSpacingBtn.textContent = self.state.lineSpacing;
                var label = document.querySelector("#acc-lineSpacing").parentNode.querySelector(".option-info span");
                if (label) label.textContent = "Espaciado Vertical: " + self.state.lineSpacing;
            });
        }
        var letterSpacingBtn = document.getElementById("acc-letterSpacing");
        if (letterSpacingBtn) {
            letterSpacingBtn.addEventListener("click", function () {
                var options = [0, 2, 4, 6];
                var currentIndex = options.indexOf(self.state.letterSpacing);
                currentIndex = (currentIndex + 1) % options.length;
                self.state.letterSpacing = options[currentIndex];
                self.applySpacing();
                self.saveSettings();
                letterSpacingBtn.textContent = self.state.letterSpacing;
                var label = document.querySelector("#acc-letterSpacing").parentNode.querySelector(".option-info span");
                if (label) label.textContent = "Espaciado Horizontal: " + self.state.letterSpacing;
            });
        }
        var resetBtn = document.getElementById("resetAccessibility");
        if (resetBtn) {
            resetBtn.addEventListener("click", function () { self.resetAll(); });
        }

        // Keyboard navigation within the panel
        this.setupPanelKeyboardNav();
    };

    AccessibilityManager.prototype.setupPanelKeyboardNav = function () {
        var self = this;
        if (!this.panel) return;

        this.panel.addEventListener("keydown", function (e) {
            if (!self.isOpen) return;

            var selector = 'button:not([disabled]), input[type="checkbox"]:not([disabled]), [tabindex]:not([tabindex="-1"])';
            var focusableElements = self.panel.querySelectorAll(selector);
            var focusableArray = Array.from(focusableElements);
            if (focusableArray.length === 0) return;

            var currentIndex = focusableArray.indexOf(document.activeElement);
            if (currentIndex === -1) currentIndex = 0;

            switch (e.key) {
                case 'ArrowDown':
                case 'ArrowRight':
                    e.preventDefault();
                    var nextIndex = (currentIndex + 1) % focusableArray.length;
                    focusableArray[nextIndex].focus();
                    break;
                case 'ArrowUp':
                case 'ArrowLeft':
                    e.preventDefault();
                    var prevIndex = currentIndex <= 0 ? focusableArray.length - 1 : currentIndex - 1;
                    focusableArray[prevIndex].focus();
                    break;
                case 'Home':
                    e.preventDefault();
                    focusableArray[0].focus();
                    break;
                case 'End':
                    e.preventDefault();
                    focusableArray[focusableArray.length - 1].focus();
                    break;
                case 'Tab':
                    var firstElement = focusableArray[0];
                    var lastElement = focusableArray[focusableArray.length - 1];

                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            e.preventDefault();
                            lastElement.focus();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            e.preventDefault();
                            firstElement.focus();
                        }
                    }
                    break;
            }
        });
    };

    AccessibilityManager.prototype.applySetting = function (key) {
        var body = document.body;
        switch (key) {
            case "grayscale":
                body.classList.toggle("accesibilidad-grayscale", this.state.grayscale);
                break;
            case "highContrast":
                body.classList.toggle("accesibilidad-high-contrast", this.state.highContrast);
                break;
            case "invertColors":
                body.classList.toggle("accesibilidad-invert", this.state.invertColors);
                break;
            case "lightTheme":
                body.classList.toggle("accesibilidad-light", this.state.lightTheme);
                break;
            case "readingMask":
                if (this.state.readingMask) {
                    body.classList.add("accesibilidad-reading-mask");
                    this.createReadingMask();
                } else {
                    body.classList.remove("accesibilidad-reading-mask");
                    this.removeReadingMask();
                }
                break;
            case "readingGuide":
                if (this.state.readingGuide) {
                    body.classList.add("accesibilidad-reading-guide");
                    this.createReadingGuide();
                } else {
                    body.classList.remove("accesibilidad-reading-guide");
                    this.removeReadingGuide();
                }
                break;
            case "highlightLinks":
                body.classList.toggle("accesibilidad-highlight-links", this.state.highlightLinks);
                break;
            case "dyslexicFont":
                body.classList.toggle("accesibilidad-dyslexic", this.state.dyslexicFont);
                this.applySpacing();
                break;
            case "textScale":
                this.applyTextScale();
                break;
            case "screenReader":
                if (this.state.screenReader) { this.enableScreenReader(); }
                else { this.disableScreenReader(); }
                break;
            case "skipToContent":
                this.toggleSkipToContent();
                break;
            case "keyboardNav":
                this.keyboardNavEnabled = this.state.keyboardNav;
                break;
        }
    };

    AccessibilityManager.prototype.createReadingMask = function () {
        this.removeReadingMask();
        var overlay = document.createElement("div");
        overlay.id = "reading-mask-overlay";
        overlay.className = "active";
        overlay.innerHTML = '<div class="mask-top"></div><div class="mask-center"><div class="mask-line mask-line-top"></div><div class="mask-line mask-line-bottom"></div></div><div class="mask-bottom"></div>';
        document.body.appendChild(overlay);

        // Position the mask based on mouse position
        var self = this;
        this._maskMouseMove = function (e) {
            if (self.state.readingMask) {
                var lineHeight = 60;
                var top = e.clientY - lineHeight / 2;
                var maskTop = overlay.querySelector(".mask-top");
                var maskBottom = overlay.querySelector(".mask-bottom");
                var maskCenter = overlay.querySelector(".mask-center");
                if (maskTop) { maskTop.style.height = top + "px"; }
                if (maskBottom) { maskBottom.style.top = (top + lineHeight) + "px"; maskBottom.style.height = "100%"; }
                if (maskCenter) {
                    maskCenter.style.top = top + "px";
                    maskCenter.style.height = lineHeight + "px";
                }
            }
        };
        document.addEventListener("mousemove", this._maskMouseMove);
    };

    AccessibilityManager.prototype.removeReadingMask = function () {
        var mask = document.getElementById("reading-mask-overlay");
        if (mask) mask.remove();
        if (this._maskMouseMove) {
            document.removeEventListener("mousemove", this._maskMouseMove);
            this._maskMouseMove = null;
        }
    };

    AccessibilityManager.prototype.createReadingGuide = function () {
        this.removeReadingGuide();
        var guide = document.createElement("div");
        guide.id = "reading-guide-line";
        guide.className = "active";
        guide.innerHTML = '<div class="guide-line-horizontal"></div>';
        document.body.appendChild(guide);
        var self = this;
        this._guideMouseMove = function (e) {
            if (self.state.readingGuide) {
                guide.style.top = e.clientY + "px";
            }
        };
        document.addEventListener("mousemove", this._guideMouseMove);
    };

    AccessibilityManager.prototype.removeReadingGuide = function () {
        var guide = document.getElementById("reading-guide-line");
        if (guide) guide.remove();
        if (this._guideMouseMove) {
            document.removeEventListener("mousemove", this._guideMouseMove);
            this._guideMouseMove = null;
        }
    };

    AccessibilityManager.prototype.applyTextScale = function () {
        document.body.classList.remove("accesibilidad-text-resize-50", "accesibilidad-text-resize-100", "accesibilidad-text-resize-150", "accesibilidad-text-resize-200");
        document.body.classList.add("accesibilidad-text-resize-" + this.state.textScale);
    };

    AccessibilityManager.prototype.applySpacing = function () {
        document.body.style.lineHeight = this.state.lineSpacing;
        document.body.style.letterSpacing = this.state.letterSpacing + "px";
    };

    AccessibilityManager.prototype.disableScreenReader = function () {
        this.screenReaderActive = false;
        if (this.speechSynthesis) { this.speechSynthesis.cancel(); }
    };

    AccessibilityManager.prototype.toggleSkipToContent = function () {
        var existingLink = document.querySelector("#accesibility-skip-link");
        if (existingLink) existingLink.remove();
        if (this.state.skipToContent) {
            var skipLink = document.createElement("a");
            skipLink.id = "accesibility-skip-link";
            skipLink.href = "#main-content";
            skipLink.className = "accesibility-skip-link";
            skipLink.textContent = "Saltar al contenido principal";
            skipLink.setAttribute("aria-label", "Saltar al contenido principal");
            skipLink.addEventListener("click", function (e) {
                e.preventDefault();
                var mainContent = document.querySelector("#main-content") || document.querySelector(".principal");
                if (mainContent) {
                    mainContent.setAttribute("tabindex", "-1");
                    mainContent.focus();
                    mainContent.scrollIntoView({ behavior: "smooth" });
                }
            });
            document.body.insertBefore(skipLink, document.body.firstChild);
        }
    };

    AccessibilityManager.prototype.applyAllSettings = function () {
        var self = this;
        Object.keys(this.state).forEach(function (key) { self.applySetting(key); });
    };

    AccessibilityManager.prototype.improveAriaAttributes = function () {
        var menuBtn = document.getElementById("btn-menu");
        if (menuBtn) {
            menuBtn.setAttribute("aria-expanded", "false");
            menuBtn.setAttribute("aria-controls", "barra-lateral");
        }
        var sidebar = document.querySelector(".barra-lateral");
        if (sidebar) {
            sidebar.setAttribute("role", "navigation");
            sidebar.setAttribute("aria-label", "Barra de navegacion principal");
        }
    };

    AccessibilityManager.prototype.enableScreenReader = function () {
        if (this.screenReaderActive) return;
        this.screenReaderActive = true;
        // Only read page when user manually activates the toggle, not on page load
        if (!this.isInitialLoad) {
            var self = this;
            setTimeout(function () { self.readEntirePage(); }, 500);
        }
    };

    AccessibilityManager.prototype.readEntirePage = function () {
        if (!this.screenReaderActive) return;
        // Get all text nodes from the entire page
        var bodyText = this.extractTextFromNode(document.body);
        if (bodyText.trim()) {
            this.speak(bodyText);
        }
    };

    AccessibilityManager.prototype.extractTextFromNode = function (node) {
        var text = "";
        if (node.nodeType === Node.TEXT_NODE) {
            var trimmed = node.textContent.trim();
            if (trimmed) text += trimmed + ". ";
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Skip script, style, and hidden elements
            if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'NOSCRIPT') {
                return "";
            }
            if (node.offsetParent === null && node.style && node.style.display === 'none') {
                return "";
            }
            // Skip accessibility panel and skip links
            if (node.classList && (node.classList.contains('accesibilidad-panel') || node.classList.contains('accesibility-skip-link'))) {
                return "";
            }
            for (var i = 0; i < node.childNodes.length; i++) {
                text += this.extractTextFromNode(node.childNodes[i]);
            }
        }
        return text;
    };

    AccessibilityManager.prototype.speak = function (text) {
        if (!this.speechSynthesis) return;
        this.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "es-MX";
        utterance.rate = 0.9;
        this.speechSynthesis.speak(utterance);
    };

    AccessibilityManager.prototype.resetAll = function () {
        this.state = {
            grayscale: false, highContrast: false, invertColors: false,
            readingMask: false, readingGuide: false, highlightLinks: false,
            dyslexicFont: false, lightTheme: false, lineSpacing: 1.5,
            letterSpacing: 0, fontSize: 16, textScale: 100,
            screenReader: false, skipToContent: false,
            keyboardNav: false
        };
        this.currentScaleIndex = 1;
        this.removeReadingMask();
        this.removeReadingGuide();
        this.applyAllSettings();
        this.saveSettings();
        this.syncCheckboxes();
        var textScaleBtn = document.getElementById("acc-textScale");
        if (textScaleBtn) { textScaleBtn.textContent = "100%"; }
    };

    AccessibilityManager.prototype.saveSettings = function () {
        localStorage.setItem("accesibilitySettings", JSON.stringify(this.state));
    };

    AccessibilityManager.prototype.loadSettings = function () {
        var saved = localStorage.getItem("accesibilitySettings");
        if (saved) {
            try {
                var parsed = JSON.parse(saved);
                this.state = Object.assign({}, this.state, parsed);
            } catch (e) {
                console.error("Error loading settings:", e);
            }
        }
    };

    document.addEventListener("DOMContentLoaded", function () {
        window.accessibilityManager = new AccessibilityManager();
    });
})();
