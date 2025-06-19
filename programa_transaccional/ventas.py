import FreeSimpleGUI as sg 
from datetime import datetime

def create_ingresar_ventas_window(cursor, conn):
    cursor.execute("SELECT * FROM venta")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    cursor.execute("SELECT id_vendedor, nombre FROM vendedor")
    vendedores = cursor.fetchall()
    vendedores_list = [f"{id} - {nombre}" for id , nombre in vendedores]

    cursor.execute("SELECT id_producto, nombre, precio FROM producto")
    productos = cursor.fetchall()
    productos_dict = {f"{id} - {nombre}": (id, precio) for id, nombre, precio in productos}
    productos_list = list(productos_dict.keys())

    def get_product_row(key_suffix):
        return [
            sg.Combo(productos_list, key=f"PRODUCTO_{key_suffix}", readonly=True, size=(25, 1)),
            sg.Input(key=f"CANTIDAD_{key_suffix}", size=(5, 1))
        ]

    layout = [
        [sg.Text("Ventas realizadas", font="Any 12 bold")],
        [sg.Text("Método de pago:", font="Any 10 bold"),
         sg.Combo(['Efectivo', 'Débito', 'Transferencia'], readonly=True, key='METODO')],
        [sg.Text("Fecha (dd-mm-aaaa):", font="Any 10 bold")],
        [sg.Input(key='FECHA')],
        [sg.Text("Vendedor:", font="Any 10 bold")],
        [sg.Combo(vendedores_list, key="VENDEDOR", readonly=True)],
        [sg.Text("ID Cliente:", font="Any 10 bold")],
        [sg.Input(key="CLIENTE")],
        [sg.Text("Productos:", font="Any 10 bold")],
        [sg.Column([get_product_row(0)], key='PRODUCT_ROWS')],
        [sg.Button("Agregar producto"), sg.Button("Guardar"), sg.Button("Volver")]
    ]

    resultWindow = sg.Window("Ingresar venta", layout, finalize=True)
    product_count = 1

    while True:
        event, values = resultWindow.read()
        if event in (sg.WINDOW_CLOSED, "Volver"):
            break

        if event == "Agregar producto":
            resultWindow.extend_layout(resultWindow['PRODUCT_ROWS'], [get_product_row(product_count)])
            product_count += 1

        if event == "Guardar":
            required_fields = ['METODO', 'FECHA', 'VENDEDOR', 'CLIENTE']
            if any(not values[field] for field in required_fields):
                sg.popup_error("Debes llenar todos los campos obligatorios.")
                continue

            try:
                id_vendedor = int(values['VENDEDOR'].split(" - ")[0])
                id_cliente = int(values['CLIENTE'])
                fecha = datetime.strptime(values['FECHA'], "%d-%m-%Y")
            except ValueError:
                sg.popup_error("ID Cliente debe ser numérico y fecha en formato válido.")
                continue

            cursor.execute("SELECT 1 FROM cliente WHERE id_cliente = %s", (id_cliente,))
            if cursor.fetchone() is None:
                sg.popup_error("El cliente no existe.")
                continue

            productos_agregados = []
            monto_total = 0
            for i in range(product_count):
                prod_key = f"PRODUCTO_{i}"
                cant_key = f"CANTIDAD_{i}"
                if prod_key in values and values[prod_key]:
                    try:
                        prod_str = values[prod_key]
                        id_prod, precio = productos_dict[prod_str]
                        cantidad = int(values[cant_key])
                        productos_agregados.append((id_prod, cantidad))
                        monto_total += cantidad * precio
                    except:
                        sg.popup_error(f"Revisa los valores del producto en la fila {i + 1}")
                        break

            if not productos_agregados:
                sg.popup_error("Debes agregar al menos un producto con su cantidad.")
                continue

            try:
                cursor.execute("""
                    INSERT INTO venta (monto, medio_pago, fecha, id_vendedor, id_cliente)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id_venta
                """, (monto_total, values['METODO'], fecha, id_vendedor, id_cliente))
                id_venta = cursor.fetchone()[0]

                for id_prod, cantidad in productos_agregados:
                    cursor.execute("""
                        INSERT INTO vender (id_venta, id_producto, cantidad)
                        VALUES (%s, %s, %s)
                    """, (id_venta, id_prod, cantidad))

                conn.commit()
                sg.popup(f"Venta registrada con éxito.\nMonto total: ${monto_total}")
                break
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error al registrar la venta: {e}")

    resultWindow.close()

