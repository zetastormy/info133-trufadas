from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import FreeSimpleGUI as sg
import matplotlib
import os
import psycopg2
import graficos as g

sg.theme('SandyBeach')
matplotlib.use('TkAgg')

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'trufadas',
    'user': 'zetastormy',
    'password': ''
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def draw_figure(canvas, figure):
    for widget in canvas.winfo_children():
        widget.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

def create_main_window():
    tab_mas_ventas = [[sg.Canvas(key='GRAFICO_MAS_VENTAS')]]
    tab_compras_insumo = [[sg.Canvas(key='GRAFICO_COMPRAS_INSUMO')]]
    tab_ventas_vendedor = [[sg.Canvas(key='GRAFICO_VENTAS_VENDEDOR')]]
    tab_metodos_pago = [[sg.Canvas(key='GRAFICO_METODOS_PAGO')]]
    tab_ventas_mes = [[sg.Canvas(key='GRAFICO_VENTAS_MES')]]
    tab_ventas_producto = [[sg.Canvas(key='GRAFICO_VENTAS_PRODUCTO')]]

    columna1 = [[sg.Text("Seleccione año:", font="Any 10 bold"), sg.Combo(values=['2023', '2024', '2025'], readonly=True, key='ANIO', enable_events=True), sg.Button("Cargar gráficos")]]
    columna2 = [[sg.Button("Salir")]]

    layout = [
            [sg.TabGroup([[
                sg.Tab("Días con más ventas", tab_mas_ventas), 
                sg.Tab("Compras por insumo", tab_compras_insumo),
                sg.Tab("Ventas por vendedor", tab_ventas_vendedor),
                sg.Tab("Métodos de pago", tab_metodos_pago),
                sg.Tab("Ventas por mes", tab_ventas_mes),
                sg.Tab("Ventas por producto", tab_ventas_producto)]], key='GRAFICOS', visible=False)],
            [sg.Column(columna1, element_justification='l', expand_x=True), sg.Column(columna2, element_justification='r', expand_x=True)]
            ]

    window = sg.Window("Gráficos de análisis", layout)

    return window

def main():
    mainWindow = create_main_window()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        while True:
            event, values = mainWindow.read()

            if event == 'Cargar gráficos':
                if values['ANIO'] == '':
                    sg.popup_error(f"Debe seleccionar un año.")
                    continue

                year = values['ANIO']
                matplotlib.pyplot.close('all')

                draw_figure(mainWindow['GRAFICO_MAS_VENTAS'].TKCanvas, g.analisis_dias_con_mas_ventas(cursor, year))
                draw_figure(mainWindow['GRAFICO_COMPRAS_INSUMO'].TKCanvas, g.analisis_compras_por_insumo(cursor, year))
                draw_figure(mainWindow['GRAFICO_VENTAS_VENDEDOR'].TKCanvas, g.analisis_monto_total_recaudado_por_vendedor(cursor, year))
                draw_figure(mainWindow['GRAFICO_METODOS_PAGO'].TKCanvas, g.analisis_porcentaje_metodos_de_pago(cursor, year))
                draw_figure(mainWindow['GRAFICO_VENTAS_MES'].TKCanvas, g.analisis_ventas_por_mes(cursor, year))
                draw_figure(mainWindow['GRAFICO_VENTAS_PRODUCTO'].TKCanvas, g.analisis_ventas_por_producto(cursor, year))          

                mainWindow['GRAFICOS'].update(visible=True)

            if event in (sg.WINDOW_CLOSED, "Salir"):
                break

    except Exception as e:
        print("Error:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()
    
    mainWindow.close()

if __name__ == "__main__":
    main()