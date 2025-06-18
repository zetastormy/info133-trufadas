import FreeSimpleGUI as sg
import datetime

def create_ingresar_ventas_window(cursor, conn):
    cursor.execute("SELECT id_vendedor, nombre FROM vendedor")
    vendedores = cursor.fetchall()
    vendedores_list = [f"{id} - {nombre}" for id , nombre in vendedores]
    
    layout = [
        [sg.Text("Ventas realizadas", font = "Any 12 bold")],
        [sg.Text("Ingrese monto: ", font = "Any 10 bold")],
        [sg.Input(key = 'MONTO')],
        [sg.Text("Ingrese el metodo de pago: ", font="Any 10 bold"), 
         sg.Combo(['Efectivo', 'Débito', 'Transferencia'], readonly=True ,key = 'METODO', enable_events=True)],
        [sg.Text("Ingrese fecha(dd-mm-aaaa): ", font = "Any 10 bold")],
        [sg.Input(key = 'FECHA')],
        [sg.Text("ID Vendedor:", font = "Any 10 bold")],
        [sg.Combo(vendedores_list, key = "VENDEDOR", readonly=True)],
        [sg.Text("ID Cliente", font = "Any 10 bold")],
        [sg.Input(key="CLIENTE")],
        [sg.Button("Guardar"), sg.Button("Volver")]
    ]

    resultWindow = sg.Window("volver", layout)

    while True:
        event, values = resultWindow.read()
        if event == sg.WIN_CLOSED or event == "Volver":
            break

        if event == "Guardar":
            if not values['VENDEDOR'] or not values['CLIENTE'] or not values['MONTO'] or not values['METODO'] or not values['FECHA']:
                sg.popup_error("Debes llenar todos los campos")
                continue
            
            try:
                id_vendedor = int(values['VENDEDOR'].split(" - ")[0]) 
                id_cliente = int(values['CLIENTE'])
                monto = int(values['MONTO'])
            except ValueError:
                sg.popup_error("Los IDs deben ser enteros y el monto debe ser un número")
                continue

            cursor.execute("SELECT 1 FROM cliente WHERE id_cliente = %s", (id_cliente,))
            if cursor.fetchone() is None:
                sg.popup_error("El cliente no existe")
                continue

            try:
                fecha = datetime.datetime.strptime(values['FECHA'], "%d-%m-%Y")
            except ValueError:
                sg.popup_error("La fecha debe tener el formato dd-mm-aaaa")
                continue

            try:
                cursor.execute("""INSERT INTO venta (monto, medio_pago, fecha, id_vendedor, id_cliente)
                               VALUES (%s, %s, %s, %s, %s)""", (monto, values['METODO'], fecha, id_vendedor, id_cliente))
                conn.commit()
                sg.popup("Venta registrada con éxito")
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error al registrar la venta: {e}")

            
    resultWindow.close()