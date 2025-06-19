import FreeSimpleGUI as sg
import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os
from ventas import create_ingresar_ventas_window
from productos import *

sg.theme('SandyBeach')
fake = Faker("es_CL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

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

    with open(os.path.join(BASE_DIR, "tables.sql"), "r", encoding="utf-8") as f:
        tables_script = f.read()

    cursor.execute(tables_script)

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

def load_env():
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH, override=True)

        return {
            "host": os.getenv("HOST"),
            "port": os.getenv("PORT"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        }
    return None

def save_env(host, port, dbname, user, password):
    with open(ENV_PATH, 'w') as f:
        f.write(f"DB_HOST={host}\n")
        f.write(f"DB_PORT={port}\n")
        f.write(f"DB_NAME={dbname}\n")
        f.write(f"DB_USER={user}\n")
        f.write(f"DB_PASSWORD={password}\n")

def connect_from_env():
    config = load_env()
    if config:
        try:
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                dbname=config["dbname"],
                user=config["user"],
                password=config["password"]
            )
            return conn
        except Exception as e:
            sg.popup_error("Error al conectar desde .env:", str(e))
    return None

def prefill_env_values():
    config = load_env()
    if config:
        return {
            'HOST': config['host'],
            'PORT': config['port'],
            'DB_NAME': config['dbname'],
            'DB_USER': config['user'],
            'DB_PASSWORD': config['password']
        }
    return {}

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

    return sg.Window("Trufadas", layout)

def create_data_window(prefilled_values=None):
    if prefilled_values is None:
        prefilled_values = {}

    layout = [
        [sg.Text("Ingrese host:", font="Any 10 bold")],
        [sg.InputText(default_text=prefilled_values.get('HOST', ''), key='HOST')],
        
        [sg.Text("Ingrese puerto:", font="Any 10 bold")],
        [sg.InputText(default_text=prefilled_values.get('PORT', ''), key='PORT')],
        
        [sg.Text("Ingrese nombre base de datos:", font="Any 10 bold")],
        [sg.InputText(default_text=prefilled_values.get('DB_NAME', ''), key='DB_NAME')],
        
        [sg.Text("Ingrese usuario:", font="Any 10 bold")],
        [sg.InputText(default_text=prefilled_values.get('DB_USER', ''), key='DB_USER')],
        
        [sg.Text("Ingrese contraseña:", font="Any 10 bold")],
        [sg.InputText(default_text=prefilled_values.get('DB_PASSWORD', ''), key='DB_PASSWORD', password_char='*')],
        
        [sg.Button("Guardar y generar datos"), sg.Button("Volver")]
    ]
    return sg.Window("Ingresar datos de base datos", layout)

def main():
    conn = connect_from_env()
    cursor = conn.cursor() if conn else None

    if conn:
        try:
            sg.popup("¡Se ha conectado correctamente a la base de datos anteriormente especificada!")
        except Exception as e:
            sg.popup("Error al conectarse a la base de datos de .env:", str(e))
    
    mainWindow = create_main_window()

    while True:
        event, values = mainWindow.read()

        if event == "Ingresar venta":
            if cursor == None:
                sg.popup("¡Debe especificar su base de datos previamente en el botón \"Cargar datos de prueba\"!")
                continue
            
            try:
                create_ingresar_ventas_window(cursor, conn)
            except Exception as e:
                sg.popup("¡Debe crear datos de prueba antes de usar esta función!")

        if event == "Ingresar producto":
            if cursor == None:
                sg.popup("¡Debe especificar su base de datos previamente en el botón \"Cargar datos de prueba\"!")
                continue
            
            try:
                create_ingresar_producto_window(cursor, conn)
            except Exception as e:
                sg.popup("¡Debe crear datos de prueba antes de usar esta función!")

        if event == "Listar productos":
            if cursor == None:
                sg.popup("¡Debe especificar su base de datos previamente en el botón \"Cargar datos de prueba\"!")
                continue
            
            try:
                create_listar_productos_window(cursor)
            except Exception as e:
                sg.popup("¡Debe crear datos de prueba antes de usar esta función!")

        if event == "Modificar producto":
            if cursor == None:
                sg.popup("¡Debe especificar su base de datos previamente en el botón \"Cargar datos de prueba\"!")
                continue
            
            try:
                create_modificar_producto_window(cursor, conn)
            except Exception as e:
                sg.popup("¡Debe crear datos de prueba antes de usar esta función!")            
        
        if event == "Eliminar producto":
            if cursor == None:
                sg.popup("¡Debe especificar su base de datos previamente en el botón \"Cargar datos de prueba\"!")
                continue
            
            try:
                create_eliminar_producto_window(cursor, conn)
            except Exception as e:
                sg.popup("¡Debe crear datos de prueba antes de usar esta función!")

        if event == "Cargar datos de prueba":
            dataWindow = create_data_window(prefill_env_values())
            while True:
                event_data, values_data = dataWindow.read()
                if event_data == "Guardar y generar datos":
                    try:
                        save_env(values_data["HOST"], values_data["PORT"], values_data["DB_NAME"], values_data["DB_USER"], values_data["DB_PASSWORD"])
                        conn = connect_from_env()

                        if conn:
                            cursor = conn.cursor()

                            sg.popup_no_buttons("Por favor, espere unos segundos a que se carguen los datos.", auto_close=True, auto_close_duration=3)
                            load_test_data(cursor)
                            conn.commit()
                            sg.popup_no_buttons("¡Se han insertado los datos de prueba correctamente!", auto_close=True, auto_close_duration=3)
                        else:
                            sg.popup_error("No se pudo establecer la conexión.")
                    except Exception as e:
                        sg.popup_error(f"Ocurrió un error: {e}")
                if event_data in (sg.WINDOW_CLOSED, "Volver"):
                    dataWindow.close()
                    break

        if event in (sg.WINDOW_CLOSED, "Salir"):
            break

    if conn:
        conn.close()
    mainWindow.close()

if __name__ == "__main__":
    main()