def create_listar_ventas_window(cursor):
    cursor.execute("SELECT * FROM venta")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    cursor.execute("""
        SELECT v.id_venta, v.monto, v.medio_pago, v.fecha, c.nombre AS cliente, vd.nombre AS vendedor
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        JOIN vendedor vd ON v.id_vendedor = vd.id_vendedor
        WHERE v.borrado = FALSE
        ORDER BY v.fecha DESC
    """)
    ventas = cursor.fetchall()

    detalles = []
    for venta in ventas:
        cursor.execute("""
            SELECT p.nombre, ve.cantidad
            FROM vender ve
            JOIN producto p ON ve.id_producto = p.id_producto
            WHERE ve.id_venta = %s AND ve.borrado = FALSE
        """, (venta[0],))
        productos = cursor.fetchall()
        productos_str = ", ".join([f"{nombre} (x{cant})" for nombre, cant in productos])
        detalles.append(list(venta) + [productos_str])

    headings = ["ID Venta", "Monto", "Medio de pago", "Fecha", "Cliente", "Vendedor", "Productos"]
    layout = [
        [sg.Text("Listado de Ventas", font="Any 12 bold")],
        [sg.Table(values=detalles, headings=headings, auto_size_columns=True, justification='left',
                  key='-TABLE-', expand_x=True, expand_y=True, num_rows=10)],
        [sg.Button("Cerrar")]
    ]

    window = sg.Window("Ventas", layout, resizable=True)
    while True:
        event, _ = window.read()
        if event in (sg.WINDOW_CLOSED, "Cerrar"):
            break
    
    window.close()

