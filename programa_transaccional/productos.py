import FreeSimpleGUI as sg

def create_ingresar_producto_window(cursor, conn):
    cursor.execute("SELECT * FROM producto")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    layout = [
        [sg.Text("Ingresar producto", font="Any 12 bold")],
        [sg.Text("Nombre:")],
        [sg.Input(key="NOMBRE")],
        [sg.Text("Precio:")],
        [sg.Input(key="PRECIO")],
        [sg.Button("Guardar"), sg.Button("Volver")]
    ]

    window = sg.Window("Ingresar producto", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Volver"):
            break

        if event == "Guardar":
            nombre = values["NOMBRE"].strip()
            try:
                precio = int(values["PRECIO"])
                if not nombre:
                    raise ValueError("Nombre vacío")
                cursor.execute("INSERT INTO producto (nombre, precio) VALUES (%s, %s)", (nombre, precio))
                conn.commit()
                sg.popup("Producto agregado correctamente")
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error: {e}")

    window.close()

def create_listar_productos_window(cursor):
    cursor.execute("SELECT * FROM producto")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    cursor.execute("SELECT id_producto, nombre, precio FROM producto WHERE NOT borrado")
    productos = cursor.fetchall()
    data = [[str(p[0]), p[1], str(p[2])] for p in productos]

    layout = [
        [sg.Text("Listado de productos", font="Any 12 bold")],
        [sg.Table(values=data, headings=["ID", "Nombre", "Precio"],
                  auto_size_columns=True, justification='left',
                  num_rows=min(20, len(data)), key='TABLE')],
        [sg.Button("Volver")]
    ]

    window = sg.Window("Listar productos", layout)
    while True:
        event, _ = window.read()
        if event in (sg.WINDOW_CLOSED, "Volver"):
            break
    window.close()

def create_modificar_producto_window(cursor, conn):
    cursor.execute("SELECT * FROM producto")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    layout = [
        [sg.Text("Modificar producto", font="Any 12 bold")],
        [sg.Text("ID del producto a modificar:"), sg.Input(key="ID")],
        [sg.Text("Nuevo nombre (dejar en blanco para no cambiar):")],
        [sg.Input(key="NOMBRE")],
        [sg.Text("Nuevo precio (dejar en blanco para no cambiar):")],
        [sg.Input(key="PRECIO")],
        [sg.Button("Actualizar"), sg.Button("Volver")]
    ]

    window = sg.Window("Modificar producto", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Volver"):
            break

        if event == "Actualizar":
            try:
                pid = int(values["ID"])

                cursor.execute("SELECT 1 FROM producto WHERE id_producto = %s AND borrado = FALSE", (pid,))
                if cursor.fetchone() is None:
                    sg.popup_error("El producto no existe")
                    continue

                nombre = values["NOMBRE"].strip()
                precio = values["PRECIO"].strip()
                campos = []
                datos = []

                if nombre:
                    campos.append("nombre = %s")
                    datos.append(nombre)
                if precio:
                    campos.append("precio = %s")
                    datos.append(int(precio))
                if not campos:
                    raise ValueError("Debe ingresar al menos un campo para modificar")

                datos.append(pid)
                query = f"UPDATE producto SET {', '.join(campos)} WHERE id_producto = %s"
                cursor.execute(query, tuple(datos))
                conn.commit()
                sg.popup("Producto actualizado correctamente")
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error: {e}")

    window.close()

def create_eliminar_producto_window(cursor, conn):
    cursor.execute("SELECT * FROM producto")
    
    if cursor.fetchone() is None:
        raise Exception
        return

    layout = [
        [sg.Text("Eliminar producto", font="Any 12 bold")],
        [sg.Text("Ingrese ID del producto a eliminar:"), sg.Input(key="ID")],
        [sg.Button("Eliminar"), sg.Button("Volver")]
    ]

    window = sg.Window("Eliminar producto", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Volver"):
            break

        if event == "Eliminar":
            try:
                pid = int(values["ID"])

                cursor.execute("SELECT 1 FROM producto WHERE id_producto = %s AND borrado = FALSE", (pid,))
                if cursor.fetchone() is None:
                    sg.popup_error("El producto no existe")
                    continue

                cursor.execute("UPDATE producto SET borrado = TRUE WHERE id_producto = %s", (pid,))
                conn.commit()
                sg.popup("Producto eliminado correctamente")
            except Exception as e:
                conn.rollback()
                sg.popup_error(f"Error: {e}")

    window.close()
