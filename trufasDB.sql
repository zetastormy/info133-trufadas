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
