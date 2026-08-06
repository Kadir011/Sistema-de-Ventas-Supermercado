//script DOM para generar contraseña aleatoria 
document.addEventListener('DOMContentLoaded', () => {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');

    // Función para generar contraseña aleatoria — garantiza al menos un
    // carácter de cada categoría exigida por el checklist (mayúscula,
    // minúscula, número, símbolo), para que SIEMPRE pase las reglas.
    const generatePassword = () => {
        const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const lower = 'abcdefghijklmnopqrstuvwxyz';
        const digits = '0123456789';
        const special = '!@#$%^&*()_+-=';
        const all = upper + lower + digits + special;

        const pick = (set) => set.charAt(Math.floor(Math.random() * set.length));

        let chars = [pick(upper), pick(lower), pick(digits), pick(special)];
        for (let i = chars.length; i < 12; i++) {
            chars.push(pick(all));
        }
        // Barajar para que no siempre empiece con Mayúscula-minúscula-número-símbolo
        for (let i = chars.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [chars[i], chars[j]] = [chars[j], chars[i]];
        }
        const password = chars.join('');

        // Rellenar ambos campos y disparar 'input' para que el checklist
        // de fortaleza (live_validation.js) se actualice visualmente.
        if (password1) {
            password1.value = password;
            password1.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (password2) {
            password2.value = password;
            password2.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };

    // Asocia el evento al enlace de sugerir contraseña
    const sugerirPassword = document.getElementById('id_sugerir');
    if (sugerirPassword) {
        sugerirPassword.addEventListener('click', (e) => {
            e.preventDefault();
            generatePassword();
        });
    }
});
