/* Obtener el producto más vendido por cantidad en el último mes. */
SELECT p.nombre AS producto, SUM(pv.cantidad) AS total_vendido 
FROM productos p 
JOIN productos_vendidos pv ON p.id_producto = pv.id_producto 
JOIN hechos_ventas v ON v.id_venta = pv.id_venta 
WHERE v.fecha >= CURRENT_DATE - INTERVAL '1 month' 
GROUP BY p.nombre 
ORDER BY total_vendido DESC;

/* Obtener el cliente que compró más trufas sabor coñac. */
SELECT clientes.nombre, COUNT(*) AS cantidad
FROM clientes
JOIN hechos_ventas ON clientes.id_cliente = hechos_ventas.id_cliente
JOIN productos_vendidos ON hechos_ventas.id_venta = productos_vendidos.id_venta
JOIN productos ON productos_vendidos.id_producto = productos.id_producto
WHERE productos.id_producto = 2
GROUP BY clientes.nombre
ORDER BY cantidad DESC;

/* Los 5 clientes que más han comprado (por monto total). */
SELECT c.nombre, SUM(hv.monto_total) AS total_gastado 
FROM clientes c JOIN hechos_ventas hv ON c.id_cliente = hv.id_cliente 
GROUP BY c.nombre 
ORDER BY total_gastado DESC LIMIT 5; 

/* Rendimiento de vendedores. */
SELECT vd.nombre, COUNT(hv.id_venta) AS cantidad_ventas, SUM(hv.monto_total) AS total_vendido 
FROM vendedores vd JOIN hechos_ventas hv ON vd.id_vendedor = hv.id_vendedor 
GROUP BY vd.nombre 
ORDER BY total_vendido DESC;

/* Insumos más usados (por cantidad de reposiciones). */
SELECT i.nombre, SUM(ri.cantidad) AS cantidad_repuesta 
FROM insumos i JOIN reposiciones_insumos ri ON i.id_insumo = ri.id_insumo 
GROUP BY i.nombre 
ORDER BY cantidad_repuesta DESC; 