def create_modificar_venta_window(cursor, conn):
    cursor.execute("SELECT * FROM venta")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    def get_product_row(productos_list, key_suffix, selected=None, cantidad=""):
        return [
            sg.Combo(productos_list, key=f"PRODUCTO_{key_suffix}", readonly=True, default_value=selected, size=(25, 1)),
            sg.Input(key=f"CANTIDAD_{key_suffix}", size=(5, 1), default_text=cantidad)
        ]

    cursor.execute("SELECT id_producto, nombre, precio FROM producto")
    productos = cursor.fetchall()
    productos_dict = {f"{id} - {nombre}": (id, precio) for id, nombre, precio in productos}
    productos_list = list(productos_dict.keys())

    layout = [
        [sg.Text("Modificar Venta", font="Any 12 bold")],
        [sg.Text("ID Venta a modificar:", font="Any 10 bold")],
        [sg.Input(key="ID_VENTA")],
        [sg.Button("Cargar Venta"), sg.Button("Cancelar")],
        [sg.Text("Productos vendidos:", font="Any 10 bold", key='PRODUCTS_TITLE', visible=False)],
        [sg.Column([], key='PRODUCT_ROWS', visible=False)]
    ]

    window = sg.Window("Modificar Venta", layout)
    product_count = 0
    venta_loaded = False

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break

        if event == "Cargar Venta":
            if venta_loaded:
                continue

            if not values["ID_VENTA"].isdigit():
                sg.popup_error("El ID de venta debe ser un número.")
                continue

            id_venta = int(values["ID_VENTA"])
            cursor.execute("SELECT medio_pago, fecha FROM venta WHERE id_venta = %s AND borrado = FALSE", (id_venta,))
            venta = cursor.fetchone()
            if not venta:
                sg.popup_error("Venta no encontrada.")
                continue

            metodo_pago, fecha = venta
            fecha_str = fecha.strftime("%d-%m-%Y")

            cursor.execute("""
                SELECT p.id_producto, p.nombre, v.cantidad
                FROM vender v
                JOIN producto p ON v.id_producto = p.id_producto
                WHERE v.id_venta = %s
            """, (id_venta,))
            productos_venta = cursor.fetchall()

            new_layout = [
                [sg.Text("Método de pago:", font="Any 10 bold"),
                 sg.Combo(['Efectivo', 'Débito', 'Transferencia'], key='METODO', default_value=metodo_pago, readonly=True)],
                [sg.Text("Nueva fecha (dd-mm-aaaa):", font="Any 10 bold")],
                [sg.Input(key="FECHA", default_text=fecha_str)],
            ]

            for id_prod, nombre, cantidad in productos_venta:
                key = f"{id_prod} - {nombre}"
                window.extend_layout(window['PRODUCT_ROWS'], [get_product_row(productos_list, product_count, key, cantidad)])
                product_count += 1

            window['PRODUCTS_TITLE'].update(visible=True)
            window['PRODUCT_ROWS'].update(visible=True)
            window.extend_layout(window, new_layout + [[sg.Button("Guardar")]])
            venta_loaded = True

        if event == "Guardar" and venta_loaded:
            if not values['FECHA'] or not values['METODO']:
                sg.popup_error("Debe llenar todos los campos.")
                continue

            try:
                fecha = datetime.strptime(values["FECHA"], "%d-%m-%Y")
            except ValueError:
                sg.popup_error("Formato de fecha inválido (debe ser dd-mm-aaaa).")
                continue

            nuevos_productos = []
            monto_total = 0

            for i in range(product_count):
                prod_key = f"PRODUCTO_{i}"
                cant_key = f"CANTIDAD_{i}"
                if prod_key in values and values[prod_key]:
                    try:
                        prod_str = values[prod_key]
                        id_prod, precio = productos_dict[prod_str]
                        cantidad = int(values[cant_key])
                        nuevos_productos.append((id_prod, cantidad))
                        monto_total += cantidad * precio
                    except:
                        sg.popup_error(f"Error en la fila de producto #{i+1}.")
                        break

            if not nuevos_productos:
                sg.popup_error("Debe ingresar al menos un producto.")
                continue

            try:
                cursor.execute("DELETE FROM vender WHERE id_venta = %s", (id_venta,))

                for id_prod, cantidad in nuevos_productos:
                    cursor.execute("""
                        INSERT INTO vender (id_venta, id_producto, cantidad)
                        VALUES (%s, %s, %s)
                    """, (id_venta, id_prod, cantidad))

                cursor.execute("""
                    UPDATE venta SET monto=%s, medio_pago=%s, fecha=%s WHERE id_venta=%s
                """, (monto_total, values['METODO'], fecha, id_venta))

                conn.commit()
                sg.popup(f"Venta actualizada correctamente.\nMonto recalculado: ${monto_total}")
                break
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error al modificar la venta: {e}")

    window.close()

def create_eliminar_venta_window(cursor, conn):
    cursor.execute("SELECT * FROM venta")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    layout = [
        [sg.Text("Eliminar Venta", font="Any 12 bold")],
        [sg.Text("Ingrese ID de la venta a eliminar:", font="Any 10 bold")],
        [sg.Input(key="ID_VENTA")],
        [sg.Button("Eliminar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Eliminar Venta", layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Eliminar":
            try:
                id_venta = int(values['ID_VENTA'])
                cursor.execute("SELECT 1 FROM venta WHERE id_venta = %s AND borrado = FALSE", (id_venta,))
                if cursor.fetchone() is None:
                    sg.popup_error("La venta no existe")
                    continue
                cursor.execute("UPDATE vender SET borrado = TRUE WHERE id_venta = %s", (id_venta,)) 
                cursor.execute("UPDATE venta SET borrado = TRUE WHERE id_venta = %s", (id_venta,))
                conn.commit()
                sg.popup("Venta eliminada correctamente")
                break
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error al eliminar la venta: {e}")
                
    window.close()