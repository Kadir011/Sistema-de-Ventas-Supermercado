/*
 * Módulo único de notificaciones.
 * Cubre los dos sistemas del proyecto:
 *   1) Mensajes renderizados por Django ({% if messages %} en base.html)
 *   2) Toasts creados por JS al vuelo (showNotification), usados en
 *      shop.html y product_detail.html para las respuestas de fetch/AJAX.
 * Ambos casos: se pueden cerrar con la "x" y se autocierran a los 10s,
 * sin importar el rol del usuario ni el tipo de notificación.
 */

const NOTIFICATION_AUTO_DISMISS_MS = 10000;

/**
 * Cierra (con animación) y elimina del DOM una notificación.
 * Sirve tanto para el click en la "x" como para el auto-cierre.
 */
function dismissNotificationElement(el) {
    if (!el || el.dataset.dismissed === 'true') return;
    el.dataset.dismissed = 'true';

    if (el._notificationTimer) {
        clearTimeout(el._notificationTimer);
    }

    el.style.transition = 'opacity 0.25s ease, transform 0.25s ease, max-height 0.25s ease, margin 0.25s ease, padding 0.25s ease';
    el.style.maxHeight = el.offsetHeight + 'px';
    el.style.overflow = 'hidden';

    requestAnimationFrame(() => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        el.style.maxHeight = '0';
        el.style.marginTop = '0';
        el.style.marginBottom = '0';
        el.style.paddingTop = '0';
        el.style.paddingBottom = '0';
    });

    // Fallback por si el evento transitionend no dispara (p.ej. display:none previo)
    setTimeout(() => el.remove(), 350);
}

/**
 * Agrega botón de cierre + temporizador de 10s a una notificación existente.
 */
function initNotification(el) {
    if (!el || el.dataset.notificationInit === 'true') return;
    el.dataset.notificationInit = 'true';

    let closeBtn = el.querySelector('.js-notification-close');
    if (!closeBtn) {
        closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'js-notification-close';
        closeBtn.setAttribute('aria-label', 'Cerrar notificación');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.marginLeft = 'auto';
        closeBtn.style.background = 'transparent';
        closeBtn.style.border = 'none';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '1.1rem';
        closeBtn.style.lineHeight = '1';
        closeBtn.style.opacity = '0.6';
        closeBtn.style.flexShrink = '0';
        closeBtn.style.padding = '0 2px';
        closeBtn.addEventListener('mouseenter', () => { closeBtn.style.opacity = '1'; });
        closeBtn.addEventListener('mouseleave', () => { closeBtn.style.opacity = '0.6'; });
        el.appendChild(closeBtn);
    }

    closeBtn.addEventListener('click', () => dismissNotificationElement(el));

    el._notificationTimer = setTimeout(
        () => dismissNotificationElement(el),
        NOTIFICATION_AUTO_DISMISS_MS
    );
}

/**
 * Toast genérico usado por el JS de las páginas (carrito, etc).
 * Sustituye a las copias sueltas de showNotification() que había
 * en shop.html y en los dos product_detail.html.
 */
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `js-notification fixed top-20 right-4 z-50 flex items-center gap-3 px-4 py-3 pr-3 rounded-lg shadow-lg text-white animate-slide-in-right ${type === 'success' ? 'bg-green-600' : 'bg-red-600'}`;

    const text = document.createElement('span');
    text.textContent = message;
    notification.appendChild(text);

    document.body.appendChild(notification);
    initNotification(notification);
}
window.showNotification = showNotification;

document.addEventListener('DOMContentLoaded', function () {
    // Notificaciones renderizadas por el servidor (mensajes de Django)
    document.querySelectorAll('.js-notification').forEach(initNotification);
});