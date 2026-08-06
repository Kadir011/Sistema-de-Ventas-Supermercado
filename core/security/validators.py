"""
Validadores reutilizables para registro y perfil:
- Cédula ecuatoriana (algoritmo módulo 10 oficial)
- Teléfono ecuatoriano (10 dígitos, formato nacional)
- Fortaleza de contraseña (estilo e-commerce: longitud + mayúscula + minúscula + número + símbolo)

Se usan tanto en los forms (backend) como espejados en JS (frontend) para
dar feedback en tiempo real sin depender de un roundtrip al servidor.
"""

import re
from django.core.exceptions import ValidationError


def validate_ecuadorian_cedula(value: str) -> None:
    """
    Valida una cédula ecuatoriana con el algoritmo oficial (módulo 10).
    Lanza ValidationError con un mensaje específico si falla.
    """
    if not value or not value.isdigit() or len(value) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos numéricos.')

    province = int(value[:2])
    if province < 1 or province > 24:
        raise ValidationError('El código de provincia de la cédula no es válido.')

    third_digit = int(value[2])
    if third_digit >= 6:
        raise ValidationError('La cédula ingresada no corresponde a una persona natural.')

    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for i, coef in enumerate(coefficients):
        product = int(value[i]) * coef
        if product > 9:
            product -= 9
        total += product

    verifier_digit = int(value[9])
    calculated = (10 - (total % 10)) % 10

    if calculated != verifier_digit:
        raise ValidationError('La cédula ingresada no es válida (dígito verificador incorrecto).')


def validate_ecuadorian_phone(value: str) -> None:
    """Valida un teléfono ecuatoriano: 10 dígitos, empieza en 0."""
    if not value or not value.isdigit() or len(value) != 10:
        raise ValidationError('El teléfono debe tener exactamente 10 dígitos numéricos.')
    if not value.startswith('0'):
        raise ValidationError('El teléfono debe empezar con 0 (formato nacional, ej. 0991234567).')


# Reglas de fortaleza de contraseña — deben coincidir 1:1 con las de
# static/js/password_strength.js para que el checklist visual y el
# rechazo del backend nunca se contradigan.
PASSWORD_RULES = [
    ('length', 'Al menos 8 caracteres', lambda p: len(p) >= 8),
    ('upper', 'Una letra mayúscula', lambda p: bool(re.search(r'[A-Z]', p))),
    ('lower', 'Una letra minúscula', lambda p: bool(re.search(r'[a-z]', p))),
    ('digit', 'Un número', lambda p: bool(re.search(r'[0-9]', p))),
    ('special', 'Un carácter especial (!@#$%^&*...)', lambda p: bool(re.search(r'[^A-Za-z0-9]', p))),
]


def validate_password_strength(value: str) -> None:
    """Exige longitud + mayúscula + minúscula + número + símbolo. Junta TODOS los errores, no solo el primero."""
    failed = [label for _, label, check in PASSWORD_RULES if not check(value)]
    if failed:
        raise ValidationError('Tu contraseña debe incluir: ' + ', '.join(failed) + '.')
