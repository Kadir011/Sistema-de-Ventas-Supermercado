#!/bin/bash

# Configuración de colores para la terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Configuración de Base de Datos y Entorno ===${NC}"

# ── 1. Verificar herramientas básicas ─────────────────────────────────────────
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: PostgreSQL (psql) no está en el PATH.${NC}"
    exit 1
fi

# ── 2. Detectar entorno virtual (rutas posibles) ──────────────────────────────
# El script puede ejecutarse desde /app/ o desde la raíz del proyecto.
# Se prueba en orden: rutas hermanas (../env), locales (./env) y la ruta
# absoluta construida dinámicamente desde la ubicación real del script.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Candidatos en orden de prioridad
VENV_CANDIDATES=(
    "$SCRIPT_DIR/../env"          # Estructura original: /proyecto/env  + /proyecto/app/setup.sh
    "$SCRIPT_DIR/env"             # Entorno dentro de /app/env
    "$SCRIPT_DIR/../venv"         # Alternativa con nombre 'venv'
    "$SCRIPT_DIR/venv"            # Alternativa local con nombre 'venv'
)

VENV_PATH=""
ACTIVATE_PATH=""

echo -e "\n${YELLOW}[INFO] Buscando entorno virtual...${NC}"

for candidate in "${VENV_CANDIDATES[@]}"; do
    # Normalizar la ruta (resuelve .. y symlinks)
    resolved="$(cd "$candidate" 2>/dev/null && pwd)"
    if [ -z "$resolved" ]; then
        continue
    fi

    # Windows (Git Bash): Scripts/activate
    if [ -f "$resolved/Scripts/activate" ]; then
        VENV_PATH="$resolved"
        ACTIVATE_PATH="$resolved/Scripts/activate"
        echo -e "${GREEN}[OK] Entorno encontrado (Windows): $VENV_PATH${NC}"
        break
    fi

    # Unix/Mac: bin/activate
    if [ -f "$resolved/bin/activate" ]; then
        VENV_PATH="$resolved"
        ACTIVATE_PATH="$resolved/bin/activate"
        echo -e "${GREEN}[OK] Entorno encontrado (Unix): $VENV_PATH${NC}"
        break
    fi
done

# Si no encontró ninguno, preguntar la ruta manualmente
if [ -z "$VENV_PATH" ]; then
    echo -e "${RED}[ERROR] No se encontró el entorno virtual en las rutas predeterminadas.${NC}"
    echo -e "${YELLOW}Rutas buscadas:${NC}"
    for c in "${VENV_CANDIDATES[@]}"; do
        echo "  - $c"
    done
    echo ""
    read -p "Ingresa la ruta completa a tu entorno virtual (ej: C:/ruta/al/env): " MANUAL_PATH

    # Normalizar separadores (Windows usa \ pero bash prefiere /)
    MANUAL_PATH="${MANUAL_PATH//\\//}"

    if [ -f "$MANUAL_PATH/Scripts/activate" ]; then
        VENV_PATH="$MANUAL_PATH"
        ACTIVATE_PATH="$MANUAL_PATH/Scripts/activate"
    elif [ -f "$MANUAL_PATH/bin/activate" ]; then
        VENV_PATH="$MANUAL_PATH"
        ACTIVATE_PATH="$MANUAL_PATH/bin/activate"
    else
        echo -e "${RED}[ERROR] Tampoco se encontró activate en '$MANUAL_PATH'. Verifica la ruta.${NC}"
        exit 1
    fi
fi

# Activar el entorno
source "$ACTIVATE_PATH"
echo -e "${GREEN}[OK] Entorno virtual activado.${NC}"

# ── 3. Instalar requerimientos ────────────────────────────────────────────────
echo -e "\n${GREEN}[1/5] Verificando e instalando dependencias...${NC}"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

# ── 4. Solicitar credenciales ─────────────────────────────────────────────────
echo -e "\n${YELLOW}Introduce los datos de conexión a PostgreSQL:${NC}"
read -p "Usuario (default: postgres): " PG_USER
PG_USER=${PG_USER:-postgres}
read -sp "Contraseña para '$PG_USER': " PG_PASSWORD
echo
read -p "Nombre de la Base de Datos a crear: " DB_NAME
read -p "Host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}
read -p "Puerto (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

export PGPASSWORD=$PG_PASSWORD

# ── 5. Reiniciar base de datos ────────────────────────────────────────────────
echo -e "\n${GREEN}[2/5] Reiniciando base de datos '$DB_NAME'...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"

# ── 6. Ejecutar migraciones ───────────────────────────────────────────────────
echo -e "\n${GREEN}[3/5] Ejecutando migraciones de Django...${NC}"
cd "$SCRIPT_DIR"
python manage.py makemigrations
python manage.py migrate

