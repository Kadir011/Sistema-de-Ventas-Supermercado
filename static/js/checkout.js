/* ══════════════════════════════════════════
   checkout.js
   CRÍTICO corregido: eliminadas todas las etiquetas Django template
   ({{ total|stringformat }}) de este archivo estático. Ahora los
   valores numéricos se leen desde data-attributes del DOM, que sí
   son procesados por Django en el template HTML.
══════════════════════════════════════════ */

/* ── Leer valores del DOM (inyectados por Django en el template) ── */
function getCheckoutData() {
    const el = document.getElementById('checkout-data');
    if (!el) return { total: 0, subtotal: 0, iva: 0, discount: 0 };
    return {
        total: parseFloat(el.dataset.total || 0),
        subtotal: parseFloat(el.dataset.subtotal || 0),
        iva: parseFloat(el.dataset.iva || 0),
        discount: parseFloat(el.dataset.discount || 0),
    };
}

/* ══════════════════════════════════════════
   CONSTANTES
══════════════════════════════════════════ */
const ACTIVE_PAYMENT_METHODS = [
    'Efectivo',
    'Tarjeta de crédito',
    'Tarjeta de débito',
];

const CARD_NETWORKS = [
    {
        name: 'Visa',
        logo: 'logo_visa',
        gradient: 'linear-gradient(135deg,#1A1F71 0%,#2563eb 100%)',
        regex: /^4/,
        lengths: [13, 16, 19]
    },
    {
        name: 'Mastercard',
        logo: 'logo_mastercard',
        gradient: 'linear-gradient(135deg,#1c1c1c 0%,#eb001b 60%,#f79e1b 100%)',
        regex: /^5[1-5]|^2[2-7]/,
        lengths: [16]
    },
    {
        name: 'American Express',
        logo: 'logo_amex',
        gradient: 'linear-gradient(135deg,#007bc1 0%,#00b4d8 100%)',
        regex: /^3[47]/,
        lengths: [15]
    },
    {
        name: 'Discover',
        logo: 'logo_discover',
        gradient: 'linear-gradient(135deg,#f76f20 0%,#fbbf24 100%)',
        regex: /^6(?:011|5|4[4-9]|22)/,
        lengths: [16, 19]
    },
];

let currentNetwork = null;
let luhnValid = false;

