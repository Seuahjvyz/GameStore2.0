/**
 * Admin Modal Helpers - Working Version
 * Simple focus trapping that actually works
 */

(function() {
    "use strict";

    var openModals = [];

    // Prevent focus from escaping to elements outside modal
    document.addEventListener("focusin", function(e) {
        if (openModals.length === 0) return;

        var modal = openModals[openModals.length - 1];
        if (!modal || modal.style.display !== "block") return;

        // If focus moved outside modal, bring it back
        if (!modal.contains(e.target)) {
            e.preventDefault();
            e.target.blur();

            // Focus first element in modal (in DOM order)
            var list = getFocusableElements(modal);

            if (list.length > 0) {
                list[0].focus();
            }
        }
    }, true);

    // Global Tab trap - capture phase
    document.addEventListener("keydown", function(e) {
        if (e.key !== "Tab" || openModals.length === 0) return;

        var modal = openModals[openModals.length - 1];
        if (!modal) return;

        // Check if modal is visible (not display:none or visibility:hidden)
        var isVisible = modal.offsetParent !== null ||
                       modal.style.display === "block" ||
                       modal.style.display === "" ||
                       modal.classList.contains("show") ||
                       modal.classList.contains("active");

        if (!isVisible) return;

        e.preventDefault();

        // Get all focusable elements in DOM order
        var list = getFocusableElements(modal);

        if (list.length === 0) return;

        var first = list[0];
        var last = list[list.length - 1];

        // If focus is outside modal or on last element with Tab
        if (document.activeElement === last || !modal.contains(document.activeElement)) {
            first.focus();
        } else if (document.activeElement === first && e.shiftKey) {
            last.focus();
        } else {
            // Find current position and move forward with Tab
            if (!e.shiftKey) {
                var found = false;
                for (var i = 0; i < list.length - 1; i++) {
                    if (document.activeElement === list[i]) {
                        list[i + 1].focus();
                        found = true;
                        return;
                    }
                }
                // If not found, focus first element
                if (!found) list[0].focus();
            } else {
                // Move backward with Shift+Tab
                var foundShift = false;
                for (var j = 1; j < list.length; j++) {
                    if (document.activeElement === list[j]) {
                        list[j - 1].focus();
                        foundShift = true;
                        return;
                    }
                }
                // If not found, focus last element
                if (!foundShift) list[list.length - 1].focus();
            }
        }
    }, true);

    // Function to get all focusable elements in DOM order
    function getFocusableElements(modal) {
        var focusableSelectors = [
            'button:not([disabled]):not([tabindex="-1"])',
            'input:not([disabled]):not([tabindex="-1"])',
            'select:not([disabled]):not([tabindex="-1"])',
            'textarea:not([disabled]):not([tabindex="-1"])',
            'a[href]:not([tabindex="-1"])',
            '[tabindex]:not([tabindex="-1"])'
        ];

        var elements = modal.querySelectorAll(focusableSelectors.join(', '));
        var list = [];

        for (var i = 0; i < elements.length; i++) {
            if (elements[i].offsetParent !== null) {
                list.push(elements[i]);
            }
        }

        return list;
    }

    function setupModalKeyboardNav(modal) {
        if (!modal) return;

        modal.setAttribute("role", "dialog");
        modal.setAttribute("aria-modal", "true");
        modal.setAttribute("aria-hidden", "true");

        var savedFocus = null;

        function onOpen() {
            if (openModals.indexOf(modal) === -1) {
                openModals.push(modal);
            }
            savedFocus = document.activeElement;
            modal.setAttribute("aria-hidden", "false");
            document.body.style.overflow = "hidden";

            setTimeout(function() {
                // Get focusable elements in DOM order
                var list = getFocusableElements(modal);

                if (list.length > 0) {
                    list[0].focus();
                } else {
                    modal.setAttribute("tabindex", "-1");
                    modal.focus();
                }
            }, 100);
        }

        function onClose() {
            modal.setAttribute("aria-hidden", "true");
            document.body.style.overflow = "";
            var idx = openModals.indexOf(modal);
            if (idx > -1) {
                openModals.splice(idx, 1);
            }
            if (savedFocus && savedFocus.focus) {
                savedFocus.focus();
            }
        }

        // Watch for display changes
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                if (m.type === "attributes") {
                    if (m.attributeName === "style" && modal.style.display === "block") {
                        onOpen();
                    }
                    // Also check for class changes (some modals use classes like 'show')
                    if (m.attributeName === "class") {
                        if (modal.classList.contains("show") || modal.classList.contains("active") || modal.style.display === "block") {
                            if (modal.offsetParent !== null) {
                                onOpen();
                            }
                        }
                    }
                }
            });
        });
        observer.observe(modal, { attributes: true });

        // Escape key
        modal.addEventListener("keydown", function(e) {
            if (e.key === "Escape" && modal.style.display === "block") {
                e.preventDefault();
                modal.style.display = "none";
                onClose();
            }
        });
    }

    function setupModalClickOutside(modal) {
        if (!modal) return;
        window.addEventListener("click", function(e) {
            if (e.target === modal) {
                modal.style.display = "none";
                modal.setAttribute("aria-hidden", "true");
                document.body.style.overflow = "";
            }
        });
    }

    function setupModalCloseButtons(modal, selectors) {
        if (!modal) return;
        selectors = selectors || [".close-modal", ".modal-close", ".btn-secondary", ".modal-cerrar", ".btn-cancelar"];
        selectors.forEach(function(sel) {
            var buttons = modal.querySelectorAll(sel);
            for (var i = 0; i < buttons.length; i++) {
                (function(btn) {
                    btn.addEventListener("click", function() {
                        modal.style.display = "none";
                        modal.setAttribute("aria-hidden", "true");
                        document.body.style.overflow = "";
                    });
                })(buttons[i]);
            }
        });
    }

    // Expose functions globally
    window.setupModalKeyboardNav = setupModalKeyboardNav;
    window.setupModalClickOutside = setupModalClickOutside;
    window.setupModalCloseButtons = setupModalCloseButtons;
})();
