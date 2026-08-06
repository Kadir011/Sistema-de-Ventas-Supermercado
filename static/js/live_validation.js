/**
 * Validación visual en tiempo real: fortaleza de contraseña, cédula
 * ecuatoriana y teléfono. Espeja EXACTAMENTE las reglas del backend
 * (core/security/validators.py) — si cambias una regla ahí, cámbiala
 * también aquí, o el checklist puede decir "válido" y el backend rechazarlo.
 *
 * Convención de activación (no requiere tocar cada template más de una vez):
 *   - Contraseña:  agregar atributo  data-password-strength  al <input>
 *   - Cédula:      cualquier <input name="dni">              (automático)
 *   - Teléfono:    cualquier <input name="phone_number">     (automático)
 */
document.addEventListener('DOMContentLoaded', function () {
    initPasswordStrengthFields();
    initPasswordMatchFields();
    initCedulaFields();
    initPhoneFields();
});

/* ────────────────────────────────────────────────────────────────
   CONFIRMACIÓN DE CONTRASEÑA — barra + mensaje de coincidencia en vivo
   Activación: <input data-password-match="id_del_input_original">
   ──────────────────────────────────────────────────────────────── */

function initPasswordMatchFields() {
    document.querySelectorAll('[data-password-match]').forEach(confirmInput => {
        const originalInput = document.getElementById(confirmInput.dataset.passwordMatch);
        if (!originalInput) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'pw-match-wrap';
        wrapper.innerHTML = `
            <div class="pw-strength-bar-track">
                <div class="pw-match-bar-fill" style="width:0%"></div>
            </div>
            <span class="field-live-feedback"></span>
        `;
        confirmInput.insertAdjacentElement('afterend', wrapper);

        const bar = wrapper.querySelector('.pw-match-bar-fill');
        const feedback = wrapper.querySelector('.field-live-feedback');

        const checkMatch = () => {
            const original = originalInput.value;
            const confirm = confirmInput.value;

            confirmInput.classList.remove('border-red-500', 'border-green-500');

            if (confirm.length === 0) {
                bar.style.width = '0%';
                bar.className = 'pw-match-bar-fill';
                feedback.textContent = '';
                feedback.className = 'field-live-feedback';
                return;
            }

            const matches = confirm === original;
            // Progreso parcial: cuánto del texto coincide desde el inicio,
            // para que la barra avance mientras escribes en vez de saltar de 0 a 100.
            let matchingChars = 0;
            while (matchingChars < confirm.length && confirm[matchingChars] === original[matchingChars]) {
                matchingChars++;
            }
            const pct = original.length > 0 ? Math.min(100, (matchingChars / original.length) * 100) : 0;

            bar.style.width = pct + '%';

            if (matches && original.length > 0) {
                bar.className = 'pw-match-bar-fill pw-bar--strong';
                feedback.innerHTML = "<i class='bx bx-check-circle'></i> Las contraseñas coinciden";
                feedback.className = 'field-live-feedback field-live-feedback--ok';
                confirmInput.classList.add('border-green-500');
            } else {
                bar.className = 'pw-match-bar-fill pw-bar--weak';
                feedback.innerHTML = "<i class='bx bx-x-circle'></i> Las contraseñas no coinciden";
                feedback.className = 'field-live-feedback field-live-feedback--fail';
                confirmInput.classList.add('border-red-500');
            }
        };

        confirmInput.addEventListener('input', checkMatch);
        // Si el usuario cambia la contraseña original después de haber escrito
        // la confirmación, revalidamos también (evita un falso "coincide").
        originalInput.addEventListener('input', () => {
            if (confirmInput.value.length > 0) checkMatch();
        });
    });
}

/* ────────────────────────────────────────────────────────────────
   CONTRASEÑA — checklist animado + barra de fortaleza
   ──────────────────────────────────────────────────────────────── */

const PASSWORD_RULES = [
    { id: 'length',  label: 'Al menos 8 caracteres',        test: p => p.length >= 8 },
    { id: 'upper',   label: 'Una letra mayúscula',           test: p => /[A-Z]/.test(p) },
    { id: 'lower',   label: 'Una letra minúscula',           test: p => /[a-z]/.test(p) },
    { id: 'digit',   label: 'Un número',                     test: p => /[0-9]/.test(p) },
    { id: 'special', label: 'Un carácter especial (!@#$...)', test: p => /[^A-Za-z0-9]/.test(p) },
];

