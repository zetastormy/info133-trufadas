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
