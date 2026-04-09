from django.core.management.base import BaseCommand
from core.super.models import Category, Brand, PaymentMethod

class Command(BaseCommand):
    help = 'Inserta los datos iniciales (Categorías, Marcas, Métodos de Pago) en la Base de Datos.'

    def handle(self, *args, **kwargs):
        # ── Configuración de colores ANSI para la terminal ──
        GREEN = '\033[92m'
        BLUE = '\033[94m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        self.stdout.write(f"\n{BOLD}{BLUE}===================================================={RESET}")
        self.stdout.write(f"{BOLD}{BLUE}       INICIANDO CARGA DE DATOS INICIALES           {RESET}")
        self.stdout.write(f"{BOLD}{BLUE}===================================================={RESET}\n")

        # ── Listas de datos extraídas de tu script ──
        categories = [
            'Frutas y verduras', 'Carnes rojas', 'Pollos y aves', 'Pescados y mariscos', 'Embutidos y fiambres',
            'Panaderías', 'Pastelería', 'Lácteos', 'Huevos', 'Congelados', 'Enlatados', 'Arroz y granos',
            'Pastas', 'Harinas', 'Aceites y grasas', 'Sal y especias', 'Salsas y aderezos', 'Conservas',
            'Cereales', 'Agua', 'Jugos', 'Gaseosas', 'Bebidas energéticas', 'Bebidas alcohólicas',
            'Bebidas isotónicas', 'Té y café', 'Galletas', 'Chocolates', 'Caramelos', 'Frituras',
            'Frutos secos', 'Barras energéticas', 'Jabónes', 'Shampoos y acondicionadores', 'Pasta dentales',
            'Desodorantes', 'Productos de afeitar', 'Higiene femenina', 'Detergentes', 'Suavizantes',
            'Desinfectantes', 'Limpiadores multiuso', 'Lavavajillas', 'Esponjas y paños', 'Papel higiénico',
            'Servilletas', 'Toallas de papel', 'Pañuelos', 'Bolsas de basura', 'Pañales', 'Toallitas húmedas',
            'Alimentos para bebés', 'Leche infantil', 'Productos de higiene para bebés', 'Alimento para perros',
            'Alimento para gatos', 'Juguetes para perros', 'Juguetes para gatos', 'Snacks para mascotas',
            'Arena para gatos', 'Accesorios básicos', 'Productos orgánicos', 'Productos sin gluten',
            'Productos dietéticos', 'Productos importados'
        ]

        brands = [
            'Arroz Súper Extra', 'Arroz Donato', 'Goya', 'La Favorita', 'Facundo', 'Oriental', 'Del Monte',
            'La Costeña', 'Isabel', 'Van Camps', 'Real', 'La Europea', 'Campomar', 'Sardimar', 'Toni',
            'Nestlé', 'Parmalat', 'Alpina', 'La Lechera', 'Nutrileche', 'Coca-Cola', 'Pepsi', 'Sprite',
            'Fanta', 'Inca Kola', 'Dasani', 'Ciel', 'Powerade', 'Gatorade', 'Red Bull', 'Nescafé',
            'Juan Valdez', 'Minerva', 'Si Café', 'Lipton', 'Hornimans', 'Ferrero', 'Oreo', 'Ritz',
            'Club Social', 'Pringles', 'Lays', 'Doritos', 'Trident', 'Colgate', 'Oral-B', 'Dove',
            'Rexona', 'Axe', 'Pantene', 'Head & Shoulders', 'Sedal', 'Gillette', 'Ariel', 'Ace', 'Deja',
            'Fab', 'Mr. Músculo', 'Clorox', 'Fabuloso', 'Ajax', 'Sapolio', 'Familia', 'Scott', 'Elite',
            'Rosal', 'Suave', 'Pampers', 'Huggies', 'Babysec', "Johnson's Baby", 'Nestlé Baby', 'Dog Chow',
            'Cat Chow', 'Pedigree', 'Whiskas', 'Purina', 'Pro Plan'
        ]

        payment_methods = [
            'Efectivo', 'Tarjeta de crédito', 'Tarjeta de débito', 'Transferencia bancaria', 'Pago móvil',
            'Billetera electrónica', 'Código QR', 'Cheque', 'Crédito del local', 'Vales / cupones', 'Gift Card'
        ]

        # ── Función reutilizable para insertar datos ──
        def load_data(model, data_list, name_label):
            self.stdout.write(f"  {YELLOW}▶ Procesando catálogo de {name_label}...{RESET}")
            created_count = 0
            
            for item in data_list:
                # get_or_create revisa si existe, si no, lo crea. Retorna una tupla (objeto, booleano)
                obj, created = model.objects.get_or_create(name=item)
                if created:
                    created_count += 1
            
            # Mostramos el resultado con sangría
            if created_count > 0:
                self.stdout.write(f"      {GREEN}✔ {created_count} nuevos registros insertados.{RESET}")
            
            already_exists = len(data_list) - created_count
            if already_exists > 0:
                self.stdout.write(f"      {BLUE}ℹ {already_exists} registros ya existían (omitidos).{RESET}")
                
            self.stdout.write("") # Salto de línea estético

        # Ejecutamos la función para cada modelo
        load_data(Category, categories, 'Categorías')
        load_data(Brand, brands, 'Marcas')
        load_data(PaymentMethod, payment_methods, 'Métodos de Pago')

        self.stdout.write(f"{BOLD}{GREEN}=== PROCESO COMPLETADO EXITOSAMENTE ==={RESET}\n")