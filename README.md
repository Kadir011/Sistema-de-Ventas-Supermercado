<div align="center">

<br/>

<img src="https://img.shields.io/badge/-%F0%9F%9B%92%20MY%20SUPERMARKET-7f1d1d?style=for-the-badge&labelColor=991b1b&color=b91c1c&logoColor=white" alt="MySupermarket" height="52"/>

<h3>Full-Stack E-Commerce & POS Platform</h3>

<p>
  Production Django system shipped with SOLID architecture, end-to-end idempotency,<br/>
  real-time AI chatbot, and a cross-browser-audited frontend. <strong>Live on Render.</strong>
</p>

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-my--supermarket--6l71.onrender.com-b91c1c?style=for-the-badge&labelColor=7f1d1d)](https://my-supermarket-6l71.onrender.com)

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white&labelColor=0d1117)](https://djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=flat-square&logo=postgresql&logoColor=white&labelColor=0d1117)](https://neon.tech/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white&labelColor=0d1117)](https://tailwindcss.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Flash-4285F4?style=flat-square&logo=google&logoColor=white&labelColor=0d1117)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white&labelColor=0d1117)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square&labelColor=0d1117)](LICENSE)

<br/>

![SOLID](https://img.shields.io/badge/SOLID_Architecture-6366f1?style=flat-square&labelColor=0d1117)
![Strategy](https://img.shields.io/badge/Strategy_Pattern-f59e0b?style=flat-square&labelColor=0d1117)
![Singleton](https://img.shields.io/badge/Singleton_Pattern-ec4899?style=flat-square&labelColor=0d1117)
![Builder](https://img.shields.io/badge/Builder%2FDirector-10b981?style=flat-square&labelColor=0d1117)
![Idempotency](https://img.shields.io/badge/End--to--end_Idempotency-0ea5e9?style=flat-square&labelColor=0d1117)
![Cloudinary](https://img.shields.io/badge/Cloudinary_Media-3448C5?style=flat-square&logo=cloudinary&logoColor=white&labelColor=0d1117)

</div>

---

## What this project actually demonstrates

This is not a tutorial project. It's a production-deployed system built from scratch that solves real business problems — dual-mode (POS + e-commerce), personalized discount lifecycle management, race condition prevention, and AI that actually knows your inventory.

The decisions behind it are the interesting part:

- **Why idempotency via UUID instead of just disabling the button?** — The button is a UX hint. The UUID constraint at the DB layer is the guarantee. Both exist. Double-click, network retry, tab duplication — none of them create a duplicate sale.
- **Why Strategy for payments instead of if/elif?** — Adding a new payment method means writing one class and registering it. The checkout never changes. That's OCP in practice, not in a diagram.
- **Why Singleton for IdempotencyService?** — One shared instance ensures the same UUID parse and lookup logic everywhere. No state leaks, no re-instantiation overhead per request.
- **Why Builder/Director for chatbot context?** — The AI receives a completely different payload depending on role. The Director assembles it from specialized builders without the view knowing anything about what goes in.

---

## Table of Contents

- [What this project actually demonstrates](#what-this-project-actually-demonstrates)
- [Table of Contents](#table-of-contents)
- [🌐 Live Demo](#-live-demo)
- [Architecture Overview](#architecture-overview)
- [Engineering Decisions](#engineering-decisions)
  - [SOLID in Practice](#solid-in-practice)
  - [Design Patterns](#design-patterns)
  - [Idempotency \& Concurrency](#idempotency--concurrency)
  - [Discount System with Expiry](#discount-system-with-expiry)
  - [AI Chatbot with Role Context](#ai-chatbot-with-role-context)
- [Tech Stack](#tech-stack)
- [Cross-Browser Audit](#cross-browser-audit)
- [Frontend Design System](#frontend-design-system)
- [Modules](#modules)
  - [🛒 Customer Storefront](#-customer-storefront)
  - [⚙️ Admin Panel](#️-admin-panel)
  - [🤖 AI Chatbot](#-ai-chatbot)
  - [📷 EAN-13 Scanner](#-ean-13-scanner)
  - [📊 Reports](#-reports)
- [Data Models](#data-models)
- [🐳 Docker Setup](#-docker-setup)
- [🖥️ Local Setup](#️-local-setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Changelog](#changelog)
  - [v1.3.0 — Discount System + Contextual Chatbot](#v130--discount-system--contextual-chatbot)
  - [v1.2.0 — Frontend Design System + Cross-Browser Audit](#v120--frontend-design-system--cross-browser-audit)
  - [v1.1.0 — SOLID Architecture + Idempotency](#v110--solid-architecture--idempotency)
  - [v1.0.0 — Initial release](#v100--initial-release)
- [Developer](#developer)

---

## 🌐 Live Demo

> Deployed on **Render** · PostgreSQL on **Neon** · Media on **Cloudinary** · Static files via **WhiteNoise**

**[https://my-supermarket-6l71.onrender.com](https://my-supermarket-6l71.onrender.com)**

<div align="center">

| Path | Description |
|---|---|
| `/` | Public homepage |
| `/security/login/` | Login — customer or admin tabs |
| `/menu/` | Admin dashboard |
| `/tienda/` | Customer storefront |
| `/scan_barcode/` | EAN-13 barcode scanner |

</div>

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│   Tailwind CSS 3.x · JavaScript ES6+ · QuaggaJS (EAN-13)        │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP/HTTPS
┌───────────────────────────▼──────────────────────────────────────┐
│                    DJANGO 5.1.4                                   │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │ Thin Views  │  │ Middlewares  │  │    URL Routing       │    │
│  │             │  │ CSRF · Auth  │  │   25+ routes         │    │
│  └──────┬──────┘  └──────────────┘  └──────────────────────┘    │
│         │ delegates to                                           │
│  ┌──────▼──────────────────────────────────────┐                 │
│  │           Service Layer  (SOLID)             │                 │
│  │                                             │                 │
│  │  CheckoutService        ← SRP               │                 │
│  │  PaymentProcessor       ← OCP + Strategy    │                 │
│  │  IdempotencyService     ← Singleton         │                 │
│  │  ChatContextDirector    ← Builder/Director  │                 │
│  │  GeminiAIClient         ← DIP (AIClient ABC)│                 │
│  └──────┬──────────────────────────────────────┘                 │
│         │                                                        │
│  ┌──────▼──────┐  ┌──────────────────────────────────────────┐  │
│  │   ORM       │  │  select_for_update() + F() expressions   │  │
│  │  Models     │  │  UUID idempotency_key UNIQUE constraint   │  │
│  └─────────────┘  │  ATOMIC_REQUESTS = True                  │  │
│                   └──────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
┌─────────────▼──────────┐  ┌────────────▼────────────┐
│   PostgreSQL (Neon)     │  │   Google Gemini API     │
│   SSL required          │  │   Exponential backoff   │
│   CHECK constraints     │  │   Role-aware prompts    │
└────────────────────────┘  └─────────────────────────┘
```

---

## Engineering Decisions

### SOLID in Practice

Every principle has a concrete location in the codebase — not aspirational, but verifiable:

<div align="center">

| Principle | Where | What it prevents |
|---|---|---|
| **S** — Single Responsibility | `CheckoutService`, `StoreContextBuilder`, `SalesContextBuilder`, `CustomerContextBuilder`, `ChatContextDirector` | Views that balloon into 200-line functions mixing business logic with HTTP handling |
| **O** — Open/Closed | `PaymentProcessor` + `PAYMENT_PROCESSORS` registry | Modifying checkout logic to add a new payment method — just add a class |
| **L** — Liskov Substitution | `CashPaymentProcessor`, `CardPaymentProcessor`, `TransferPaymentProcessor` | Runtime errors when swapping payment implementations |
| **I** — Interface Segregation | `AIClient(ABC)` exposes only `generate()` | Concrete clients forced to implement irrelevant methods |
| **D** — Dependency Inversion | `ChatbotProxyView` depends on `AIClient`, not `GeminiAIClient` | Swapping the AI provider requires zero changes to the view |

</div>

### Design Patterns

**Strategy — Payment processing**

```python
# Adding a new payment method: write one class, register it. Done.
class WalletPaymentProcessor(PaymentProcessor):
    def calculate_received_and_change(self, total, post_data):
        return total, Decimal('0.00')

PAYMENT_PROCESSORS['billetera electrónica'] = WalletPaymentProcessor()
```

**Singleton — Idempotency service**

```python
class IdempotencyService:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

One shared instance. Same UUID parse logic everywhere. No hidden state divergence.

**Builder / Director — AI context assembly**

```python
class ChatContextDirector:
    def build_for_role(self, role: str, user=None) -> dict:
        store_ctx = self.store_builder.build()
        if role == 'admin':
            return {'store_ctx': store_ctx, 'sales_ctx': self.sales_builder.build(), ...}
        elif role == 'customer':
            return {'store_ctx': store_ctx, 'extra_ctx': self.customer_builder.build(user), ...}
        ...
```

The view calls `build_for_role()`. It doesn't know whether it's querying sales stats, customer history, or guest totals — that's the Director's job.

---

### Idempotency & Concurrency

**The problem being solved:** A customer double-clicks "Pay". Two POST requests hit the server within milliseconds. Both read the cart. Both pass validation. Without protection: two `Sale` records, stock decremented twice, two PDF invoices.

**The solution (defense in depth):**

```
Client side:   Button disabled on first click
              ↓
Transport:     UUID generated on GET, travels in hidden field
              ↓
Service layer: IdempotencyService.find_existing(key) → redirect if found
              ↓
Database:      UNIQUE constraint on idempotency_key → IntegrityError if race wins
```

The DB constraint is the actual guarantee. The rest is UX and latency reduction.

**Race conditions on cart updates:**

```python
# Instead of: item.quantity += 1; item.save()  ← read-modify-write race
CartItem.objects.filter(pk=cart_item.pk).update(quantity=F('quantity') + 1)
# The increment happens in a single atomic SQL UPDATE
```

**Stock decrement on sale creation:**

```python
with transaction.atomic():
    product = Product.objects.select_for_update().get(pk=detail['product'])
    # Row locked until transaction commits — concurrent requests queue behind it
    Product.objects.filter(pk=product.pk).update(stock=F('stock') - quantity)
```

---

### Discount System with Expiry

The admin assigns a `discount_percentage` + `discount_expiry` date per customer. The model owns the business logic:

```python
def has_active_discount(self) -> bool:
    if not self.discount_percentage or self.discount_percentage <= 0:
        return False
    if not self.discount_expiry:
        return False
    return self.discount_expiry >= timezone.localdate()
```

This single method is the source of truth. `CheckoutService`, the chatbot's `CustomerContextBuilder`, and the admin list view all call it — no duplicated date comparison logic anywhere.

**Discount eligibility matrix:**

<div align="center">

| Invoice type | Payment method | Discount applies? |
|---|---|---|
| Personal data | Cash / Card | ✅ Yes |
| Personal data | Bank transfer | ❌ No |
| Consumidor Final | Any | ❌ No |
| Any | Expired expiry date | ❌ No |
| Any | Empty expiry date | ❌ No |

</div>

---

### AI Chatbot with Role Context

Three completely separate system prompts, assembled at request time from live DB data:

<div align="center">

| Role | What the model receives |
|---|---|
| **Admin** | Full inventory · Sales summary (24h / 7d / 30d) · Average ticket · Top 5 products · Low-stock alerts (≤5 units) · Last 10 transactions |
| **Customer** | Available catalog · Last 5 purchases · **Active discount status** (percentage + expiry date) · Active payment methods |
| **Guest** | Catalog totals · Payment methods · Registration invitation |

</div>

The Gemini client retries transient 503 errors with exponential backoff (1.5s → 3s → 6s, max 3 attempts) before surfacing an error to the user.

---

## Tech Stack

<div align="center">

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.10+ | Base |
| Framework | Django | 5.1.4 | Web framework |
| Database | PostgreSQL (Neon) | 15+ | Relational DB with SSL |
| AI | Google Gemini Flash | — | Contextual chatbot |
| Media | Cloudinary | — | Image storage in production |
| Static files | WhiteNoise | 6.8.2 | Serve statics without CDN |
| Hosting | Render | — | PaaS deployment |
| CSS | Tailwind CSS | 3.x | Utility-first styling |
| PDF | xhtml2pdf | 0.2.17 | Invoice generation |
| Excel | openpyxl | 3.1.5 | 5-sheet report export |
| Barcode | QuaggaJS | 0.12.1 | EAN-13 camera scanner |

</div>

---

## Cross-Browser Audit

Tested across Chrome, Firefox, Safari, and Edge. Critical fixes shipped in v1.2.0:

<div align="center">

| Severity | Issue | Fix | File |
|---|---|---|---|
| 🔴 Critical | `navigator.hardwareConcurrency` undefined on Safari iOS | Fallback `|| 2` | `scan_barcode.js` |
| 🔴 Critical | Advanced camera constraints crash on iOS | Moved to `applyConstraints()` with `try/catch` | `scan_barcode.js` |
| 🔴 Critical | `OverconstrainedError` on iOS — no rear camera | Fallback to front camera | `scan_barcode.js` |
| 🔴 Critical | `add_to_cart` used GET with side effects | Changed to POST + CSRF | `cart.py`, `shop.html` |
| 🔴 Critical | Django template tags inside static JS file | Values moved to `data-attributes` on DOM elements | `checkout.js` |
| 🟡 Warning | `position: sticky` broken on Safari < 13 | Added `-webkit-sticky` prefix | `base.css` |
| 🟡 Warning | `backdrop-filter` unsupported on Firefox < 103 | Added `-webkit-backdrop-filter` + alpha fallback | `base.css` |
| 🟡 Warning | Spin buttons on `readonly` number inputs in Safari | Hidden via `-webkit-appearance: none` | `sale_form.css` |
| 🔵 Info | Missing `prefers-reduced-motion` support | `@media` query disables all animations | `base.css` |
| 🔵 Info | `line-clamp` vendor prefix missing | Added standard `line-clamp: 2` alongside webkit | `base.css` |

</div>

---

## Frontend Design System

**Typography:** Plus Jakarta Sans (UI) · Syne (headings) · DM Sans (body copy)

**Color system — module-scoped accents:**

<div align="center">

| Module | Accent | Variable |
|---|---|---|
| Customers | Green `#16a34a` | `customer_form.css` |
| Sellers | Blue `#2563eb` | `seller_form.css` |
| Products | Purple `#7c3aed` | `product_form.css` |
| Sales | Cyan `#0ea5e9` | `sale_form.css` |
| Deletions | Red `#dc2626` | `*_delete.css` |
| Customer store navbar | Dark green `#14532d` | `base.css` |
| Admin panel navbar | Dark red `#991b1b` | `base.css` |

</div>

**10 scoped CSS files** — no global style bleed between modules. Each form carries its own accent color without touching shared styles.

---

## Modules

### 🛒 Customer Storefront
Category / brand / search filters · Cart with live stock validation · Checkout with invoice type selection (Consumidor Final vs. personal data) · Automatic discount application by payment method and expiry · Cash / Card / Transfer payment flows · Order history with PDF invoice download

### ⚙️ Admin Panel
Full CRUD: products, categories, brands, customers (with discount management), sellers, users · Sale registry and history · Modal sale detail viewer · PDF invoice generation with PCI-masked card/account numbers · 5-sheet Excel report export with advanced filters · Dashboard with 24h sales notification badge

### 🤖 AI Chatbot
Role-differentiated system prompts assembled from live DB data · Admin receives sales KPIs and inventory alerts · Customers receive their discount status and purchase history · Guests receive catalog summary and registration invitation · Persistent history in `localStorage` per user, cleared on logout

### 📷 EAN-13 Scanner
Camera access via QuaggaJS · 3-vote consensus before confirming a read (prevents false positives from reflective packaging) · Mathematical check digit validation · Cross-browser fallbacks for Safari iOS and Firefox

### 📊 Reports
KPIs: revenue, sales count, average ticket, discounts granted · Daily revenue chart (Chart.js) · Payment method breakdown (doughnut) · Top 15 products by units · Revenue by category with progress bars · Top 5 sellers and customers · Date range quick-selects (7 / 30 / 90 days / this month) · Export to Excel with same filters applied

---

## Data Models

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Category  │     │    Brand    │     │  PaymentMethod  │
└──────┬──────┘     └──────┬──────┘     └────────┬────────┘
       └──────────┬─────────┘                    │
                  │                              │
           ┌──────▼──────┐               ┌───────▼──────────────────────────┐
           │   Product   │               │              Sale                 │
           │─────────────│◄──────────────│──────────────────────────────────│
           │ barcode     │  SaleDetail   │ idempotency_key UUID  ← UNIQUE    │
           │ stock       │               │ card_number_masked                │
           │ price       │               │ transfer_account_masked           │
           │ state       │               │ discount                         │
           └─────────────┘               └───────────────────────────────────┘
                                                      │
                                         ┌────────────▼──────────────┐
                                         │         Customer          │
                                         │  discount_percentage      │
                                         │  discount_expiry ◄──date  │
                                         │  has_active_discount()    │
                                         │  get_active_discount_pct()│
                                         └───────────────────────────┘
```

**PostgreSQL constraints enforced at DB level:**

```sql
CHECK (stock >= 0)          -- product_stock_non_negative
CHECK (price > 0)           -- product_price_non_negative
CHECK (subtotal >= 0)       -- sale_subtotal_non_negative
CHECK (iva >= 0)            -- sale_iva_non_negative
CHECK (discount >= 0)       -- sale_discount_non_negative
CHECK (total >= 0)          -- sale_total_non_negative
CHECK (quantity >= 1)       -- saledetail_quantity_non_negative
UNIQUE (idempotency_key)    -- super_sale
UNIQUE (cart, product)      -- CartItem
```

---

## 🐳 Docker Setup

> **Recommended** — zero dependency installation, up in under 2 minutes.

**Prerequisites:** Docker 24+, Docker Compose v2+, Gemini API key, Gmail App Password

```bash
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado
cp .env.example .env   # then fill in your values — see Environment Variables below
docker compose up --build
```

Services started:

<div align="center">

| Service | Image | Host port |
|---|---|---|
| `db` | `postgres:14.10-alpine` | `5433` |
| `web` | Built from `Dockerfile` | `8000` |

</div>

`web` waits for `db` healthcheck before starting. On launch it runs `collectstatic`, `migrate`, then `runserver`.

```bash
# Load seed data (65 categories, 77 brands, 11 payment methods)
docker compose exec web python manage.py initial_data

# Create admin user
docker compose exec web python manage.py createsuperuser
```

**Useful commands:**

```bash
docker compose logs -f web          # tail logs
docker compose down -v              # stop + wipe volumes (clean DB)
docker compose up --build web       # rebuild after requirements changes
docker compose exec web python manage.py test
```

> ℹ️ Source is bind-mounted as a volume — code changes reflect immediately without rebuild. Only `requirements.txt` or `Dockerfile` changes need `--build`.

---

## 🖥️ Local Setup

**Prerequisites:** Python 3.10+, PostgreSQL 15+, `psql` in PATH

```bash
git clone https://github.com/Kadir011/Sistema-de-Ventas-Supermercado.git
cd Sistema-de-Ventas-Supermercado

python -m venv env
source env/bin/activate          # Linux / macOS
# env\Scripts\activate.bat       # Windows CMD
# source env/Scripts/activate    # Windows Git Bash

pip install -r app/requirements.txt
```

Copy `.env` into `app/` (see [Environment Variables](#environment-variables) — use `DB_SOCKET=localhost`), then:

```bash
cd app
chmod +x setup.sh && ./setup.sh   # creates DB, runs migrations, loads seed data
python manage.py createsuperuser
python manage.py runserver
```

**Manual steps (without the script):**

```bash
psql -U postgres -c "CREATE DATABASE my_supermarket;"
python manage.py migrate
python manage.py initial_data
python manage.py createsuperuser
python manage.py runserver
```

---

## Environment Variables

Place in project root for Docker, or in `/app/` for local setup.

```env
# ── Database ───────────────────────────────────
DB_ENGINE=django.db.backends.postgresql
DB_DATABASE=my_supermarket
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_SOCKET=localhost          # Docker: use "db"
DB_PORT=5432

# ── Email (Gmail SMTP) ─────────────────────────
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your_app_password   # App Password, not account password
DEFAULT_FROM_EMAIL=you@gmail.com

# ── Google Gemini AI ───────────────────────────
GEMINI_API_KEY=your_api_key

# ── Django ────────────────────────────────────
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ── Cloudinary (production media) ─────────────
CLOUDINARY_URL=cloudinary://key:secret@cloud_name
```

> ⚠️ `.env` is listed in both `.gitignore` and `.dockerignore`. Never commit it.

---

## Project Structure

```
django_supermercado/
├── docker-compose.yml
├── Dockerfile
└── app/
    ├── config/
    │   ├── settings.py          # ATOMIC_REQUESTS=True, Cloudinary, WhiteNoise
    │   └── urls.py
    ├── core/
    │   ├── security/            # Custom AbstractUser with user_type field
    │   │   ├── models.py
    │   │   └── views/auth.py    # Dual-tab login, logout with localStorage cleanup
    │   └── super/
    │       ├── models.py        # All domain models with DB constraints
    │       ├── services/        # ← The interesting part
    │       │   ├── ai_client.py           # DIP: AIClient ABC + GeminiAIClient
    │       │   ├── chat_context.py        # Builder/Director pattern
    │       │   ├── checkout_service.py    # SRP: checkout orchestration
    │       │   ├── idempotency_service.py # Singleton
    │       │   └── payment_processors.py  # Strategy pattern
    │       ├── views/           # Thin controllers — delegate to services
    │       ├── form/
    │       └── urls.py          # 25+ routes
    ├── templates/
    ├── static/
    │   ├── css/                 # 10 scoped CSS files
    │   └── js/                  # checkout.js · sale.js · scan_barcode.js · chatbot.js
    ├── requirements.txt
    └── setup.sh
```

---

## Changelog

### v1.3.0 — Discount System + Contextual Chatbot
- `discount_expiry` DateField on `Customer` with migration `0002`
- `has_active_discount()` and `get_active_discount_pct()` — single source of truth
- `CheckoutService.calculate_totals()` validates invoice type + payment method + expiry before applying discount
- Discount preview on checkout GET; JS recalculates on payment method change
- `CustomerContextBuilder` injects exact discount state into chatbot prompt
- Admin customer list: three visual states — active (green), expired (red), no expiry (gray)
- Customer form: auto-suggest today + 2 months as default expiry

### v1.2.0 — Frontend Design System + Cross-Browser Audit
- Unified design system: Plus Jakarta Sans, per-module color palette, gradient cards
- 10 scoped CSS files, one per module
- Navbar redesign: customer (green) and admin (dark red), mobile-first
- Critical cross-browser fixes: `add_to_cart` POST, `checkout.js` data-attributes, QuaggaJS iOS fallbacks
- `GeminiAIClient` with exponential backoff on 503 errors
- Reports module: advanced filters, Chart.js charts, Excel export (5 sheets)

### v1.1.0 — SOLID Architecture + Idempotency
- `idempotency_key` UUID with UNIQUE constraint on `Sale`
- `select_for_update()` + `F()` expressions on cart and admin sale views
- Service layer extraction: `CheckoutService`, `PaymentProcessor`, `IdempotencyService`
- Strategy pattern for payment processors
- Builder/Director for chatbot context assembly
- Unit tests for `PaymentProcessor` and `IdempotencyService`

### v1.0.0 — Initial release

---

## Developer

<div align="center">

**Kadir Barquet Bravo**

Full Stack Developer — Guayaquil, Ecuador

*Available for remote opportunities*

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-kadir--barquet--bravo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kadir-barquet-bravo/)
[![GitHub](https://img.shields.io/badge/GitHub-Kadir011-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kadir011)
[![Email](https://img.shields.io/badge/Email-barquetbravokadir%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:barquetbravokadir@gmail.com)
[![Live](https://img.shields.io/badge/Live_Demo-my--supermarket-b91c1c?style=for-the-badge&logo=render&logoColor=white)](https://my-supermarket-6l71.onrender.com)

<br/>

<sub>Django 5.1.4 · Python 3.10+ · PostgreSQL (Neon) · Cloudinary · Render · v1.3.0</sub>

</div>