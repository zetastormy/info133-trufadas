import psycopg2
import matplotlib.pyplot as plt
from datetime import datetime

def analisis_ventas_por_mes(cursor, anio):
    cursor.execute("""
        SELECT DATE_TRUNC('month', fecha) AS mes, SUM(monto_total)
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY mes ORDER BY mes
    """, (anio,))
    datos = cursor.fetchall()
    meses = [m[0].strftime('%b') for m in datos]
    totales = [m[1] for m in datos]

    fig = plt.figure()
    plt.plot(meses, totales, color='red', figure=fig)
    plt.title(f'Ventas por mes - {anio}', figure=fig)
    plt.xlabel('Mes', figure=fig)
    plt.ylabel('Monto total ($)', figure=fig)
    plt.tight_layout()

    return fig

def analisis_ventas_por_producto(cursor, anio):
    cursor.execute("""
        SELECT p.nombre, SUM(hv.cantidad)
        FROM hechos_ventas hv
        JOIN productos p ON hv.id_producto = p.id_producto
        WHERE EXTRACT(YEAR FROM hv.fecha) = %s
        GROUP BY p.nombre ORDER BY SUM(hv.cantidad) DESC
    """, (anio,))
    datos = cursor.fetchall()
    productos = [d[0] for d in datos]
    cantidades = [d[1] for d in datos]

    fig = plt.figure(figsize=(10,5))
    plt.barh(productos, cantidades, color='orange', figure=fig)
    plt.title(f'Ventas por producto - {anio}', figure=fig)
    plt.xlabel('Cantidad vendida (unidad)', figure=fig)
    plt.ylabel('Producto', figure=fig)
    plt.tight_layout()

    return fig

def analisis_monto_total_recaudado_por_vendedor(cursor, anio):
    cursor.execute("""
        SELECT v.nombre, SUM(hv.monto_total)
        FROM hechos_ventas hv
        JOIN vendedores v ON hv.id_vendedor = v.id_vendedor
        WHERE EXTRACT(YEAR FROM hv.fecha) = %s
        GROUP BY v.nombre ORDER BY SUM(hv.monto_total) DESC
    """, (anio,))
    datos = cursor.fetchall()
    nombres = [d[0] for d in datos]
    montos = [d[1] for d in datos]

    fig = plt.figure()
    plt.bar(nombres, montos, color='green', figure=fig)
    plt.title(f'Ventas por vendedor - {anio}', figure=fig)
    plt.xlabel('Vendedor', figure=fig)
    plt.ylabel('Monto total ($)', figure=fig)
    plt.xticks(rotation=45, figure=fig)
    plt.tight_layout()

    return fig

def analisis_compras_por_insumo(cursor, anio):
    cursor.execute("""
        SELECT i.nombre, SUM(hc.cantidad)
        FROM hechos_compras hc
        JOIN insumos i ON hc.id_insumo = i.id_insumo
        WHERE EXTRACT(YEAR FROM hc.fecha) = %s
        GROUP BY i.nombre ORDER BY SUM(hc.cantidad) DESC
    """, (anio,))
    datos = cursor.fetchall()
    insumos = [d[0] for d in datos]
    cantidades = [d[1] for d in datos]

    fig = plt.figure(figsize=(10,5))
    plt.barh(insumos, cantidades, color='purple', figure=fig)
    plt.title(f'Compras por insumo - {anio}', figure=fig)
    plt.xlabel('Cantidad comprada (unidad)', figure=fig)
    plt.ylabel('Insumo', figure=fig)
    plt.tight_layout()

    return fig

def analisis_porcentaje_metodos_de_pago(cursor, anio):
    cursor.execute("""
        SELECT medio_pago, COUNT(*)
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY medio_pago
    """, (anio,))
    datos = cursor.fetchall()
    medios = [d[0] for d in datos]
    cantidad = [d[1] for d in datos]

    fig = plt.figure()
    plt.pie(cantidad, labels=medios, autopct='%1.1f%%', startangle=140)
    plt.title(f'Métodos de pago - {anio}', figure=fig)
    plt.tight_layout()

    return fig

def analisis_dias_con_mas_ventas(cursor, anio):
    cursor.execute("""
        SELECT DATE(fecha) AS dia, COUNT(DISTINCT id_venta) AS total_ventas
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY dia ORDER BY total_ventas DESC
        LIMIT 10
    """, (anio,))
    datos = cursor.fetchall()
    dias = [d[0].strftime('%Y-%m-%d') for d in datos]
    cantidades = [d[1] for d in datos]

    fig = plt.figure(figsize=(10, 5))
    plt.barh(dias[::-1], cantidades[::-1], color='teal', figure=fig) 
    plt.title(f'Días con más ventas - Top 10 - {anio}', figure=fig)
    plt.xlabel('Cantidad de ventas', figure=fig)
    plt.ylabel('Fecha', figure=fig)
    plt.tight_layout()

    return fig