# ── 7. Cargar datos iniciales ─────────────────────────────────────────────────
echo -e "\n${GREEN}[4/5] Insertando Categorías, Marcas y Métodos de Pago...${NC}"
TEMP_SQL="$SCRIPT_DIR/temp_init_data.sql"

cat <<SQLEOF > "$TEMP_SQL"
SET client_encoding = 'UTF8';

INSERT INTO super_category (name) VALUES
('Frutas y verduras'), ('Carnes rojas'), ('Pollos y aves'), ('Pescados y mariscos'), ('Embutidos y fiambres'),
('Panaderías'), ('Pastelería'), ('Lácteos'), ('Huevos'), ('Congelados'), ('Enlatados'), ('Arroz y granos'),
('Pastas'), ('Harinas'), ('Aceites y grasas'), ('Sal y especias'), ('Salsas y aderezos'), ('Conservas'),
('Cereales'), ('Agua'), ('Jugos'), ('Gaseosas'), ('Bebidas energéticas'), ('Bebidas alcohólicas'),
('Bebidas isotónicas'), ('Té y café'), ('Galletas'), ('Chocolates'), ('Caramelos'), ('Frituras'),
('Frutos secos'), ('Barras energéticas'), ('Jabónes'), ('Shampoos y acondicionadores'), ('Pasta dentales'),
('Desodorantes'), ('Productos de afeitar'), ('Higiene femenina'), ('Detergentes'), ('Suavizantes'),
('Desinfectantes'), ('Limpiadores multiuso'), ('Lavavajillas'), ('Esponjas y paños'), ('Papel higiénico'),
('Servilletas'), ('Toallas de papel'), ('Pañuelos'), ('Bolsas de basura'), ('Pañales'), ('Toallitas húmedas'),
('Alimentos para bebés'), ('Leche infantil'), ('Productos de higiene para bebés'), ('Alimento para perros'),
('Alimento para gatos'), ('Juguetes para perros'), ('Juguetes para gatos'), ('Snacks para mascotas'),
('Arena para gatos'), ('Accesorios básicos'), ('Productos orgánicos'), ('Productos sin gluten'),
('Productos dietéticos'), ('Productos importados');

INSERT INTO super_brand (name) VALUES
('Arroz Súper Extra'), ('Arroz Donato'), ('Goya'), ('La Favorita'), ('Facundo'), ('Oriental'), ('Del Monte'),
('La Costeña'), ('Isabel'), ('Van Camps'), ('Real'), ('La Europea'), ('Campomar'), ('Sardimar'), ('Toni'),
('Nestlé'), ('Parmalat'), ('Alpina'), ('La Lechera'), ('Nutrileche'), ('Coca-Cola'), ('Pepsi'), ('Sprite'),
('Fanta'), ('Inca Kola'), ('Dasani'), ('Ciel'), ('Powerade'), ('Gatorade'), ('Red Bull'), ('Nescafé'),
('Juan Valdez'), ('Minerva'), ('Si Café'), ('Lipton'), ('Hornimans'), ('Ferrero'), ('Oreo'), ('Ritz'),
('Club Social'), ('Pringles'), ('Lays'), ('Doritos'), ('Trident'), ('Colgate'), ('Oral-B'), ('Dove'),
('Rexona'), ('Axe'), ('Pantene'), ('Head & Shoulders'), ('Sedal'), ('Gillette'), ('Ariel'), ('Ace'), ('Deja'),
('Fab'), ('Mr. Músculo'), ('Clorox'), ('Fabuloso'), ('Ajax'), ('Sapolio'), ('Familia'), ('Scott'), ('Elite'),
('Rosal'), ('Suave'), ('Pampers'), ('Huggies'), ('Babysec'), ('Johnson''s Baby'), ('Nestlé Baby'), ('Dog Chow'),
('Cat Chow'), ('Pedigree'), ('Whiskas'), ('Purina'), ('Pro Plan');

INSERT INTO super_paymentmethod (name) VALUES
('Efectivo'), ('Tarjeta de crédito'), ('Tarjeta de débito'), ('Transferencia bancaria'), ('Pago móvil'),
('Billetera electrónica'), ('Código QR'), ('Cheque'), ('Crédito del local'), ('Vales / cupones'), ('Gift Card');
SQLEOF

psql -h "$DB_HOST" -p "$DB_PORT" -U "$PG_USER" -d "$DB_NAME" -f "$TEMP_SQL"

# ── 8. Limpieza final ─────────────────────────────────────────────────────────
echo -e "\n${GREEN}[5/5] Finalizando proceso...${NC}"
rm "$TEMP_SQL"
unset PGPASSWORD

echo -e "\n${GREEN}¡Configuración completada con éxito!${NC}"
echo -e "Ahora puedes ejecutar: ${YELLOW}python manage.py createsuperuser${NC}"