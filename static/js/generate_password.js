//script DOM para generar contraseña aleatoria 

document.addEventListener('DOMContentLoaded', () => {
    const password1 = document.getElementById('id_password1'); 

    // Función para generar contraseña aleatoria
    const generatePassword = () => {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=';
        let password = ''; 
        for (let i = 0; i < 12; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        password1.value = password;
    };

    // Asocia el evento al botón de sugerir contraseña
    document.getElementById('id_sugerir').addEventListener('click', generatePassword);
});

