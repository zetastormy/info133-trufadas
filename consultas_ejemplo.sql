CREATE TABLE "vendedores" (
  "id_vendedor" integer PRIMARY KEY,
  "nombre" varchar,
  "correo" varchar
);

CREATE TABLE "hechos_ventas" (
  "id_venta" integer PRIMARY KEY,
  "monto_total" integer,
  "id_cliente" integer,
  "fecha" timestamp,
  "id_vendedor" integer,
  "medio_pago" varchar,
  "id_producto" integer,
  "cantidad" integer
);

CREATE TABLE "clientes" (
  "id_cliente" integer PRIMARY KEY,
  "nombre" varchar,
  "genero" varchar
);

CREATE TABLE "productos" (
  "id_producto" integer PRIMARY KEY,
  "precio" integer,
  "nonbre" varchar
);

CREATE TABLE "hechos_compras" (
  "id_gasto" integer PRIMARY KEY,
  "id_insumo" integer,
  "cantidad" integer,
  "fecha" timestamp
);

CREATE TABLE "insumos" (
  "id_insumo" integer PRIMARY KEY,
  "nombre" varchar,
  "precio" integer,
  "medida" varchar
);

ALTER TABLE "vendedores" ADD FOREIGN KEY ("id_vendedor") REFERENCES "hechos_ventas" ("id_vendedor");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("id_cliente") REFERENCES "clientes" ("id_cliente");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("id_producto") REFERENCES "productos" ("id_producto");

ALTER TABLE "insumos" ADD FOREIGN KEY ("id_insumo") REFERENCES "hechos_compras" ("id_insumo");

/* Obtener el producto más vendido por cantidad en los últimos 7 días. */
SELECT p.nombre AS producto, SUM(pv.cantidad) AS total_vendido 
FROM productos p 
JOIN productos_vendidos pv ON p.id_producto = pv.id_producto 
JOIN hechos_ventas v ON v.id_venta = pv.id_venta 
WHERE v.fecha >= CURRENT_DATE - INTERVAL '7 days' 
GROUP BY p.nombre 
ORDER BY total_vendido DESC LIMIT 1;

/* Obtener el cliente que compró más trufas sabor coñac. */
SELECT clientes.nombre, COUNT(*) AS cantidad
FROM clientes
JOIN hechos_ventas ON clientes.id_cliente = hechos_ventas.id_cliente
JOIN productos_vendidos ON hechos_ventas.id_venta = productos_vendidos.id_venta
JOIN productos ON productos_vendidos.id_producto = productos.id_producto
WHERE productos.id_producto = 2
GROUP BY clientes.nombre
ORDER BY cantidad DESC LIMIT 1;

/* Clientes que más han comprado (por monto total). */
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
