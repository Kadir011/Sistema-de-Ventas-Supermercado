//script DOM para generar contraseña aleatoria 
document.addEventListener('DOMContentLoaded', () => {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');

    // Función para generar contraseña aleatoria
    const generatePassword = () => {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=';
        let password = ''; 
        for (let i = 0; i < 12; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        // Rellenar ambos campos de contraseña
        if (password1) password1.value = password;
        if (password2) password2.value = password;
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