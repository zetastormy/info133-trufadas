import FreeSimpleGUI as sg
import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

sg.theme('SandyBeach')
fake = Faker("es_CL")

def load_test_data(cursor):
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
        cursor.execute("INSERT INTO producto (nombre, precio) VALUES (%s, %s)", (nombre, precio))

    # Insertar insumos
    for nombre, precio, medida in insumos:
        cursor.execute("INSERT INTO insumo (nombre, precio, unidad_medida) VALUES (%s, %s, %s)", (nombre, precio, medida))

    # Insertar clientes
    for _ in range(150):
        nombre = fake.first_name()
        genero = random.choice(["M", "F"])
        cursor.execute("INSERT INTO cliente (nombre, genero) VALUES (%s, %s)", (nombre, genero))

    # Insertar vendedores
    for _ in range(12):
        nombre = fake.name()
        correo = fake.email()
        cursor.execute("INSERT INTO vendedor (nombre, correo) VALUES (%s, %s)", (nombre, correo))

    # Obtener IDs
    cursor.execute("SELECT id_cliente FROM cliente")
    clientes = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT id_vendedor FROM vendedor")
    vendedores = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT id_producto, precio FROM producto")
    productos = cursor.fetchall()

    medios_pago = ["Efectivo", "Débito", "Transferencia"]

    start = datetime.now() - relativedelta(years=3)
    end = datetime.now()
    current = start.replace(day=1)

    while current <= end:
        for _ in range(500):
            fecha = current + timedelta(days=random.randint(0, 27), hours=random.randint(8, 20), minutes=random.randint(0, 59))
            cliente = random.choice(clientes)
            vendedor = random.choice(vendedores)
            medio = random.choice(medios_pago)

            cursor.execute(
                "INSERT INTO venta (monto, medio_pago, fecha, id_vendedor, id_cliente) VALUES (%s, %s, %s, %s, %s) RETURNING id_venta",
                (0, medio, fecha, vendedor, cliente)
            )
            id_venta = cursor.fetchone()[0]

            total = 0
            productos_elegidos = random.sample(productos, random.randint(1, 3))
            for prod_id, precio in productos_elegidos:
                cantidad = random.randint(1, 3)
                total += cantidad * precio
                cursor.execute(
                    "INSERT INTO vender (id_venta, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (id_venta, prod_id, cantidad)
                )

            # Actualizar monto total
            cursor.execute("UPDATE venta SET monto = %s WHERE id_venta = %s", (total, id_venta))

        current += relativedelta(months=1)

    # Reposiciones insumos (150 en total)
    cursor.execute("SELECT id_insumo FROM insumo")
    insumo_ids = [x[0] for x in cursor.fetchall()]

    for _ in range(150):
        insumo = random.choice(insumo_ids)
        cantidad = random.randint(50, 1000)
        fecha = fake.date_time_between(start_date='-3y', end_date='now')
        cursor.execute("""
            INSERT INTO reposicion_insumo (id_insumo, fecha, cantidad)
            VALUES (%s, %s, %s)
        """, (insumo, fecha, cantidad))

def create_main_window():
    buttons = ["Ingresar venta", 
        "Listar ventas", 
        "Modificar venta", 
        "Eliminar venta", 
        "Ingresar producto", 
        "Listar productos",
        "Modificar producto",
        "Eliminar producto",
        "Cargar datos de prueba"]
    max_length = max(len(b) for b in buttons)

    layout = [
        [sg.Text("Menú", font="Any 12 bold", justification='c', expand_x=True)],
        [sg.HorizontalSeparator()],
        [[[sg.Button(b, size=(max_length, 1))] for b in buttons]],
        [sg.HorizontalSeparator()],
        [sg.Button("Salir", size=(max_length, 1))]
    ]

    mainWindow = sg.Window("Trufadas", layout)

    return mainWindow

def main():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        dbname='trufadas_transaccional',
        user='zetastormy',
        password=''
    )

    cursor = conn.cursor()
    mainWindow = create_main_window()

    while True:
        event, values = mainWindow.read()
        
        if event == "Cargar datos de prueba":
            try:
                load_test_data(cursor)
                sg.popup(f"¡Se han insertado los datos de prueba correctamente!")
            except Exception as e:
                sg.popup(f"Ocurrió el siguiente error: {e}");
            
        if event in (sg.WINDOW_CLOSED, "Salir"):
            break

        conn.commit()

    mainWindow.close()

if __name__ == "__main__":
    main()
