import os
import psycopg2

TRANSACTIONAL_DB_CONFIG = {
    'host': 'localhost',
    'database': 'trufadas_transaccional',
    'user': 'zetastormy',
    'password': ''
}

ANALYTICS_DB_CONFIG = {
    'host': 'localhost',
    'database': 'trufadas',
    'user': 'zetastormy',
    'password': ''
}

def update_analytics_database():
    try:
        print("[ETL] Conectando a BD...")
        transactional_conn = psycopg2.connect(**TRANSACTIONAL_DB_CONFIG)
        transactional_cursor = transactional_conn.cursor()
        
        analytics_conn = psycopg2.connect(**ANALYTICS_DB_CONFIG)
        analytics_cursor = analytics_conn.cursor()

        print("[ETL] 1")
        # Truncar todas las tablas al mismo tiempo con CASCADE
        analytics_cursor.execute("DELETE FROM hechos_ventas")
        analytics_cursor.execute("DELETE FROM hechos_compras")
        analytics_cursor.execute("DELETE FROM vendedores")
        analytics_cursor.execute("DELETE FROM productos")
        analytics_cursor.execute("DELETE FROM clientes")
        analytics_cursor.execute("DELETE FROM insumos")

        print("[ETL] 2")
        # --- Vendedores ---
        transactional_cursor.execute("SELECT id_vendedor, nombre, correo FROM vendedor")
        for vendedor in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO vendedores (id_vendedor, nombre, correo)
                VALUES (%s, %s, %s)
            """, vendedor)

        print("[ETL] 3")
        # --- Productos ---
        transactional_cursor.execute("SELECT id_producto, nombre, precio FROM producto WHERE borrado = FALSE")
        for producto in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO productos (id_producto, nombre, precio)
                VALUES (%s, %s, %s)
            """, producto)

        print("[ETL] 4")
        # --- Clientes ---
        transactional_cursor.execute("SELECT id_cliente, nombre, genero FROM cliente")
        for cliente in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO clientes (id_cliente, nombre, genero)
                VALUES (%s, %s, %s)
            """, cliente)
        
        print("[ETL] 5")
        # --- Insumos ---
        transactional_cursor.execute("SELECT id_insumo, nombre, precio, unidad_medida FROM insumo")
        for insumo in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO insumos (id_insumo, nombre, precio, medida)
                VALUES (%s, %s, %s, %s)
            """, insumo)

        print("[ETL] 6")
        # --- Hechos ventas ---
        transactional_cursor.execute("""
            SELECT 
                v.id_venta, 
                v.monto, 
                v.id_cliente, 
                v.fecha, 
                v.id_vendedor, 
                v.medio_pago,
                p.id_producto,
                vd.cantidad
            FROM venta v
            JOIN vender vd ON v.id_venta = vd.id_venta
            JOIN producto p ON vd.id_producto = p.id_producto
            WHERE v.borrado = FALSE AND vd.borrado = FALSE AND p.borrado = FALSE
        """)
        for venta in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO hechos_ventas 
                (id_venta, monto_total, id_cliente, fecha, id_vendedor, medio_pago, id_producto, cantidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, venta)

        print("[ETL] 7")
        # --- Hechos compras ---
        transactional_cursor.execute("""
            SELECT id_insumo, cantidad, fecha FROM reposicion_insumo
        """)
        for compra in transactional_cursor.fetchall():
            analytics_cursor.execute("""
                INSERT INTO hechos_compras (id_insumo, cantidad, fecha)
                VALUES (%s, %s, %s)
            """, compra)

        analytics_conn.commit()
        print("Base de datos de análisis actualizada correctamente.")

    except Exception as e:
        print(f"Error al actualizar la base de datos de análisis: {e}")
        analytics_conn.rollback()

    finally:
        transactional_cursor.close()
        transactional_conn.close()
        analytics_cursor.close()
        analytics_conn.close()
