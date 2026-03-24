<div align="center">

<!-- Header con diseño del sistema -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td align="center" style="background-color: #14532d; border-radius: 12px; padding: 40px 32px; border: 3px solid #166534;">

<img src="https://img.shields.io/badge/-%F0%9F%9B%92%20MY%20SUPERMARKET-14532d?style=for-the-badge&labelColor=bbf7d0&color=166534&logoColor=white" alt="My Supermarket" height="48"/>

<br/><br/>

<span style="color: #ffffff; font-size: 24px; font-weight: 700;">**`MySupermarket`**</span>
<span style="color: #bbf7d0; font-size: 24px; font-weight: 700;">—</span>
<span style="color: #ffffff; font-size: 18px;">Sistema integral de E-Commerce y Punto de Venta para supermercados</span>

<br/><br/>

<span style="color: #86efac; font-size: 14px;">*Desarrollado con Django · Potenciado por IA · Protegido con idempotencia*</span>

</td>
</tr>
</table>

<br/>

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white"/>
<img src="https://img.shields.io/badge/Gemini_AI-Flash-4285F4?style=flat-square&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square"/>

</div>

---

## Índice

- [Índice](#índice)
- [Acerca del Proyecto](#acerca-del-proyecto)
- [Características](#características)
  - [🛒 Experiencia de Cliente](#-experiencia-de-cliente)
  - [🤖 Inteligencia Artificial](#-inteligencia-artificial)
  - [⚙️ Panel Administrativo](#️-panel-administrativo)
- [Arquitectura Técnica](#arquitectura-técnica)
- [Principios SOLID y Patrones de Diseño](#principios-solid-y-patrones-de-diseño)
  - [Principios SOLID aplicados](#principios-solid-aplicados)
  - [Patrones de diseño implementados](#patrones-de-diseño-implementados)
- [Seguridad e Idempotencia](#seguridad-e-idempotencia)
  - [Autenticación y Autorización](#autenticación-y-autorización)
  - [Idempotencia en Operaciones Críticas](#idempotencia-en-operaciones-críticas)
    - [Flujo del patrón de idempotencia (Checkout)](#flujo-del-patrón-de-idempotencia-checkout)
  - [Integridad de Datos en BD](#integridad-de-datos-en-bd)
- [Modelos de Datos](#modelos-de-datos)
- [Instalación](#instalación)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación manual](#instalación-manual)
  - [Instalación automática (Linux/Mac)](#instalación-automática-linuxmac)
- [Variables de Entorno](#variables-de-entorno)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Estado del Proyecto](#estado-del-proyecto)
  - [Changelog v1.1.0](#changelog-v110)
- [Desarrollador](#desarrollador)
- [Licencia](#licencia)

---

## Acerca del Proyecto

**My Supermarket** es una plataforma empresarial de doble propósito que combina un robusto sistema de punto de venta (POS) con una experiencia de e-commerce moderna. Diseñado para supermercados medianos, ofrece tanto una interfaz de cliente para compras en línea como un panel administrativo completo para la gestión interna.

El diferenciador principal radica en la integración de tecnologías de IA, un sistema de escaneo de códigos de barras en tiempo real, y una arquitectura que garantiza la **integridad transaccional** mediante patrones de idempotencia, principios SOLID y patrones de diseño como Strategy y Singleton.

---

## Características

<div align="center">

<table width="100%">
<tr>
<td width="33%" valign="top">

### 🛒 Experiencia de Cliente
- Catálogo dinámico con filtros por categoría, marca y búsqueda en tiempo real
- Carrito inteligente con actualización dinámica de cantidades
- Cálculo automático de IVA (15%) y descuentos personalizados
- Checkout flexible: Consumidor Final o datos personales para factura legal
- Historial de compras con descarga de facturas PDF
- Escáner de códigos de barras EAN-13 vía cámara

</td>
<td width="33%" valign="top">

### 🤖 Inteligencia Artificial
- Chatbot conversacional basado en Google Gemini Flash
- Contexto dinámico: accede al inventario, precios y políticas en tiempo real
- Respuestas diferenciadas por rol (visitante, cliente, administrador)
- Los administradores reciben datos de ventas en tiempo real durante la conversación
- Historial de conversación persistente en sesión

</td>
<td width="33%" valign="top">

### ⚙️ Panel Administrativo
- CRUD completo de productos, categorías, marcas con validaciones
- Administración de clientes y vendedores
- Registro histórico de ventas con búsqueda y filtros
- Generación automática de facturas PDF con datos censurados (PCI)
- Dashboard con notificaciones de ventas recientes
- Formulario de contacto con integración SMTP Gmail

</td>
</tr>
</table>

</div>

---

## Arquitectura Técnica

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENTE / BROWSER                    │
│  Tailwind CSS 3.x · JavaScript ES6+ · Quagga (Scanner)  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/HTTPS
┌────────────────────────▼────────────────────────────────┐
│                   DJANGO 5.1.4 (Backend)                 │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ core.super  │  │core.security │  │    config/     │  │
│  │  (negocio)  │  │    (auth)    │  │   (settings)   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Middleware Stack                     │    │
│  │  CSRF · Auth · Session · CRUM · Clickjacking     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────┬───────────────────────────┬──────────────────┘
           │                           │
┌──────────▼──────────┐    ┌───────────▼──────────────────┐
│   PostgreSQL 15+     │    │    Google Gemini API          │
│                      │    │  (gemini-flash-preview)       │
│  ATOMIC_REQUESTS=True│    └──────────────────────────────┘
│  Constraints CHECK   │
│  UUID idempotency    │
└─────────────────────-┘
```

<div align="center">

| Capa | Tecnología |
|:-----|:----------|
| **Backend** | Python 3.10+ / Django 5.1.4 |
| **Base de Datos** | PostgreSQL 15+ con `ATOMIC_REQUESTS=True` |
| **Frontend** | Tailwind CSS 3.x, JavaScript ES6+, Boxicons |
| **IA / Chatbot** | Google GenAI SDK (Gemini Flash) |
| **PDF** | xhtml2pdf + ReportLab |
| **Scanner** | QuaggaJS (EAN-13, detección por votos) |
| **Seguridad** | python-dotenv, CSRF, UUID idempotency keys |

</div>

---

## Principios SOLID y Patrones de Diseño

El proyecto aplica de forma explícita principios SOLID y patrones de diseño en la capa de servicios.

### Principios SOLID aplicados

<div align="center">

| Principio | Aplicación |
|:----------|:-----------|
| **SRP** — Single Responsibility | `CheckoutService`, `StoreContextBuilder`, `SalesContextBuilder` y `ChatContextDirector` tienen una única responsabilidad cada uno |
| **OCP** — Open/Closed | `PaymentProcessor` es extensible sin modificar el checkout: agregar un nuevo método solo requiere una nueva clase y registrarla en `PAYMENT_PROCESSORS` |
| **DIP** — Dependency Inversion | `ChatbotProxyView` depende de la abstracción `AIClient`, no de `GeminiAIClient` directamente, permitiendo sustituir el proveedor de IA |

</div>

### Patrones de diseño implementados

<div align="center">

| Patrón | Clase / Archivo | Descripción |
|:-------|:----------------|:------------|
| **Strategy** | `PaymentProcessor` → `CashPaymentProcessor`, `CardPaymentProcessor`, `TransferPaymentProcessor` | Cada método de pago encapsula su lógica de cálculo de monto recibido y cambio de forma intercambiable |
| **Singleton** | `IdempotencyService` | Una única instancia compartida gestiona la verificación y resolución de claves de idempotencia en toda la aplicación |
| **Builder / Director** | `ChatContextDirector` + `StoreContextBuilder` + `SalesContextBuilder` | Construye el contexto del chatbot ensamblando partes según el rol del usuario |

</div>

---

## Seguridad e Idempotencia

El proyecto implementa múltiples capas de seguridad y protección contra operaciones duplicadas.

### Autenticación y Autorización

- **Separación estricta de roles**: clientes y administradores usan flujos de login independientes con validación cruzada
- **Protección CSRF**: activa en todas las peticiones, incluyendo AJAX con `X-CSRFToken`
- **Variables de entorno**: toda configuración sensible externalizada con `python-dotenv`
- **Datos de pago censurados**: tarjetas y cuentas se almacenan parcialmente enmascaradas (PCI-compatible)

### Idempotencia en Operaciones Críticas

<div align="center">

| Operación | Riesgo sin protección | Mecanismo aplicado |
|:----------|:----------------------|:-------------------|
| **Checkout / Crear venta (cliente)** | Doble clic, F5 o botón "atrás" generaban dos ventas y descontaban stock dos veces | `idempotency_key` UUID generado en el GET del checkout, almacenado con constraint `UNIQUE` en la BD. El segundo submit detecta la clave existente y redirige a la venta ya creada sin procesar nada nuevo. El botón "Finalizar Compra" se deshabilita en el cliente al primer click |
| **Crear venta (panel admin)** | Doble clic en "Guardar" creaba ventas duplicadas en el panel administrativo | El UUID generado al abrir el formulario viaja en el payload JSON. El backend verifica existencia antes de insertar. El botón se deshabilita en JS al primer envío y se rehabilita solo si el servidor devuelve error |
| **Agregar al carrito** | Dos clicks rápidos podían sumar +2 en lugar de +1 (race condition) | `select_for_update()` a nivel de fila + `F('quantity') + 1` para incremento atómico |
| **Eliminar venta (restaurar stock)** | Fallo a mitad dejaba stock inconsistente | `@transaction.atomic` envuelve la restauración de stock y la eliminación de la venta |
| **Registro de usuarios** | — | Constraint `UNIQUE` en `username` y `email` con `IntegrityError` correctamente capturado |

</div>

#### Flujo del patrón de idempotencia (Checkout)

```
Cliente abre /checkout/  →  GET genera UUID  →  uuid almacenado en campo hidden
        │
        ▼
Usuario hace submit  →  POST envía uuid  →  ¿Existe Sale con ese uuid?
        │                                          │
        │                                    SÍ ──►  redirect a venta existente
        │                                          │  (sin procesar nada)
        │                                    NO ──►  crear venta + guardar uuid
        │
        ▼
Botón deshabilitado en JS  →  segundo click bloqueado en el cliente
(defensa en profundidad: cliente + servidor)
```

### Integridad de Datos en BD

```sql
-- Constraints CHECK activos en PostgreSQL
product_stock_non_negative   CHECK (stock >= 0)
product_price_non_negative   CHECK (price > 0)
sale_subtotal_non_negative   CHECK (subtotal >= 0)
sale_total_non_negative      CHECK (total >= 0)
saledetail_quantity_non_neg  CHECK (quantity >= 1)

-- Unique constraint de idempotencia
super_sale.idempotency_key   UNIQUE (null permitido para ventas legacy)
```

---

## Modelos de Datos

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Category  │     │    Brand    │     │  PaymentMethod  │
│─────────────│     │─────────────│     │─────────────────│
│ id_category │     │  id_brand   │     │id_payment_method│
│ name        │     │ name        │     │ name            │
└──────┬──────┘     └──────┬──────┘     └────────┬────────┘
       │                   │                     │
       └──────────┬────────┘                     │
                  │                              │
           ┌──────▼──────┐                       │
           │   Product   │               ┌───────▼──────────────┐
           │─────────────│               │         Sale          │
           │ id_product  │◄──────────────│───────────────────────│
           │ name        │  SaleDetail   │ id_sale               │
           │ price       │               │ user (FK→User)        │
           │ stock       │               │ customer (FK)         │
           │ barcode     │               │ seller (FK)           │
           │ state       │               │ payment (FK)          │
           └──────┬──────┘               │ subtotal / iva / total│
                  │                      │ idempotency_key (UUID)│◄── UNIQUE
                  │                      └───────────────────────┘
           ┌──────▼──────┐
           │  CartItem   │    ┌─────────────┐     ┌─────────────┐
           │─────────────│    │  Customer   │     │   Seller    │
           │ cart (FK)   │    │─────────────│     │─────────────│
           │ product (FK)│    │ dni (unique)│     │ dni (unique)│
           │ quantity    │    │ email       │     │ email       │
           └─────────────┘    │discount_pct │     │             │
                              └─────────────┘     └─────────────┘
```

<div align="center">

| Modelo | Descripción |
|:-------|:------------|
| `Product` | Inventario con código EAN-13, estado calculado automáticamente desde stock |
| `Category` / `Brand` | Clasificación y organización de productos |
| `Customer` | Perfil con descuentos personalizados por porcentaje |
| `Seller` | Registro de empleados vendedores |
| `Sale` | Transacciones con IVA, descuentos, datos de pago censurados e **idempotency_key** |
| `SaleDetail` | Línea items de cada venta con constraints de integridad |
| `Cart` / `CartItem` | Carrito persistente por usuario con `unique_together` |

</div>

---

## Instalación

### Requisitos previos

- Python 3.10 o superior
- PostgreSQL 15+ (servidor activo)
- Cuenta de Google Cloud con API Key de Gemini
- Cuenta Gmail con Contraseña de Aplicación (para SMTP)

### Instalación manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado

# 2. Configurar entorno virtual
python -m venv env

# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo .env (ver sección siguiente)

# 5. Ejecutar migraciones
cd app
python manage.py makemigrations
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Levantar servidor
python manage.py runserver
```

### Instalación automática (Linux/Mac)

El script `setup.sh` detecta automáticamente el entorno virtual en múltiples rutas posibles y carga los datos iniciales (categorías, marcas, métodos de pago).

```bash
cd app
chmod +x setup.sh
./setup.sh
```

> **Nota Windows (Git Bash):** Si el script no encuentra el entorno virtual automáticamente, te pedirá la ruta completa. Ejemplo: `C:/PROGRAMACION/proyecto/env`

---

## Variables de Entorno

Crear archivo `.env` en la raíz de `/app`:

```env
# ── Base de Datos ─────────────────────────────
DB_DATABASE=my_supermarket
DB_USERNAME=postgres
DB_PASSWORD=tu_password
DB_SOCKET=localhost
DB_PORT=5432

# ── Email (Gmail SMTP) ─────────────────────────
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_app
DEFAULT_FROM_EMAIL=tu_correo@gmail.com

# ── Google Gemini AI ───────────────────────────
GEMINI_API_KEY=tu_api_key_de_gemini

# ── Django (opcional) ─────────────────────────
SECRET_KEY=tu_secret_key_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> ⚠️ El archivo `.env` está en `.gitignore`. Nunca lo subas al repositorio.

---

## Estructura del Proyecto

```
django_supermercado/
├── env/                        # Entorno virtual (ignorado por git)
└── app/
    ├── config/                 # Configuración centralizada de Django
    │   ├── settings.py        # Settings · ATOMIC_REQUESTS=True
    │   ├── urls.py            # Rutas principales
    │   └── wsgi.py / asgi.py
    ├── core/
    │   ├── security/           # Módulo de autenticación
    │   │   ├── models.py      # User (AbstractUser) con user_type
    │   │   ├── views/auth.py  # Login dual · Registro con creación de Customer
    │   │   └── urls.py
    │   └── super/              # Módulo principal del negocio
    │       ├── models.py      # Product · Sale · Cart · SaleDetail · …
    │       ├── services/       # ← Capa de servicios (SOLID + Patrones)
    │       │   ├── ai_client.py          # DIP: interfaz AIClient + GeminiAIClient
    │       │   ├── chat_context.py       # SRP: Builder + Director para chatbot
    │       │   ├── checkout_service.py   # SRP: orquestación del checkout
    │       │   ├── idempotency_service.py# Singleton: gestión de claves UUID
    │       │   └── payment_processors.py # OCP + Strategy: procesadores de pago
    │       ├── views/
    │       │   ├── cart.py    # ← Idempotencia: select_for_update + F()
    │       │   ├── sale.py    # ← Idempotencia: UUID en handle_ajax
    │       │   ├── chatbot.py # Google Gemini con contexto dinámico
    │       │   └── shop.py / product.py / customer.py / seller.py
    │       ├── form/          # Formularios Django con validaciones
    │       └── urls.py
    ├── templates/
    │   ├── components/        # base.html · navbar · chatbot · footer
    │   ├── security/          # login.html · signup.html
    │   └── super/             # shop · cart · checkout · sales · products
    ├── static/
    │   ├── css/               # Estilos optimizados por módulo
    │   └── js/
    │       ├── checkout.js    # ← Idempotencia: btn.dataset.submitted
    │       ├── sale.js        # ← Idempotencia: idempotency_key en payload
    │       ├── scan_barcode.js # Quagga · sistema de votos · EAN-13
    │       └── chatbot.js
    ├── manage.py
    ├── requirements.txt
    └── setup.sh               # Script de instalación automática
```

---

## Estado del Proyecto

<div align="center">

| Versión | Estado | Notas |
|:-------:|:------:|:------|
| `1.1.0` | ✅ Estable | Idempotencia · SOLID · Patrones de diseño · Setup.sh mejorado |
| `1.0.0` | ✅ Estable | Versión inicial funcional |

</div>

### Changelog v1.1.0

- ✅ **Idempotencia en checkout**: `idempotency_key` UUID con constraint UNIQUE en `Sale`
- ✅ **Idempotencia en ventas admin**: UUID en payload JSON de `SaleCreateView`
- ✅ **Race condition en carrito**: `select_for_update()` + `F('quantity') + 1`
- ✅ **Atomicidad en eliminación**: `@transaction.atomic` en `SaleDeleteView.delete()`
- ✅ **Protección cliente**: botón submit deshabilitado tras primer click
- ✅ **Principio SRP**: servicios extraídos a `core/super/services/`
- ✅ **Principio OCP + Strategy**: `PaymentProcessor` extensible sin modificar checkout
- ✅ **Principio DIP**: `ChatbotProxyView` depende de `AIClient` (abstracción)
- ✅ **Singleton**: `IdempotencyService` con instancia única compartida
- ✅ **Builder/Director**: `ChatContextDirector` ensambla contexto por rol
- ✅ **CSS modular**: estilos separados por módulo (customer, product, sale, seller)
- ✅ **setup.sh mejorado**: detección automática del virtualenv en múltiples rutas

---

## Desarrollador

<div align="center">

**Kadir Barquet Bravo**
Desarrollador Full Stack

[![LinkedIn](https://img.shields.io/badge/LinkedIn-kadir--barquet--bravo-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kadir-barquet-bravo/)
[![GitHub](https://img.shields.io/badge/GitHub-Kadir011-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Kadir011)
[![Email](https://img.shields.io/badge/Email-barquetbravokadir%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:barquetbravokadir@gmail.com)

</div>

---

## Licencia

Este proyecto está licenciado bajo **MIT License**.
Puedes usarlo, modificarlo y distribuirlo libremente siempre que incluyas el aviso de copyright original.

---

<div align="center">
<sub>Built with ❤️ in Guayaquil, Ecuador · Django 5.1.4 · Python 3.10+</sub>
</div>