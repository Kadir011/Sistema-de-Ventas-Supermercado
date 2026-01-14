# My Supermarket - Sistema de Ventas y Tienda E-Commerce

## Descripcion
Este proyecto es una plataforma integral de comercio electronico y gestion interna para un supermercado. El sistema permite a los usuarios navegar por un catalogo de productos, gestionar un carrito de compras y realizar pedidos. Ademas, cuenta con un panel administrativo robusto para la gestion de inventario, ventas y clientes, integrando herramientas avanzadas como un escaner de codigos de barras y un asistente virtual basado en inteligencia artificial.

## Caracteristicas Principales

### Modulo de Cliente
* **Catalogo Dinamico**: Visualizacion de productos con filtros por categoria y marca.
* **Carrito de Compras**: Gestion de items, actualizacion de cantidades y calculo automatico de totales e impuestos.
* **Proceso de Checkout**: Opcion de compra como Consumidor Final (DNI generico) o con datos personales para facturacion.
* **Mis Compras**: Historial detallado de pedidos realizados por el usuario autenticado.
* **Contacto**: Formulario funcional que envia mensajes directamente al correo electronico del administrador a traves de Gmail.

### Asistente y Herramientas
* **Chatbot IA**: Asistente virtual integrado con la API de Google Gemini (modelo gemini-3-flash-preview) que resuelve dudas sobre metodos de pago y logica de negocio.
* **Escaner de Barcode**: Herramienta para identificar productos rapidamente mediante el uso de la camara y codigos de barras.

### Modulo Administrativo
* **Gestion de Inventario**: CRUD completo de productos, categorias y marcas.
* **Gestion de Usuarios**: Administracion de clientes y vendedores.
* **Control de Ventas**: Registro historico de transacciones y generacion de facturas en formato PDF.

## Tecnologias Utilizadas
* **Backend**: Python 3.10+ y Django 5.1.4.
* **Base de Datos**: PostgreSQL.
* **Frontend**: HTML5, Tailwind CSS y JavaScript.
* **Inteligencia Artificial**: Google GenAI SDK (Gemini API).
* **Generacion de Documentos**: xhtml2pdf para facturacion.
* **Seguridad**: Variables de entorno con python-dotenv y proteccion CSRF en peticiones AJAX.

## Requisitos Previos
* Python instalado en su version 3.10 o superior.
* Servidor PostgreSQL activo.
* Cuenta de Google con API Key de Gemini.
* Cuenta de Gmail con Contrasena de Aplicacion activa para el envio de correos.

## Instalacion y Configuracion

### 1. Clonar el repositorio
```bash
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd sistema-de-ventas-supermercado
```

### 2. Configurar el entorno virtual
```bash
python -m venv env
# En Windows:
.\env\Scripts\activate
# En Linux/Mac:
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Cree un archivo .env en la raiz del proyecto y configure los siguientes parametros:
```bash
# Base de Datos
DB_DATABASE=nombre_db
DB_USERNAME=usuario_db
DB_PASSWORD=contrasena_db
DB_SOCKET=localhost
DB_PORT=5432

# Configuracion de Email (Gmail)
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_aplicacion
DEFAULT_FROM_EMAIL=tu_correo@gmail.com

# Google Gemini API
GEMINI_API_KEY=tu_api_key_aqui
```

### 5. Ejecutar migraciones y servidor
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Adicionales
Para no crear la base de datos, ni ejecutar el entorno virtual, ni instalar dependencias, ni ejecutar migraciones, ni insertar los datos de administración (marcas, categorias y metodos de pago) puede utilizar el comando:
```bash
./setup.sh
```

Pero antes debes darle los permisos de ejecución a este script:
```bash
chmod +x setup.sh
```

**OJO:** Debes tener instalado postgresql en tu sistema para que este script funcione.

## Datos del Autor
- **Nombre:** Kadir Barquet

- **Rol:** Desarrollador Principal Full Stack

- **Enfoque:** Desarrollo de aplicaciones web con Python/Django e integracion de IA.

- **Linkedin:** https://www.linkedin.com/in/kadir-barquet-bravo/

- **GitHub:** https://github.com/Kadir011/

- **Email:** barquetbravokadir@gmail.com

## Estado del Proyecto

- **Version:** 1.0.0
- **Estado:** Funcional / En fase de optimizacion de IA.

## Notas de Desarrollo

- El sistema utiliza una logica de seguridad en la vista de ordenes donde los usuarios solo pueden visualizar las ventas asociadas a su cuenta, incluso en compras como Consumidor Final.

- Para el correcto funcionamiento del chatbot, asegurese de que el archivo static/js/chatbot.js apunte a la ruta interna /chatbot/api/.

- El envio de correos desde el formulario de contacto esta configurado para que el administrador pueda responder directamente al cliente mediante la cabecera reply_to.

## Licencia
Este proyecto se distribuye bajo la Licencia MIT. Esto permite el uso, copia y modificacion del software de forma gratuita, siempre que se incluya el aviso de copyright original.