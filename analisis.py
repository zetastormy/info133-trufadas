import psycopg2
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': '',
    'user': '',
    'password': ''
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def analisis_ventas_por_mes(cursor, año):
    cursor.execute("""
        SELECT DATE_TRUNC('month', fecha) AS mes, SUM(monto_total)
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY mes ORDER BY mes
    """, (año,))
    datos = cursor.fetchall()
    meses = [m[0].strftime('%b') for m in datos]
    totales = [m[1] for m in datos]

    plt.figure()
    plt.plot(meses, totales, color='red')
    plt.title(f'Ventas por mes - {año}')
    plt.xlabel('Mes')
    plt.ylabel('Monto total')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_ventas_por_mes_{año}.png"))

def analisis_ventas_por_producto(cursor, año):
    cursor.execute("""
        SELECT p.nombre, SUM(hv.cantidad)
        FROM hechos_ventas hv
        JOIN productos p ON hv.id_producto = p.id_producto
        WHERE EXTRACT(YEAR FROM hv.fecha) = %s
        GROUP BY p.nombre ORDER BY SUM(hv.cantidad) DESC
    """, (año,))
    datos = cursor.fetchall()
    productos = [d[0] for d in datos]
    cantidades = [d[1] for d in datos]

    plt.figure(figsize=(10,5))
    plt.barh(productos, cantidades, color='orange')
    plt.title(f'Ventas por producto - {año}')
    plt.xlabel('Cantidad vendida')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_ventas_por_producto_{año}.png"))

def analisis_monto_total_recaudado_por_vendedor(cursor, año):
    cursor.execute("""
        SELECT v.nombre, SUM(hv.monto_total)
        FROM hechos_ventas hv
        JOIN vendedores v ON hv.id_vendedor = v.id_vendedor
        WHERE EXTRACT(YEAR FROM hv.fecha) = %s
        GROUP BY v.nombre ORDER BY SUM(hv.monto_total) DESC
    """, (año,))
    datos = cursor.fetchall()
    nombres = [d[0] for d in datos]
    montos = [d[1] for d in datos]

    plt.figure()
    plt.bar(nombres, montos, color='green')
    plt.title(f'Ventas por vendedor - {año}')
    plt.ylabel('Monto total')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_monto_total_recaudado_por_vendedor_{año}.png"))

def analisis_compras_por_insumo(cursor, año):
    cursor.execute("""
        SELECT i.nombre, SUM(hc.cantidad)
        FROM hechos_compras hc
        JOIN insumos i ON hc.id_insumo = i.id_insumo
        WHERE EXTRACT(YEAR FROM hc.fecha) = %s
        GROUP BY i.nombre ORDER BY SUM(hc.cantidad) DESC
    """, (año,))
    datos = cursor.fetchall()
    insumos = [d[0] for d in datos]
    cantidades = [d[1] for d in datos]

    plt.figure(figsize=(10,5))
    plt.barh(insumos, cantidades, color='purple')
    plt.title(f'Compras por insumo - {año}')
    plt.xlabel('Cantidad comprada')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_compras_por_insumo_{año}.png"))

def analisis_porcentaje_metodos_de_pago(cursor, año):
    cursor.execute("""
        SELECT medio_pago, COUNT(*)
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY medio_pago
    """, (año,))
    datos = cursor.fetchall()
    medios = [d[0] for d in datos]
    cantidad = [d[1] for d in datos]

    plt.figure()
    plt.pie(cantidad, labels=medios, autopct='%1.1f%%', startangle=140)
    plt.title(f'Métodos de pago - {año}')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_porcentaje_metodos_de_pago_{año}.png"))

def analisis_dias_con_mas_ventas(cursor, año):
    cursor.execute("""
        SELECT DATE(fecha) AS dia, COUNT(DISTINCT id_venta) AS total_ventas
        FROM hechos_ventas
        WHERE EXTRACT(YEAR FROM fecha) = %s
        GROUP BY dia ORDER BY total_ventas DESC
        LIMIT 10
    """, (año,))
    datos = cursor.fetchall()
    dias = [d[0].strftime('%Y-%m-%d') for d in datos]
    cantidades = [d[1] for d in datos]

    plt.figure(figsize=(10, 5))
    plt.barh(dias[::-1], cantidades[::-1], color='teal') 
    plt.title(f'Días con más ventas - Top 10 - {año}')
    plt.xlabel('Cantidad de ventas')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, f"graficos/analisis_10_dias_con_mas_ventas_{año}.png"))

def main():
    if len(sys.argv) != 2:
        print("Uso: python graficos.py <año>")
        return

    año = int(sys.argv[1])

    if not os.path.exists(os.path.join(BASE_DIR, "graficos")):
        os.mkdir(os.path.join(BASE_DIR, "graficos"))

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        analisis_ventas_por_mes(cursor, año)
        analisis_ventas_por_producto(cursor, año)
        analisis_ventas_por_vendedor(cursor, año)
        analisis_compras_por_insumo(cursor, año)
        analisis_porcentaje_metodos_de_pago(cursor, año)
        analisis_dias_con_mas_ventas(cursor, año)

        print("Gráficos generados correctamente.")

    except Exception as e:
        print("Error:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()
