## ¿Cómo utilizar el programa?

Primero debe tener creada una base de datos vacía, la cual ingresará junto con sus datos en `analisis.py` en `DB_CONFIG`. Para generar las tablas de la base de datos, referirse al archivo `tables.sql`. Posteriormente para rellenar la base de datos recién creada, puede ejecutar el script `generar_datos.py`, el cual creará datos en un lapso de 4 años a partir de la fecha de hoy hacia atrás. Genera 50 clientes y 4 vendedores, realizando un total de 500 ventas y 30 reposiciones de insumos. Además, se insertarán los datos de productos e insumos que son realmente usados en el negocio en la realidad.

Finalmente, para realizar el análisis de los datos ejecute el script `analisis.py` de la siguiente manera:

```sh
python analisis.py <año>
```

Este script creará los 6 gráficos siguientes:

- Las compras por insumo
- Los 10 días con más ventas del año
- Proporción de métodos de pago usados durante el año
- Las ventas por cada mes del año
- Las ventas por producto
- Las ventas por vendedor

## Especificación base de datos 

Se requiere el diseño de una base de datos para registrar y gestionar las operaciones de ventas y compras de insumos en un negocio emergente de repostería. Este sistema permitirá llevar un control detallado de los productos comercializados, así como de los materiales necesarios para su elaboración, facilitando así la toma de decisiones basada en datos.

Actualmente, el negocio ofrece los siguientes productos:

  - Trufas (Sabores: coñac, menta, ron y chocolate).
  - Cocadas.
  - Pan con chicharrón.

El objetivo principal de la base de datos es centralizar la información de las transacciones realizadas, tanto de ingreso (ventas de productos) como de egreso (compras de insumos), para posteriormente realizar análisis que permitan evaluar la rentabilidad, optimizar los procesos de producción, y proyectar la demanda. Para ello, se debe contar con la siguiente información:

  - Clientes: Personas que han realizado una o más compras. Su inclusión en el sistema permitirá analizar el comportamiento de compra, establecer relaciones y ofrecer un mejor servicio. Se guardarán sus nombres y géneros.
  - Vendedores: Encargados de efectuar las ventas. Es importante llevar un control de quién realizó cada transacción para evaluar el rendimiento individual y asignar responsabilidades. Se guardarán sus nombres y correos.
  - Productos: Elementos disponibles para la venta. Se guardarán sus nombres y precios. 
  - Insumos: Materiales necesarios para la preparación de los productos. Su seguimiento permitirá controlar el inventario, planificar futuras adquisiciones y calcular los costos asociados a la producción. Se guardarán sus nombres, precios y unidades de medida (1kg, 1000gr, etc).


Esta información permitirá también gestionar las ventas, considerando los siguientes aspectos:
  - ID de la venta: Identificador único que permite agrupar todos los productos comprados en una misma transacción.
  - Monto total: Suma total que el cliente pagó por todos los productos adquiridos.
  - Cliente asociado: Persona que realizó la compra.
  - Fecha y hora: Momento exacto en que se concretó la venta.
  - Vendedor asociado: Empleado responsable de la transacción.
  - Medio de pago: Forma en que se efectuó el pago (efectivo, débito o transferencia).
  - Producto adquirido: Producto incluido en la compra.
  - Cantidad: Número de unidades compradas de dicho producto.

Adicionalmente, será necesario llevar el control de la reposición de insumos, para lo cual se requiere:
  - Insumo asociado: Insumo específico que está siendo adquirido.
  - Cantidad: Número de unidades del insumo comprado.
  - Fecha de compra: Día en que se realizó la adquisición del insumo.
