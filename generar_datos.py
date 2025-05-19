import psycopg2
import random
from faker import Faker

fake = Faker("es_CL")

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='trufadas',
    user='zetastormy',
    password=''
)

cursor = conn.cursor()

productos = [
    ('Trufa coñac', 500),
    ('Trufa ron', 500),
    ('Trufa menta', 500),
    ('Trufa chocolate', 500),
    ('Cocadas con maní', 500),
    ('Cocadas', 500),
    ('Pan con chicharrón', 1200),
]

insumos = [
    ('Crema', 2500, '200 mL'),
    ('Chocolate Semibutter', 6500, '1 kg'),
    ('Galletas Vino', 1200, '160 g'),
    ('Esencia coñac', 2300, '25 g'),
    ('Esencia ron', 2300, '25 g'),
    ('Esencia menta', 2300, '25 g'),
    ('Maní', 3890, '1 kg'),
    ('Coco Rayado', 11800, '1 kg'),
    ('Manjar Nestlé', 3590, '1 kg'),
    ('Harina sin polvos de hornear', 1700, '1 kg'),
    ('Levadura', 800, '250 g'),
    ('Sal', 450, '1 kg'),
    ('Huevos caja', 47000, '180 u'),
    ('Aceite', 2000, '1 L'),
    ('Chicharrón Hecho', 10500, '1 kg'),
    ('Manteca', 4000, '1 kg'),
    ('Bolsas PP 10 cm x 15 cm', 700, '100 u'),
]

# Insertar productos
for nombre, precio in productos:
    cursor.execute("""
        INSERT INTO productos (nombre, precio)
        VALUES (%s, %s)
    """, (nombre, precio))

# Insertar insumos
for nombre, precio, medida in insumos:
    cursor.execute("""
        INSERT INTO insumos (nombre, precio, medida)
        VALUES (%s, %s, %s)
    """, (nombre, precio, medida))

# Insertar clientes
for _ in range(50):
    nombre = fake.first_name()
    genero = random.choice(["M", "F"])
    cursor.execute("INSERT INTO clientes (nombre, genero) VALUES (%s, %s)", (nombre, genero))

# Insertar vendedores
for _ in range(4):
    nombre = fake.name()
    correo = fake.email()
    cursor.execute("INSERT INTO vendedores (nombre, correo) VALUES (%s, %s)", (nombre, correo))

# Obtener datos existentes
cursor.execute("SELECT id_cliente FROM clientes")
clientes = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT id_vendedor FROM vendedores")
vendedores = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT id_producto, nombre, precio FROM productos")
productos = cursor.fetchall()

medios_pago = ["Efectivo", "Débito", "Transferencia"]

def es_combo(nombre):
    return 'trufa' in nombre.lower() or 'cocada' in nombre.lower()

for venta_id in range(1, 501):
    cliente = random.choice(clientes)
    vendedor = random.choice(vendedores)
    fecha = fake.date_time_between(start_date='-4y', end_date='now')
    medio = random.choice(medios_pago)

    if random.random() < 0.5:
        combos = [p for p in productos if es_combo(p[1])]
        if len(combos) >= 3:
            elegidos = random.sample(combos, 3)
            for pid, _, _ in elegidos:
                cursor.execute("""
                    INSERT INTO hechos_ventas (id_venta, monto_total, id_cliente, fecha, id_vendedor, medio_pago, id_producto, cantidad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (venta_id, 400, cliente, fecha, vendedor, medio, pid, 1))
    else:
        elegidos = random.sample(productos, random.randint(1, 3))
        for pid, _, precio in elegidos:
            cantidad = random.randint(1, 3)
            total = cantidad * precio
            cursor.execute("""
                INSERT INTO hechos_ventas (id_venta, monto_total, id_cliente, fecha, id_vendedor, medio_pago, id_producto, cantidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (venta_id, total, cliente, fecha, vendedor, medio, pid, cantidad))

# Insertar hechos_compras si hay insumos
cursor.execute("SELECT id_insumo FROM insumos")
insumos = [x[0] for x in cursor.fetchall()]

for _ in range(30):
    insumo = random.choice(insumos)
    cantidad = random.randint(100, 1000)
    fecha = fake.date_time_between(start_date='-4y', end_date='now')
    cursor.execute("""
        INSERT INTO hechos_compras (id_insumo, cantidad, fecha)
        VALUES (%s, %s, %s)
    """, (insumo, cantidad, fecha))

conn.commit()
cursor.close()
conn.close()