function initPasswordStrengthFields() {
    document.querySelectorAll('[data-password-strength]').forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'pw-strength-wrap';
        wrapper.innerHTML = `
            <div class="pw-strength-bar-track">
                <div class="pw-strength-bar-fill" style="width:0%"></div>
            </div>
            <ul class="pw-strength-checklist">
                ${PASSWORD_RULES.map(r => `
                    <li data-rule="${r.id}" class="pw-rule pw-rule--pending">
                        <i class='bx bx-circle'></i><span>${r.label}</span>
                    </li>
                `).join('')}
            </ul>
        `;
        input.insertAdjacentElement('afterend', wrapper);

        const bar = wrapper.querySelector('.pw-strength-bar-fill');
        const ruleEls = {};
        PASSWORD_RULES.forEach(r => {
            ruleEls[r.id] = wrapper.querySelector(`[data-rule="${r.id}"]`);
        });

        input.addEventListener('input', () => {
            const value = input.value;
            let passedCount = 0;

            PASSWORD_RULES.forEach(rule => {
                const passed = rule.test(value);
                const el = ruleEls[rule.id];
                if (passed) passedCount++;

                el.classList.remove('pw-rule--pending', 'pw-rule--ok', 'pw-rule--fail');
                el.classList.add(value.length === 0 ? 'pw-rule--pending' : (passed ? 'pw-rule--ok' : 'pw-rule--fail'));
                el.querySelector('i').className = value.length === 0
                    ? 'bx bx-circle'
                    : (passed ? 'bx bx-check-circle' : 'bx bx-x-circle');
            });

            const pct = (passedCount / PASSWORD_RULES.length) * 100;
            bar.style.width = pct + '%';
            bar.className = 'pw-strength-bar-fill ' +
                (pct < 40 ? 'pw-bar--weak' : pct < 100 ? 'pw-bar--medium' : 'pw-bar--strong');

            input.classList.remove('border-red-500', 'border-green-500', 'border-yellow-500');
            if (value.length > 0) {
                input.classList.add(passedCount === PASSWORD_RULES.length ? 'border-green-500'
                    : passedCount >= 3 ? 'border-yellow-500' : 'border-red-500');
            }
        });
    });
}

/* ────────────────────────────────────────────────────────────────
   CÉDULA ECUATORIANA — algoritmo módulo 10, feedback en vivo
   ──────────────────────────────────────────────────────────────── */

function isValidEcuadorianCedula(value) {
    if (!/^\d{10}$/.test(value)) return false;

    const province = parseInt(value.substring(0, 2), 10);
    if (province < 1 || province > 24) return false;

    const thirdDigit = parseInt(value[2], 10);
    if (thirdDigit >= 6) return false;

    const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    let total = 0;
    for (let i = 0; i < 9; i++) {
        let product = parseInt(value[i], 10) * coefficients[i];
        if (product > 9) product -= 9;
        total += product;
    }
    const verifier = parseInt(value[9], 10);
    const calculated = (10 - (total % 10)) % 10;
    return calculated === verifier;
}

function initCedulaFields() {
    document.querySelectorAll('input[name="dni"]').forEach(input => {
        const feedback = document.createElement('span');
        feedback.className = 'field-live-feedback';
        input.insertAdjacentElement('afterend', feedback);

        input.addEventListener('input', () => {
            const value = input.value.replace(/\D/g, '');
            input.classList.remove('border-red-500', 'border-green-500');

            if (value.length === 0) {
                feedback.textContent = '';
                return;
            }
            if (value.length < 10) {
                feedback.textContent = `Faltan ${10 - value.length} dígitos`;
                feedback.className = 'field-live-feedback field-live-feedback--pending';
                return;
            }
            if (isValidEcuadorianCedula(value)) {
                input.classList.add('border-green-500');
                feedback.innerHTML = "<i class='bx bx-check-circle'></i> Cédula válida";
                feedback.className = 'field-live-feedback field-live-feedback--ok';
            } else {
                input.classList.add('border-red-500');
                feedback.innerHTML = "<i class='bx bx-x-circle'></i> Cédula inválida";
                feedback.className = 'field-live-feedback field-live-feedback--fail';
            }
        });
    });
}

/* ────────────────────────────────────────────────────────────────
   TELÉFONO ECUATORIANO — 10 dígitos, empieza en 0
   ──────────────────────────────────────────────────────────────── */

function isValidEcuadorianPhone(value) {
    return /^0\d{9}$/.test(value);
}

function initPhoneFields() {
    document.querySelectorAll('input[name="phone_number"]').forEach(input => {
        const feedback = document.createElement('span');
        feedback.className = 'field-live-feedback';
        input.insertAdjacentElement('afterend', feedback);

        input.addEventListener('input', () => {
            const value = input.value.replace(/\D/g, '');
            input.classList.remove('border-red-500', 'border-green-500');

            if (value.length === 0) {
                feedback.textContent = '';
                return;
            }
            if (value.length < 10) {
                feedback.textContent = `Faltan ${10 - value.length} dígitos`;
                feedback.className = 'field-live-feedback field-live-feedback--pending';
                return;
            }
            if (isValidEcuadorianPhone(value)) {
                input.classList.add('border-green-500');
                feedback.innerHTML = "<i class='bx bx-check-circle'></i> Teléfono válido";
                feedback.className = 'field-live-feedback field-live-feedback--ok';
            } else {
                input.classList.add('border-red-500');
                feedback.innerHTML = "<i class='bx bx-x-circle'></i> Debe empezar con 0";
                feedback.className = 'field-live-feedback field-live-feedback--fail';
            }
        });
    });
}