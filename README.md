<div align="center">

<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td align="center" style="background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 60%, #b91c1c 100%); border-radius: 16px; padding: 40px 32px;">

<img src="https://img.shields.io/badge/-%F0%9F%9B%92%20MY%20SUPERMARKET-7f1d1d?style=for-the-badge&labelColor=991b1b&color=b91c1c&logoColor=white" alt="My Supermarket" height="48"/>

<br/><br/>

**`MySupermarket`** — Plataforma full‑stack de E-Commerce y Punto de Venta para supermercados

*Django · PostgreSQL · Google Gemini AI · Arquitectura SOLID · Patrones de Diseño*

</td>
</tr>
</table>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white&labelColor=0d1117)](https://djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql&logoColor=white&labelColor=0d1117)](https://postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white&labelColor=0d1117)](https://tailwindcss.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Flash-4285F4?style=flat-square&logo=google&logoColor=white&labelColor=0d1117)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square&labelColor=0d1117)](.)

<br/>

![SOLID](https://img.shields.io/badge/Architecture-SOLID-6366f1?style=flat-square&labelColor=0d1117)
![Strategy](https://img.shields.io/badge/Pattern-Strategy-f59e0b?style=flat-square&labelColor=0d1117)
![Singleton](https://img.shields.io/badge/Pattern-Singleton-ec4899?style=flat-square&labelColor=0d1117)
![Builder](https://img.shields.io/badge/Pattern-Builder%2FDirector-10b981?style=flat-square&labelColor=0d1117)
![Idempotency](https://img.shields.io/badge/Feature-Idempotency-0ea5e9?style=flat-square&labelColor=0d1117)
![CrossBrowser](https://img.shields.io/badge/Feature-Cross--Browser-f97316?style=flat-square&labelColor=0d1117)
![Discounts](https://img.shields.io/badge/Feature-Discount%20System-16a34a?style=flat-square&labelColor=0d1117)

<br/>

> **Vende · Gestiona · Escala** — Sistema integral con POS, tienda online e IA conversacional
>
> *Capa de servicios desacoplada con principios **SOLID**, idempotencia end-to-end, sistema de descuentos con vigencia y compatibilidad cross-browser — v1.3.0*

</div>

---

## Tabla de Contenidos

- [Tabla de Contenidos](#tabla-de-contenidos)
- [Acerca del Proyecto](#acerca-del-proyecto)
- [Stack Tecnológico](#stack-tecnológico)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Arquitectura](#arquitectura)
- [Principios SOLID aplicados](#principios-solid-aplicados)
- [Patrones de Diseño](#patrones-de-diseño)
- [Sistema de Descuentos con Vigencia](#sistema-de-descuentos-con-vigencia)
  - [Reglas de negocio](#reglas-de-negocio)
  - [Flujo del descuento](#flujo-del-descuento)
  - [Estados del descuento](#estados-del-descuento)
- [Seguridad e Idempotencia](#seguridad-e-idempotencia)
  - [Mecanismos de protección](#mecanismos-de-protección)
  - [Flujo de idempotencia (Checkout)](#flujo-de-idempotencia-checkout)
  - [Operaciones protegidas](#operaciones-protegidas)
- [Chatbot con IA contextual](#chatbot-con-ia-contextual)
  - [Contexto por rol](#contexto-por-rol)
  - [Conocimiento del sistema de descuentos](#conocimiento-del-sistema-de-descuentos)
- [Compatibilidad Cross-Browser](#compatibilidad-cross-browser)
- [Sistema de Diseño Frontend](#sistema-de-diseño-frontend)
- [Módulos del Sistema](#módulos-del-sistema)
  - [🛒 Tienda Online (Cliente)](#-tienda-online-cliente)
  - [🤖 Chatbot con IA](#-chatbot-con-ia)
  - [⚙️ Panel Administrativo](#️-panel-administrativo)
  - [📷 Escáner EAN-13](#-escáner-ean-13)
- [Modelos de Datos](#modelos-de-datos)
- [Instalación](#instalación)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación rápida (Linux/Mac)](#instalación-rápida-linuxmac)
  - [Instalación manual](#instalación-manual)
- [Variables de Entorno](#variables-de-entorno)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Changelog](#changelog)
  - [v1.3.0 — Sistema de Descuentos + Chatbot Contextual](#v130--sistema-de-descuentos--chatbot-contextual)
  - [v1.2.0 — Diseño Frontend + Auditoría Cross-Browser](#v120--diseño-frontend--auditoría-cross-browser)
  - [v1.1.0 — Arquitectura SOLID + Idempotencia](#v110--arquitectura-solid--idempotencia)
  - [v1.0.0 — Versión inicial funcional](#v100--versión-inicial-funcional)
- [Desarrollador](#desarrollador)

---

## Acerca del Proyecto

**MySupermarket** es una plataforma empresarial de doble propósito que combina un robusto **sistema de punto de venta (POS)** con una experiencia de **e-commerce moderna**. Diseñada para supermercados medianos, unifica inventario, ventas físicas y compras online en un único sistema centralizado, eliminando procesos manuales fragmentados.

Los diferenciadores principales son su **arquitectura desacoplada con SOLID**, un sistema de **idempotencia end-to-end** que elimina ventas duplicadas incluso ante doble clic o fallo de red, un **sistema de descuentos con vigencia temporal** que el administrador asigna por cliente y que el chatbot conoce en tiempo real, integración de **IA conversacional** con acceso al inventario y datos personalizados por rol, y un **sistema de diseño frontend consistente** con componentes reutilizables auditados para compatibilidad cross-browser.

---

## Stack Tecnológico

<table>
<tr>
<td width="50%" valign="top">

### Backend

| Tecnología | Versión | Propósito |
|---|---|---|
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) Python | `3.10+` | Lenguaje base |
| ![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white&style=flat-square) Django | `5.1.4` | Web framework |
| ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?logo=postgresql&logoColor=white&style=flat-square) PostgreSQL | `15+` | Base de datos relacional |
| ![Gemini](https://img.shields.io/badge/-Gemini_AI-4285F4?logo=google&logoColor=white&style=flat-square) Google GenAI | `1.57.0` | Chatbot conversacional |
| ![xhtml2pdf](https://img.shields.io/badge/-xhtml2pdf-ef4444?style=flat-square) xhtml2pdf | `0.2.17` | Generación de facturas PDF |
| ![openpyxl](https://img.shields.io/badge/-openpyxl-217346?style=flat-square) openpyxl | `3.1.5` | Exportación de reportes Excel |

</td>
<td width="50%" valign="top">

### Frontend

| Tecnología | Versión | Propósito |
|---|---|---|
| ![Tailwind](https://img.shields.io/badge/-Tailwind-06B6D4?logo=tailwindcss&logoColor=white&style=flat-square) Tailwind CSS | `3.x` | Utility-first CSS |
| ![JS](https://img.shields.io/badge/-JavaScript-F7DF1E?logo=javascript&logoColor=black&style=flat-square) JavaScript | `ES6+` | Lógica del cliente |
| ![Quagga](https://img.shields.io/badge/-QuaggaJS-6366f1?style=flat-square) QuaggaJS | `0.12.1` | Escáner EAN-13 |
| ![JsBarcode](https://img.shields.io/badge/-JsBarcode-374151?style=flat-square) JsBarcode | `3.11.5` | Visualización de códigos |
| ![Boxicons](https://img.shields.io/badge/-Boxicons-f97316?style=flat-square) Boxicons | `2.1.4` | Iconografía |
| ![Jakarta Sans](https://img.shields.io/badge/-Plus_Jakarta_Sans-8b5cf6?style=flat-square) Plus Jakarta Sans | `—` | Tipografía base |

</td>
</tr>
</table>

---

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│                      CLIENTE / BROWSER                           │
│   Tailwind CSS 3.x · JavaScript ES6+ · QuaggaJS (EAN-13)        │
│   Plus Jakarta Sans · CSS modular por módulo                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP/HTTPS
┌───────────────────────────▼──────────────────────────────────────┐
│                    DJANGO 5.1.4 (Backend)                        │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │    Views    │  │ Middlewares  │  │    URL Routing       │    │
│  │  (thin)     │  │ CSRF · Auth  │  │   25+ rutas          │    │
│  └──────┬──────┘  └──────────────┘  └──────────────────────┘    │
│         │ delega                                                  │
│  ┌──────▼──────────────────────────────────────┐                 │
│  │              Capa de Servicios (SOLID)       │                 │
│  │                                             │                 │
│  │  CheckoutService    ← SRP                   │                 │
│  │  PaymentProcessor   ← OCP + Strategy        │                 │
│  │  IdempotencyService ← Singleton             │                 │
│  │  ChatContextDirector← Builder + Director    │                 │
│  │  CustomerContextBuilder ← descuento + hist. │                 │
│  │  GeminiAIClient     ← DIP (AIClient ABC)    │                 │
│  └──────┬──────────────────────────────────────┘                 │
│         │                                                        │
│  ┌──────▼──────┐  ┌──────────────────────────────────────────┐  │
│  │   Models    │  │  Idempotency: UUID + UNIQUE constraint   │  │
│  │ (ORM + BD)  │  │  Descuento: has_active_discount() +      │  │
│  └─────────────┘  │  discount_expiry DateField               │  │
│                   │  Concurrencia: select_for_update + F()   │  │
│                   └──────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │  ORM / Parameterized Queries
┌───────────────────────────▼──────────────────────────────────────┐
│                        POSTGRESQL 15+                            │
│  ATOMIC_REQUESTS=True · CHECK constraints · UNIQUE idempotency  │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    GOOGLE GEMINI API                              │
│   Reintentos con backoff exponencial · Contexto dinámico por rol │
│   Descuento activo del cliente inyectado en el prompt            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Principios SOLID aplicados

| Principio | Dónde se aplica |
|---|---|
| **S** — Single Responsibility | `CheckoutService`, `StoreContextBuilder`, `SalesContextBuilder`, `CustomerContextBuilder` y `ChatContextDirector` tienen una única responsabilidad cada uno. Las vistas son thin controllers que delegan a servicios. |
| **O** — Open/Closed | `PaymentProcessor` es extensible sin modificar el checkout: agregar un nuevo método de pago solo requiere una nueva clase y registrarla en `PAYMENT_PROCESSORS`. |
| **L** — Liskov Substitution | `CashPaymentProcessor`, `CardPaymentProcessor` y `TransferPaymentProcessor` implementan `PaymentProcessor` y son intercambiables donde se espere la abstracción. |
| **I** — Interface Segregation | `AIClient` (ABC) expone solo `generate()`. Las clases concretas no se ven forzadas a implementar métodos que no usan. |
| **D** — Dependency Inversion | `ChatbotProxyView` depende de la abstracción `AIClient`, no de `GeminiAIClient` directamente. Sustituir el proveedor de IA no requiere tocar la vista. |

---

## Patrones de Diseño

| Patrón | Implementación | Beneficio |
|---|---|---|
| 🎯 **Strategy** | `PaymentProcessor` → `CashPaymentProcessor`, `CardPaymentProcessor`, `TransferPaymentProcessor` | Cada método de pago encapsula su lógica de cálculo de monto y cambio sin condiciones en el checkout. |
| 🔒 **Singleton** | `IdempotencyService` | Una única instancia compartida gestiona la verificación y resolución de claves UUID en toda la aplicación, sin estado duplicado. |
| 🏗️ **Builder / Director** | `ChatContextDirector` + `StoreContextBuilder` + `SalesContextBuilder` + `CustomerContextBuilder` + `GuestContextBuilder` | Ensambla el contexto del chatbot por partes según el rol del usuario — incluyendo ahora el estado activo del descuento personal — sin que la vista conozca los detalles de construcción. |

---

## Sistema de Descuentos con Vigencia

El sistema implementa descuentos personalizados por cliente con **control de vigencia temporal**: el administrador puede asignar un porcentaje de descuento y una fecha de expiración. El sistema verifica en tiempo real si el descuento está activo antes de aplicarlo, tanto en el checkout como en el chatbot.

### Reglas de negocio

| Condición | Resultado |
|---|---|
| `discount_percentage > 0` + `discount_expiry >= hoy` + factura personal + pago Efectivo/Tarjeta | ✅ Descuento aplicado |
| `discount_expiry < hoy` (fecha vencida) | ❌ Descuento no aplicado |
| `discount_expiry` vacío | ❌ Descuento no aplicado |
| Factura tipo "Consumidor Final" | ❌ Descuento no aplicado |
| Método de pago "Transferencia bancaria" | ❌ Descuento no aplicado |

### Flujo del descuento

```
Admin edita cliente → asigna discount_percentage + discount_expiry
                                    │
                        ┌───────────▼───────────┐
                        │  has_active_discount() │  ← método en Customer model
                        │  pct > 0              │
                        │  expiry no nulo        │
                        │  expiry >= hoy         │
                        └───────────┬───────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
     GET /checkout/         POST /checkout/          Chatbot API
  Preview descuento       calculate_totals()     CustomerContextBuilder
  en template HTML        CheckoutService        inyecta estado en prompt
  (potencial máximo)      valida pago+tipo       Gemini responde con
                          aplica o no aplica     info personalizada
```

### Estados del descuento

El modelo `Customer` expone dos helpers que son usados en toda la aplicación — vistas, checkout, template y chatbot — para garantizar coherencia:

```python
customer.has_active_discount()      # bool — ¿aplica ahora mismo?
customer.get_active_discount_pct()  # Decimal — porcentaje o 0.00
```

La lista de clientes en el panel admin muestra visualmente tres estados: **activo** (badge verde con fecha), **vencido** (badge rojo con fecha de vencimiento) y **sin vigencia** (badge gris con aviso).

Al crear o editar un cliente con descuento > 0 el formulario sugiere automáticamente hoy + 2 meses como fecha de vigencia, con un preview en tiempo real que indica si el descuento está activo o ya venció.

---

## Seguridad e Idempotencia

El sistema implementa **idempotencia end-to-end**: la misma operación puede ejecutarse múltiples veces produciendo siempre el mismo resultado, sin efectos secundarios duplicados.

### Mecanismos de protección

| Mecanismo | Descripción |
|---|---|
| 🔑 **Sesión Django** | Autenticación con separación estricta de roles: clientes y administradores usan flujos de login independientes con validación cruzada. |
| 🛡️ **CSRF** | Activo en todas las peticiones POST, incluyendo AJAX con `X-CSRFToken`. Corregido en `add_to_cart` para usar POST en lugar de GET. |
| 🔐 **Bcrypt** | Hash de contraseñas con 10 rondas de salt a través del sistema de auth de Django. |
| 💳 **Validación Luhn** | Verificación matemática del número de tarjeta en tiempo real con feedback visual progresivo. |
| 🃏 **Enmascaramiento PCI** | Tarjetas y cuentas se almacenan parcialmente enmascaradas (`1234 XXXX XXXX 5678`) — nunca en texto plano. |
| 🔁 **UUID Idempotency Key** | Generado en el GET del checkout/formulario, viaja en campo hidden y se almacena con constraint `UNIQUE` en la BD. |
| ⚛️ **Transacciones atómicas** | `ATOMIC_REQUESTS=True` + `@transaction.atomic` en operaciones críticas. |
| 🔒 **select_for_update() + F()** | Bloqueo a nivel de fila e incremento atómico en el carrito y ventas para eliminar race conditions. |
| 💉 **SQL Injection** | ORM de Django con queries parametrizadas. Sin concatenación de strings SQL. |
| 🔄 **Reintentos con backoff** | `GeminiAIClient` reintenta hasta 3 veces ante errores 503/UNAVAILABLE con espera exponencial (1.5s → 3s → 6s). |
| 🧹 **Limpieza de sesión** | El logout borra el historial del chatbot de `localStorage` antes de redirigir, evitando que datos de un usuario queden expuestos a otro. |

### Flujo de idempotencia (Checkout)

```
GET /checkout/  →  Genera UUID  →  uuid en campo hidden del formulario
       │
       ▼
POST submit  →  ¿Existe Sale con ese UUID?
       │                    │
       │              SÍ ──►  redirect a venta existente (sin procesar)
       │              NO ──►  crear venta + guardar UUID + descontar stock
       │
       ▼
Botón deshabilitado en JS al primer clic (defensa en profundidad)
```

### Operaciones protegidas

| Operación | Riesgo sin protección | Mecanismo aplicado |
|---|---|---|
| **Checkout cliente** | Doble clic genera dos ventas y descuenta stock dos veces | UUID en campo hidden + constraint UNIQUE en BD + botón deshabilitado en JS |
| **Crear venta (admin)** | Doble clic en "Guardar" crea ventas duplicadas | UUID en payload JSON + verificación en backend + botón deshabilitado en JS |
| **Agregar al carrito** | Dos clics rápidos suman +2 en lugar de +1 | `select_for_update()` + `F('quantity') + 1` (atómico en BD) |
| **Eliminar venta** | Fallo a mitad deja stock inconsistente | `@transaction.atomic` envuelve restauración + eliminación |
| **Registro de usuario** | Race condition crea dos usuarios con mismo email | `get_or_create` + captura de `IntegrityError` |

---

## Chatbot con IA contextual

El chatbot usa **Google Gemini Flash** con contexto dinámico construido por el patrón **Builder/Director**. Cada rol recibe un prompt y un conjunto de datos diferente, ensamblados por `ChatContextDirector` a partir de builders especializados.

### Contexto por rol

| Rol | Datos inyectados en el prompt |
|---|---|
| **Admin** | Inventario completo · Resumen de ventas (24h / 7d / 30d) · Ticket promedio · Top 5 productos · Alertas de stock crítico (≤5 uds) · Productos agotados · Últimas 10 ventas con detalle |
| **Cliente** | Catálogo disponible (stock > 0) · Historial de últimas 5 compras · **Estado del descuento personal** (activo con fecha, vencido, o sin descuento) · Métodos de pago activos |
| **Visitante** | Totales de catálogo (productos, categorías, marcas) · Métodos de pago · Invitación a registrarse |

### Conocimiento del sistema de descuentos

El chatbot conoce el estado exacto del descuento de cada cliente gracias al `CustomerContextBuilder` actualizado:

```
Cliente con descuento activo   → bot informa porcentaje, fecha de vigencia
                                  y condiciones (personal + Efectivo/Tarjeta)
Cliente con descuento vencido  → bot informa que el descuento no aplica
                                  y sugiere contactar al administrador
Cliente sin descuento          → bot no menciona descuentos
Admin pregunta por descuentos  → bot explica mecánica completa: asignación,
                                  vigencia, condiciones y cómo renovar
```

Las acciones rápidas del chatbot están diferenciadas por rol. El admin tiene accesos directos a métricas, alertas de stock y análisis. El cliente tiene accesos a tienda, búsqueda de productos y consulta de su descuento. El visitante tiene accesos a catálogo y proceso de registro.

---

## Compatibilidad Cross-Browser

Auditoría completa aplicada sobre toda la codebase frontend:

| Categoría | Fix aplicado | Archivo |
|---|---|---|
| 🔴 **Crítico** | `navigator.hardwareConcurrency` con fallback `\|\| 2` para Safari iOS antiguo | `scan_barcode.js` |
| 🔴 **Crítico** | Constraints avanzados de cámara movidos a `applyConstraints()` con `try/catch` | `scan_barcode.js` |
| 🔴 **Crítico** | Fallback a cámara frontal si `OverconstrainedError` en iOS | `scan_barcode.js` |
| 🔴 **Crítico** | `add_to_cart` cambiado de GET a POST para evitar caché de proxies y cumplir semántica HTTP | `cart.py`, `shop.html` |
| 🔴 **Crítico** | Valores del checkout leídos desde `data-attributes` DOM, no desde template tags dentro de JS | `checkout.js`, `checkout.html` |
| 🟡 **Advertencia** | `position: sticky` con prefijo `-webkit-sticky` para Safari < 13 | `base.css` |
| 🟡 **Advertencia** | `backdrop-filter` con prefijo `-webkit-backdrop-filter` para Firefox < 103 | `base.css` |
| 🟡 **Advertencia** | Spin buttons ocultos en `readonly` inputs para Safari | `sale_form.css`, `base.css` |
| 🔵 **Informativo** | `@media (prefers-reduced-motion: reduce)` para animaciones accesibles | `base.css` |
| 🔵 **Informativo** | `line-clamp: 2` estándar junto al prefijo webkit | `base.css` |
| 🔵 **Informativo** | Placeholder en `input[type=date]` para Safari < 14.1 | `product_form.html` |

---

## Sistema de Diseño Frontend

Todos los formularios y páginas principales siguen un sistema de diseño consistente:

**Tipografía:** Plus Jakarta Sans (base) · Syne (títulos) · DM Sans (descripción)

**Paleta por módulo:**

| Módulo | Color de acento | CSS |
|---|---|---|
| Clientes | Verde (`#16a34a`) | `customer_form.css` |
| Vendedores | Azul (`#2563eb`) | `seller_form.css` |
| Productos | Púrpura (`#7c3aed`) | `product_form.css` |
| Ventas | Cyan (`#0ea5e9`) | `sale_form.css` |
| Eliminaciones | Rojo (`#dc2626`) | `*_delete.css` |
| Tienda cliente | Verde (`#14532d`) | navbar |
| Panel admin | Rojo oscuro (`#991b1b`) | navbar |

**Componentes comunes:** Cards con gradiente en header, inputs con focus ring animado, botones con sombra y hover lift, breadcrumbs, grid-2/grid-3 responsive.

**Formulario de descuento:** Preview dinámico en tiempo real con badge de estado (activo/vencido), sugerencia automática de fecha hoy + 2 meses, y aviso informativo con las condiciones de aplicación.

---

## Módulos del Sistema

<table>
<tr>
<td width="33%" valign="top">

### 🛒 Tienda Online (Cliente)
- Catálogo público con filtros por categoría, marca y búsqueda
- Carrito con actualización dinámica y validación de stock
- Checkout con tipo de factura (Consumidor Final / Datos personales)
- Descuento personalizado aplicado automáticamente según vigencia y método de pago
- Preview del descuento en el GET del checkout con recalculo dinámico en JS
- Métodos de pago: Efectivo, Tarjeta de Crédito/Débito, Transferencia
- Historial de compras con descarga de facturas PDF

</td>
<td width="33%" valign="top">

### 🤖 Chatbot con IA
- Integración con Google Gemini Flash con reintentos automáticos
- Contexto dinámico con inventario, precios y políticas en tiempo real
- Respuestas diferenciadas por rol (visitante, cliente, administrador)
- **Clientes**: informa su descuento activo, condiciones y fecha de vigencia
- **Clientes**: avisa si el descuento expiró y sugiere renovarlo con el admin
- Admins reciben datos de ventas de últimas 24h/7d/30d y pueden gestionar descuentos
- Historial persistido en `localStorage` por usuario, limpiado al logout

</td>
<td width="33%" valign="top">

### ⚙️ Panel Administrativo
- CRUD completo de productos, categorías, marcas, clientes y vendedores
- **Gestión de descuentos** por cliente con porcentaje y fecha de vigencia
- Vista de lista con estado del descuento (activo / vencido / sin vigencia)
- Registro histórico de ventas con búsqueda, filtros y modal de detalle
- Generación automática de facturas PDF con datos censurados (PCI)
- Reportes con exportación a Excel (5 hojas: resumen, detalle, productos, categorías, vendedores/clientes)
- Dashboard con notificaciones de ventas de las últimas 24 horas

</td>
</tr>
</table>

### 📷 Escáner EAN-13

- Detección vía cámara con **QuaggaJS**
- **Sistema de votos**: requiere 3 lecturas consistentes del mismo código antes de confirmar
- **Validación matemática** del dígito de control (algoritmo EAN-13)
- Feedback visual progresivo con barra de confirmación en tiempo real
- Fallbacks cross-browser para Safari iOS, Firefox y cámaras sin modo trasero

---

## Modelos de Datos

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Category  │     │    Brand    │     │  PaymentMethod  │
└──────┬──────┘     └──────┬──────┘     └────────┬────────┘
       └──────────┬─────────┘                    │
                  │                              │
           ┌──────▼──────┐               ┌───────▼──────────────────┐
           │   Product   │               │          Sale             │
           │─────────────│◄──────────────│──────────────────────────│
           │ id_product  │  SaleDetail   │ id_sale                  │
           │ name        │               │ user (FK→User)           │
           │ price       │               │ customer (FK)            │
           │ stock       │               │ seller (FK)              │
           │ barcode     │               │ payment (FK)             │
           │ state       │               │ subtotal / iva / total   │
           └──────┬──────┘               │ card_number_masked       │
                  │                      │ transfer_account_masked  │
           ┌──────▼──────┐               │ idempotency_key (UUID) ◄─── UNIQUE
           │  CartItem   │               └───────────────────────────┘
           │─────────────│    ┌──────────────────────┐   ┌─────────────┐
           │ cart (FK)   │    │       Customer        │   │   Seller    │
           │ product (FK)│    │──────────────────────│   │─────────────│
           │ quantity    │    │ dni (unique)          │   │ dni (unique)│
           └─────────────┘    │ discount_percentage   │   │             │
                              │ discount_expiry ◄──── │   └─────────────┘
                              │ has_active_discount()  │
                              │ get_active_discount_pct│
                              └──────────────────────┘
```

**Constraints de integridad activos en PostgreSQL:**

```sql
CHECK (stock >= 0)         -- product_stock_non_negative
CHECK (price > 0)          -- product_price_non_negative
CHECK (subtotal >= 0)      -- sale_subtotal_non_negative
CHECK (iva >= 0)           -- sale_iva_non_negative
CHECK (discount >= 0)      -- sale_discount_non_negative
CHECK (total >= 0)         -- sale_total_non_negative
CHECK (quantity >= 1)      -- saledetail_quantity_non_negative
UNIQUE (idempotency_key)   -- super_sale (null permitido para ventas legacy)
UNIQUE (cart, product)     -- CartItem (evita duplicados en carrito)
```

---

## Instalación

### Requisitos previos

- Python `3.10+`
- PostgreSQL `15+`
- Cuenta de Google Cloud con API Key de Gemini
- Cuenta Gmail con Contraseña de Aplicación (para SMTP)

### Instalación rápida (Linux/Mac)

```bash
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado/app
chmod +x setup.sh && ./setup.sh
```

El script instala dependencias, crea la base de datos, ejecuta migraciones e inserta datos iniciales (65 categorías, 77 marcas, 11 métodos de pago).

### Instalación manual

```bash
# 1. Clonar y activar entorno virtual
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado
python -m venv env
source env/bin/activate        # Linux/Mac
# env\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r app/requirements.txt

# 3. Configurar variables de entorno (ver sección siguiente)

# 4. Ejecutar migraciones
cd app
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Levantar servidor
python manage.py runserver
```

> **Nota Windows (Git Bash):** Si el `setup.sh` no encuentra el entorno virtual automáticamente, te pedirá la ruta completa. Ej: `C:/proyecto/env`

---

## Variables de Entorno

Crear archivo `.env` en `/app/`:

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

# ── Django ────────────────────────────────────
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
    │   │   ├── forms/auth.py  # Registro con get_or_create idempotente
    │   │   └── views/auth.py  # Login dual · logout con limpieza localStorage
    │   └── super/              # Módulo principal del negocio
    │       ├── models.py      # Product · Sale · Cart · Customer (descuento+vigencia) · …
    │       ├── services/       # ← Capa de servicios (SOLID + Patrones)
    │       │   ├── ai_client.py           # DIP: AIClient ABC + GeminiAIClient
    │       │   ├── chat_context.py        # Builder+Director: contexto por rol
    │       │   │                          #   CustomerContextBuilder: descuento activo
    │       │   ├── checkout_service.py    # SRP: orquestación del checkout
    │       │   │                          #   calculate_totals: valida vigencia descuento
    │       │   ├── idempotency_service.py # Singleton: claves UUID
    │       │   └── payment_processors.py  # OCP + Strategy: procesadores de pago
    │       ├── views/
    │       │   ├── cart.py    # POST correcto · select_for_update + F()
    │       │   ├── sale.py    # UUID idempotency · select_for_update · F()
    │       │   ├── chatbot.py # Gemini · contexto por rol · prompts de descuento
    │       │   ├── customer.py # CRUD clientes · gestión de descuentos
    │       │   └── shop.py / product.py / seller.py / home.py / reports.py
    │       ├── form/
    │       │   └── customer.py # CustomerForm: discount_percentage + discount_expiry
    │       └── urls.py        # 25+ rutas del módulo
    ├── templates/             # Templates HTML por módulo
    │   └── super/customers/
    │       ├── customer_form.html  # Preview dinámico del descuento en JS
    │       └── customer_list.html  # Badge de estado (activo/vencido/sin vigencia)
    ├── static/
    │   ├── css/
    │   │   ├── components/    # base.css · home.css · menu.css · about.css
    │   │   ├── customer/      # customer_form.css · customer_delete.css
    │   │   ├── seller/        # seller_form.css · seller_delete.css
    │   │   ├── product/       # product_form.css · product_delete.css
    │   │   ├── sale/          # sale_form.css · sale_delete.css
    │   │   ├── reports/       # reports.css
    │   │   └── security/      # auth_form.css · signup_form.css
    │   └── js/
    │       ├── checkout.js        # Luhn · validación · descuento dinámico en JS
    │       ├── sale.js            # Idempotencia UUID · botón anti-doble-clic
    │       ├── scan_barcode.js    # Quagga · votos · EAN-13 · cross-browser
    │       ├── chatbot.js         # localStorage por usuario · historial · acciones rápidas
    │       ├── barcode_validation.js
    │       ├── expiration_date.js
    │       ├── generate_password.js
    │       └── validations.js
    ├── manage.py
    ├── requirements.txt
    └── setup.sh               # Script de instalación automática
```

---

## Changelog

### v1.3.0 — Sistema de Descuentos + Chatbot Contextual

- ✅ **Campo `discount_expiry`** en modelo `Customer`: fecha límite hasta la que aplica el descuento, con migración `0002_customer_discount_expiry`
- ✅ **Helpers de negocio**: `has_active_discount()` y `get_active_discount_pct()` en el modelo — fuente única de verdad usada por vistas, checkout y chatbot
- ✅ **CheckoutService**: `calculate_totals()` valida tipo de factura + método de pago + vigencia antes de aplicar descuento; nunca aplica en Consumidor Final ni Transferencia
- ✅ **Checkout GET**: preview del descuento potencial con recalculo dinámico en JS al cambiar tipo de factura o método de pago
- ✅ **Anti-doble-clic**: botón de finalizar compra deshabilitado tras el primer clic + protección UUID idempotente en backend
- ✅ **CustomerForm**: campos `discount_percentage` + `discount_expiry` con sugerencia automática de hoy + 2 meses
- ✅ **Preview dinámico**: JS en `customer_form.html` muestra badge activo/vencido y descripción del descuento en tiempo real mientras el admin escribe
- ✅ **Lista de clientes**: tres estados visuales del descuento — activo (verde + fecha), vencido (rojo + fecha), sin vigencia (gris + aviso)
- ✅ **CustomerContextBuilder**: consulta `has_active_discount()` y construye contexto personalizado para el chatbot con estado exacto del descuento del cliente autenticado
- ✅ **Prompt de cliente**: instrucciones explícitas sobre cuándo aplica y cuándo no el descuento; el bot informa, no inventa
- ✅ **Prompt de admin**: punto dedicado a la mecánica de descuentos para responder preguntas de gestión
- ✅ **Aviso en checkout**: cuando el descuento no aplica (Consumidor Final / Transferencia) se muestra un aviso explicativo al cliente
- ✅ **Sidebar del checkout**: refleja el descuento y el total final en tiempo real sincronizado con el formulario

### v1.2.0 — Diseño Frontend + Auditoría Cross-Browser

- ✅ **Sistema de diseño unificado**: Plus Jakarta Sans, paleta por módulo, cards con gradiente, focus states animados
- ✅ **CSS modular**: 10 archivos CSS separados por módulo (customer, seller, product, sale, security, components, reports)
- ✅ **Navbar rediseñado**: cliente (verde) y admin (rojo oscuro), mobile-first con hamburger, user pill, cart badge
- ✅ **Home page rediseñada**: hero fullscreen, floating cards, stats bar, products section, why-us, CTA bottom
- ✅ **Formularios rediseñados**: customer, seller, product, sale con sistema de diseño consistente
- ✅ **Delete pages rediseñadas**: customer, seller, product, sale con card centrada y notas contextuales
- ✅ **Auditoría cross-browser crítica**: `add_to_cart` cambiado de GET a POST con CSRF
- ✅ **Fix crítico checkout.js**: valores numéricos leídos desde `data-attributes` DOM, no desde template tags en JS estático
- ✅ **Fix scan_barcode.js**: `hardwareConcurrency` con fallback, constraints avanzados con `try/catch`, fallback a cámara frontal
- ✅ **Prefijos webkit**: `position: sticky`, `backdrop-filter`, `line-clamp` con fallbacks
- ✅ **Accesibilidad**: `prefers-reduced-motion` en animaciones, placeholder para `input[type=date]` en Safari
- ✅ **Chatbot mejorado**: limpieza de `localStorage` al logout, clave de storage por usuario/rol
- ✅ **GeminiAIClient**: reintentos automáticos con backoff exponencial ante errores 503/UNAVAILABLE
- ✅ **Módulo de Reportes**: vista con filtros avanzados, KPIs, gráficos Chart.js y exportación Excel (5 hojas)

### v1.1.0 — Arquitectura SOLID + Idempotencia

- ✅ **Idempotencia en checkout**: `idempotency_key` UUID con constraint UNIQUE en `Sale`
- ✅ **Idempotencia en ventas admin**: UUID en payload JSON de `SaleCreateView`
- ✅ **Race condition en carrito**: `select_for_update()` + `F('quantity') + 1` (atómico en BD)
- ✅ **Atomicidad en eliminación**: `@transaction.atomic` en `SaleDeleteView`
- ✅ **Protección cliente**: botón submit deshabilitado tras primer clic
- ✅ **SRP**: servicios extraídos a `core/super/services/`
- ✅ **OCP + Strategy**: `PaymentProcessor` extensible sin modificar checkout
- ✅ **DIP**: `ChatbotProxyView` depende de `AIClient` (abstracción ABC)
- ✅ **Singleton**: `IdempotencyService` con instancia única compartida
- ✅ **Builder/Director**: `ChatContextDirector` ensambla contexto por rol
- ✅ **Setup.sh mejorado**: detección automática del virtualenv en múltiples rutas
- ✅ **Tests unitarios**: `PaymentProcessor` e `IdempotencyService` cubiertos

### v1.0.0 — Versión inicial funcional

---

## Desarrollador

<div align="center">

**Kadir Barquet Bravo**
Full Stack Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-kadir--barquet--bravo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kadir-barquet-bravo/)
[![GitHub](https://img.shields.io/badge/GitHub-Kadir011-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kadir011)
[![Email](https://img.shields.io/badge/Email-barquetbravokadir%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:barquetbravokadir@gmail.com)

<br/>

<sub>Built with ❤️ in Guayaquil, Ecuador · Django 5.1.4 · Python 3.10+ · v1.3.0</sub>

</div>