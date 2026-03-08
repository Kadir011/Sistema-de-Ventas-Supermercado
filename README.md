# My Supermarket - E-Commerce & POS System

**Django 5.1.4** | **Python 3.10+** | **PostgreSQL** | **Tailwind CSS** | **Google Gemini AI**

Sistema integral de comercio electrónico y gestión de ventas para supermercados, desarrollado con Django y potenciado por Inteligencia Artificial.

---

## Indice

- [My Supermarket - E-Commerce \& POS System](#my-supermarket---e-commerce--pos-system)
  - [Indice](#indice)
  - [Acerca del Proyecto](#acerca-del-proyecto)
  - [Características Destacadas](#características-destacadas)
    - [Experiencia de Cliente](#experiencia-de-cliente)
    - [Inteligencia Artificial](#inteligencia-artificial)
    - [Panel Administrativo](#panel-administrativo)
  - [Arquitectura Tecnica](#arquitectura-tecnica)
  - [Requisitos del Sistema](#requisitos-del-sistema)
  - [Instalacion](#instalacion)
    - [1. Clonar el repositorio](#1-clonar-el-repositorio)
    - [2. Configurar entorno virtual](#2-configurar-entorno-virtual)
    - [3. Instalar dependencias](#3-instalar-dependencias)
    - [4. Configurar variables de entorno](#4-configurar-variables-de-entorno)
    - [5. Ejecutar migraciones y levantar servidor](#5-ejecutar-migraciones-y-levantar-servidor)
    - [Instalacion Automatica (Linux/Mac)](#instalacion-automatica-linuxmac)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Modelo de Seguridad](#modelo-de-seguridad)
  - [Modelos de Datos Principales](#modelos-de-datos-principales)
  - [Datos del Desarrollador](#datos-del-desarrollador)
  - [Estado del Proyecto](#estado-del-proyecto)
  - [Notas de Desarrollo](#notas-de-desarrollo)
  - [Licencia](#licencia)

---

## Acerca del Proyecto

My Supermarket es una plataforma empresarial de doble propósito que combina un robusto sistema de punto de venta (POS) con una experiencia de e-commerce moderna. El proyecto está diseñado para resolver las necesidades operativas de supermercados medianos, ofreciendo tanto una interfaz de cliente para compras en linea como un panel administrativo completo para la gestión interna.

El diferenciador principal del proyecto radica en la integración de tecnologías de IA para mejorar la experiencia del usuario, incluyendo un asistente virtual conversacional y un sistema de escaneo de códigos de barras en tiempo real.

---

## Características Destacadas

### Experiencia de Cliente

- **Catalogo Dinamico**: Exploracion de productos con filtros avanzados por categoria, marca y busqueda en tiempo real
- **Carrito Inteligente**: Gestion de items con actualizacion dinamica de cantidades, calculo automatico de IVA (15%) y descuentos
- **Checkout Flexible**: Dos modos de facturacion: Consumidor Final o con datos personales para emitir facturas legales
- **Historial de Compras**: Panel personalizado para visualizar todas las ordenes anteriores y descargar facturas PDF
- **Escaner de Barras**: Identificacion instantea de productos mediante camara del dispositivo (EAN-13)

### Inteligencia Artificial

- **Chatbot Gemini**: Asistente virtual conversacional basado en Google Gemini API que resuelve consultas sobre productos, metodos de pago y procesos de compra
- **Contexto Dinamico**: El chatbot accede en tiempo real al inventario disponible, precios y politicas actualizadas
- **Soporte Multicanal**: Integracion nativa con reglas de negocio especificas del comercio

### Panel Administrativo

- **Gestion de Inventario**: CRUD completo de productos, categorias, marcas con validaciones y constraints de integridad
- **Administracion de Usuarios**: Control de clientes, vendedores y permisos diferenciados
- **Control de Ventas**: Registro historico de transacciones con busqueda y filtros avanzados
- **Facturacion PDF**: Generacion automatica de facturas en formato PDF con datos censurados para seguridad
- **Contacto Directo**: Formulario de contacto con integracion SMTP Gmail para comunicacion con clientes

---

## Arquitectura Tecnica

- **Backend**: Python 3.10+ / Django 5.1.4
- **Base de Datos**: PostgreSQL 15+
- **Frontend**: Tailwind CSS 3.x, JavaScript ES6+
- **IA**: Google GenAI SDK (Gemini 3 Flash)
- **PDF**: xhtml2pdf
- **Seguridad**: python-dotenv, CSRF Protection

---

## Requisitos del Sistema

- Python 3.10 o superior
- PostgreSQL 15+ (servidor activo)
- Cuenta de Google Cloud con API Key de Gemini
- Cuenta Gmail con Contrasena de Aplicacion (para SMTP)

---

## Instalacion

### 1. Clonar el repositorio
```bash
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado
```

### 2. Configurar entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raiz del proyecto:

```env
# Base de Datos
DB_DATABASE=my_supermarket
DB_USERNAME=postgres
DB_PASSWORD=tu_password
DB_SOCKET=localhost
DB_PORT=5432

# Email (Gmail SMTP)
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_app
DEFAULT_FROM_EMAIL=tu_correo@gmail.com

# Google Gemini AI
GEMINI_API_KEY=tu_api_key_de_gemini

# Configuracion Django (Opcional - valores por defecto)
SECRET_KEY=tu_secret_key_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Ejecutar migraciones y levantar servidor
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Instalacion Automatica (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

Nota: Requiere PostgreSQL instalado localmente.

---

## Estructura del Proyecto

```
app/
├── config/                 # Configuracion centralizada de Django
│   ├── settings.py        # Settings principales
│   ├── urls.py            # Rutas principales
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
├── core/
│   ├── security/          # Modulo de autenticacion y usuarios
│   │   ├── models.py      # Modelos de usuario y permisos
│   │   ├── views/         # Vistas de auth (login, register)
│   │   └── urls.py        # Rutas de seguridad
│   └── super/             # Modulo principal del negocio
│       ├── models.py      # Modelos: Product, Sale, Customer, etc.
│       ├── views/         # Vistas CRUD y funcionalidades
│       ├── forms/         # Formularios Django
│       ├── admin.py       # Configuracion Django Admin
│       └── urls.py        # Rutas del modulo
├── templates/              # Plantillas HTML
│   ├── components/        # Componentes reutilizables
│   ├── security/           # Templates de autenticacion
│   └── super/              # Templates del modulo principal
└── static/                 # Archivos estaticos (CSS, JS, Images)
```

---

## Modelo de Seguridad

- **Autenticacion Dual**: Separacion estricta entre clientes y administradores
- **Proteccion CSRF**: Middleware activo en todas las peticiones AJAX
- **Validaciones en Base de Datos**: Constraints de integridad (stock no negativo, precios positivos)
- **Censurado de Datos de Pago**: Las tarjetas y cuentas se almacenan parcialmente visibles
- **Variables de Ambiente**: Toda configuracion sensible externalizada

---

## Modelos de Datos Principales

| Modelo | Descripcion |
|--------|-------------|
| `Product` | Gestion de inventario con codigo de barras EAN-13 |
| `Category` / `Brand` | Clasificacion y organizacion de productos |
| `Customer` | Perfil de cliente con descuentos personalizados |
| `Seller` | Registro de empleados vendedores |
| `Sale` | Transacciones con calculo automatico de IVA y descuentos |
| `SaleDetail` | Linea items de cada venta |
| `Cart` / `CartItem` | Carrito de compras persistente por usuario |

---

## Datos del Desarrollador

**Kadir Barquet**  
Desarrollador Full Stack

- LinkedIn: [linkedin.com/in/kadir-barquet-bravo](https://www.linkedin.com/in/kadir-barquet-bravo/)
- GitHub: GitHub: [github.com/Kadir011](https://github.com/Kadir011)
- Email: barquetbravokadir@gmail.com

---

## Estado del Proyecto

| Version | Estado | Notas |
|---------|--------|-------|
| 1.0.0 | Estable | Funcional, en optimizacion continua |

---

## Notas de Desarrollo

- El sistema implementa separacion estricta de permisos: clientes solo acceden a sus propias ordenes
- El chatbot consulta el inventario en tiempo real para dar informacion actualizada
- Las facturas PDF incluyen datos censurados de pago por seguridad PCI
- El formulario de contacto esta configurado con `reply-to` para respuestas directas del administrador

---

## Licencia

Este proyecto esta licenciado bajo **MIT License**. Puedes usarlo, modificarlo y distribuirlo libremente siempre que incluyas el aviso de copyright original.