/* ══════════════════════════════════════════
   ALGORITMO DE LUHN
══════════════════════════════════════════ */
function luhnCheck(number) {
    const digits = number.replace(/\s/g, '');
    if (!/^\d+$/.test(digits)) return false;
    let sum = 0, shouldDouble = false;
    for (let i = digits.length - 1; i >= 0; i--) {
        let d = parseInt(digits[i], 10);
        if (shouldDouble) { d *= 2; if (d > 9) d -= 9; }
        sum += d;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
}

/* ══════════════════════════════════════════
   DETECCIÓN DE RED
══════════════════════════════════════════ */
function detectNetwork(digits) {
    for (const net of CARD_NETWORKS) {
        if (net.regex.test(digits)) return net;
    }
    return null;
}

/* ══════════════════════════════════════════
   FORMATEO
══════════════════════════════════════════ */
function formatNumber(raw, net) {
    const d = raw.replace(/\D/g, '');
    if (net && net.name === 'American Express') {
        return [d.slice(0, 4), d.slice(4, 10), d.slice(10, 15)].filter(Boolean).join(' ');
    }
    return d.match(/.{1,4}/g)?.join(' ') ?? d;
}

/* ══════════════════════════════════════════
   INPUT: NÚMERO DE TARJETA
══════════════════════════════════════════ */
function onCardNumberInput(input) {
    const raw = input.value.replace(/\D/g, '');
    const net = detectNetwork(raw);
    currentNetwork = net;

    const maxLen = net ? Math.max(...net.lengths) : 16;
    const trimmed = raw.slice(0, maxLen);

    input.value = formatNumber(trimmed, net);
    input.maxLength = net?.name === 'American Express' ? 17 : 19;

    updateNetworkUI(net);

    const pct = Math.min((trimmed.length / maxLen) * 100, 100);
    const bar = document.getElementById('card_progress');
    bar.style.width = pct + '%';
    bar.className = 'h-full rounded-full transition-all duration-300 ' +
        (pct < 50 ? 'bg-red-400' : pct < 100 ? 'bg-yellow-400' : 'bg-green-500');

    const icon = document.getElementById('luhn_icon');
    const msg = document.getElementById('luhn_msg');

    const isValidLength = net && net.lengths.includes(trimmed.length);

    if (isValidLength) {
        luhnValid = luhnCheck(trimmed);
        icon.classList.remove('hidden');
        msg.classList.remove('hidden');
        if (luhnValid) {
            icon.textContent = '✅';
            msg.textContent = 'Número de tarjeta válido.';
            msg.className = 'text-xs mt-1 text-green-600';
            input.classList.replace('border-red-400', 'border-green-400');
            input.classList.add('border-green-400');
        } else {
            icon.textContent = '❌';
            msg.textContent = 'Número de tarjeta inválido (falla verificación Luhn).';
            msg.className = 'text-xs mt-1 text-red-600';
            input.classList.replace('border-green-400', 'border-red-400');
            input.classList.add('border-red-400');
        }
    } else {
        luhnValid = false;
        icon.classList.add('hidden');
        msg.classList.add('hidden');
        input.classList.remove('border-green-400', 'border-red-400');
    }

    updateCardPreview();
}

/* ══════════════════════════════════════════
   UI DE RED
══════════════════════════════════════════ */
function updateNetworkUI(net) {
    const all = ['logo_visa', 'logo_mastercard', 'logo_amex', 'logo_discover'];
    const badge = document.getElementById('card_network_badge');
    const badgeName = document.getElementById('card_network_name');
    const preview = document.getElementById('card_preview');

    all.forEach(id => {
        const el = document.getElementById(id);
        if (net && id === net.logo) {
            el.classList.remove('opacity-30');
            el.classList.add('opacity-100', 'scale-110', 'drop-shadow-md');
        } else {
            el.classList.add('opacity-30');
            el.classList.remove('opacity-100', 'scale-110', 'drop-shadow-md');
        }
    });

    if (net) {
        badge.classList.remove('hidden');
        badgeName.textContent = net.name;
        preview.style.background = net.gradient;
    } else {
        badge.classList.add('hidden');
        preview.style.background = 'linear-gradient(135deg,#1a1f71 0%,#2563eb 100%)';
    }
}

/* ══════════════════════════════════════════
   PREVIEW EN TIEMPO REAL
══════════════════════════════════════════ */
function updateCardPreview() {
    const raw = document.getElementById('card_number').value.replace(/\D/g, '');
    const holder = document.getElementById('card_holder').value || 'NOMBRE APELLIDO';
    const expiry = document.getElementById('card_expiry').value || 'MM/AA';

    const isAmex = currentNetwork?.name === 'American Express';
    const maxLen = isAmex ? 15 : 16;
    const padded = raw.padEnd(maxLen, '•');
    const fmt = isAmex
        ? padded.slice(0, 4) + ' ' + padded.slice(4, 10) + ' ' + padded.slice(10, 15)
        : padded.match(/.{1,4}/g)?.join(' ') ?? padded;

    document.getElementById('preview_number').textContent = fmt;
    document.getElementById('preview_holder').textContent = holder.toUpperCase();
    document.getElementById('preview_expiry').textContent = expiry;
    document.getElementById('preview_network').textContent = currentNetwork?.name ?? '';
}

/* ══════════════════════════════════════════
   INPUT: FECHA DE VENCIMIENTO
══════════════════════════════════════════ */
function onExpiryInput(input) {
    let v = input.value.replace(/\D/g, '');
    if (v.length >= 2) v = v.slice(0, 2) + '/' + v.slice(2, 4);
    input.value = v;

    const msg = document.getElementById('expiry_msg');
    if (v.length === 5) {
        const [mm, yy] = v.split('/').map(Number);
        const now = new Date();
        const exp = new Date(2000 + yy, mm - 1, 1);
        const ok = mm >= 1 && mm <= 12 && exp >= new Date(now.getFullYear(), now.getMonth(), 1);

        if (!ok) {
            msg.textContent = 'Fecha inválida o tarjeta expirada.';
            msg.classList.remove('hidden');
            input.classList.add('border-red-400');
            input.classList.remove('border-green-400');
        } else {
            msg.classList.add('hidden');
            input.classList.add('border-green-400');
            input.classList.remove('border-red-400');
        }
    } else {
        msg.classList.add('hidden');
        input.classList.remove('border-red-400', 'border-green-400');
    }
    updateCardPreview();
}

/* ══════════════════════════════════════════
   CAMBIO DE MÉTODO DE PAGO
══════════════════════════════════════════ */
function onPaymentChange(sel) {
    const text = sel.options[sel.selectedIndex].text.trim();
    const notice = document.getElementById('payment_unavailable_notice');
    const btn = document.getElementById('submit_btn');
    const cardSec = document.getElementById('card_section');
    const cashSec = document.getElementById('cash_received_section');
    const amtInput = document.getElementById('amount_received');
    const changeSec = document.getElementById('change_display');

    /* Leer el total real desde el DOM (CRÍTICO — ya no usa template tag en JS) */
    const { total } = getCheckoutData();

    const isActive = sel.value === '' || ACTIVE_PAYMENT_METHODS.includes(text);

    if (!isActive) {
        notice.classList.remove('hidden');
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
        cardSec.classList.add('hidden');
        return;
    }

    notice.classList.add('hidden');
    btn.disabled = false;
    btn.classList.remove('opacity-50', 'cursor-not-allowed');

    const isCard = text === 'Tarjeta de crédito' || text === 'Tarjeta de débito';
    const isTransfer = text === 'Transferencia bancaria';
    const transferSec = document.getElementById('transfer_section');

    if (isCard) {
        cardSec.classList.remove('hidden');
        if (transferSec) transferSec.classList.add('hidden');
        cashSec.classList.add('hidden');
        changeSec.classList.add('hidden');
        amtInput.value = total.toFixed(2);
        document.getElementById('card_type_label').textContent =
            text === 'Tarjeta de crédito' ? '— Crédito' : '— Débito';
    } else if (isTransfer) {
        if (transferSec) transferSec.classList.remove('hidden');
        cardSec.classList.add('hidden');
        cashSec.classList.add('hidden');
        changeSec.classList.add('hidden');
        amtInput.value = total.toFixed(2);
        document.querySelectorAll('input[name="transfer_bank"]').forEach(r => r.checked = false);
        document.querySelectorAll('input[name="transfer_account_type"]').forEach(r => r.checked = false);
        const acType = document.getElementById('transfer_account_type_section');
        const acInfo = document.getElementById('transfer_account_info');
        if (acType) acType.classList.add('hidden');
        if (acInfo) acInfo.classList.add('hidden');
    } else {
        cardSec.classList.add('hidden');
        if (transferSec) transferSec.classList.add('hidden');
        cashSec.classList.remove('hidden');
        amtInput.value = '';
    }
}

/* ══════════════════════════════════════════
   TRANSFERENCIA BANCARIA
══════════════════════════════════════════ */
const TRANSFER_ACCOUNTS = {
    guayaquil: {
        name: 'Banco de Guayaquil',
        ahorros: '0016823516',
        corriente: '0024571839',
    },
    pichincha: {
        name: 'Banco Pichincha',
        ahorros: '2209440206',
        corriente: '2201938475',
    }
};

function onTransferBankChange() {
    const acType = document.getElementById('transfer_account_type_section');
    if (acType) acType.classList.remove('hidden');
    document.querySelectorAll('input[name="transfer_account_type"]').forEach(r => r.checked = false);
    const acInfo = document.getElementById('transfer_account_info');
    if (acInfo) acInfo.classList.add('hidden');
    document.getElementById('transfer_account_number_input').value = '';
}

function onTransferAccountTypeChange() {
    const bankVal = document.querySelector('input[name="transfer_bank"]:checked')?.value;
    const typeVal = document.querySelector('input[name="transfer_account_type"]:checked')?.value;
    if (!bankVal || !typeVal) return;

    const { total } = getCheckoutData();
    const bank = TRANSFER_ACCOUNTS[bankVal];
    const number = bank[typeVal];
    const typeName = typeVal === 'ahorros' ? 'Cuenta de Ahorros' : 'Cuenta Corriente';

    document.getElementById('tinfo_bank').textContent = bank.name;
    document.getElementById('tinfo_type').textContent = typeName;
    document.getElementById('tinfo_amount').textContent = '$' + total.toFixed(2);

    const numberInput = document.getElementById('transfer_account_number_input');
    numberInput.value = number;

    document.getElementById('transfer_bank_name').value = bank.name;
    document.getElementById('transfer_account_number').value = number;
    document.getElementById('transfer_account_type_value').value = typeName;

    const acInfo = document.getElementById('transfer_account_info');
    if (acInfo) acInfo.classList.remove('hidden');
}

function updateTransferAccountNumber() {
    const accountNumber = document.getElementById('transfer_account_number_input').value;
    document.getElementById('transfer_account_number').value = accountNumber;
}

/* ══════════════════════════════════════════
   TOGGLE TIPO FACTURA
══════════════════════════════════════════ */
function toggleDniField(val) {
    const section = document.getElementById('customer_data_section');
    const dniInput = document.getElementById('id_dni_input');
    const paySel = document.getElementById('id_payment_method');
    const note = document.getElementById('payment_note');
    const btn = document.getElementById('submit_btn');

    if (val === 'final') {
        section.classList.add('hidden');
        dniInput.removeAttribute('required');
        for (const opt of paySel.options) {
            if (opt.getAttribute('data-cash') === 'true') { paySel.value = opt.value; break; }
        }
        paySel.classList.add('bg-gray-100', 'cursor-not-allowed');
        paySel.style.pointerEvents = 'none';
        note.classList.remove('hidden');

        document.getElementById('payment_unavailable_notice').classList.add('hidden');
        document.getElementById('card_section').classList.add('hidden');
        const ts = document.getElementById('transfer_section');
        if (ts) ts.classList.add('hidden');
        document.getElementById('cash_received_section').classList.remove('hidden');
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
        section.classList.remove('hidden');
        dniInput.setAttribute('required', 'required');
        paySel.classList.remove('bg-gray-100', 'cursor-not-allowed');
        paySel.style.pointerEvents = 'auto';
        note.classList.add('hidden');
        onPaymentChange(paySel);
    }
}

/* ══════════════════════════════════════════
   VUELTO
   CRÍTICO corregido: lee el total desde DOM, no desde template tag
══════════════════════════════════════════ */
function calculateChange() {
    const { total } = getCheckoutData();
    const recv = parseFloat(document.getElementById('amount_received').value) || 0;
    const sec = document.getElementById('change_display');
    const txt = document.getElementById('change_amount_text');
    if (recv >= total) {
        txt.textContent = '$' + (recv - total).toFixed(2);
        sec.classList.remove('hidden');
    } else {
        sec.classList.add('hidden');
    }
}

/* ══════════════════════════════════════════
   FUNCIONES DE CENSURA
══════════════════════════════════════════ */
function maskCardNumber(cardNumber) {
    const digits = cardNumber.replace(/\D/g, '');
    if (digits.length < 4) return digits;
    const first4 = digits.slice(0, 4);
    const last4 = digits.slice(-4);
    return first4 + ' XXXX XXXX ' + last4;
}

function maskAccountNumber(accountNumber) {
    const digits = accountNumber.replace(/\D/g, '');
    if (digits.length < 3) return digits;
    return 'XXX' + digits.slice(-3);
}

/* ══════════════════════════════════════════
   VALIDACIÓN AL SUBMIT
══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkout-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        const sel = document.getElementById('id_payment_method');
        const text = sel.options[sel.selectedIndex].text.trim();
        const isCard = text === 'Tarjeta de crédito' || text === 'Tarjeta de débito';
        const isTransfer = text === 'Transferencia bancaria';
        const errors = [];

        if (isCard) {
            const cardRaw = document.getElementById('card_number').value.replace(/\D/g, '');
            if (!luhnCheck(cardRaw))
                errors.push('El número de tarjeta no pasó la validación Luhn.');

            if (!document.getElementById('card_holder').value.trim())
                errors.push('Ingrese el nombre del titular.');

            const exp = document.getElementById('card_expiry').value;
            if (exp.length < 5) {
                errors.push('Ingrese la fecha de vencimiento (MM/AA).');
            } else {
                const [mm, yy] = exp.split('/').map(Number);
                const now = new Date();
                const expDate = new Date(2000 + yy, mm - 1, 1);
                if (mm < 1 || mm > 12 || expDate < new Date(now.getFullYear(), now.getMonth(), 1))
                    errors.push('La fecha de vencimiento es inválida o la tarjeta está expirada.');
            }

            if (!document.getElementById('card_bank').value)
                errors.push('Seleccione el banco emisor.');

            if (!document.getElementById('card_voucher').value.trim())
                errors.push('Ingrese el número de autorización/voucher.');

            const cardNumber = document.getElementById('card_number').value;
            document.getElementById('card_number_masked').value = maskCardNumber(cardNumber);
        }

        if (isTransfer) {
            if (!document.querySelector('input[name="transfer_bank"]:checked'))
                errors.push('Seleccione el banco destino para la transferencia.');
            if (!document.querySelector('input[name="transfer_account_type"]:checked'))
                errors.push('Seleccione el tipo de cuenta para la transferencia.');

            const accountNumber = document.getElementById('transfer_account_number_input').value.trim();
            if (!accountNumber)
                errors.push('Ingrese el número de cuenta.');
            else if (!/^\d+$/.test(accountNumber))
                errors.push('El número de cuenta debe contener solo dígitos.');

            document.getElementById('transfer_account_masked').value = maskAccountNumber(accountNumber);
        }

        if (errors.length > 0) {
            e.preventDefault();
            alert('Corrija los siguientes errores:\n\n• ' + errors.join('\n• '));
        }
    });

    /* Init */
    toggleDniField('final');
});