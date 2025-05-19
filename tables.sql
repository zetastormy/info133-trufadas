CREATE TABLE "hechos_ventas" (
  "id" serial PRIMARY KEY,
  "id_venta" integer,
  "monto_total" integer,
  "id_cliente" integer,
  "fecha" timestamp,
  "id_vendedor" integer,
  "medio_pago" varchar,
  "id_producto" integer,
  "cantidad" integer
);

CREATE TABLE "vendedores" (
  "id_vendedor" serial PRIMARY KEY,
  "nombre" varchar,
  "correo" varchar
);

CREATE TABLE "productos" (
  "id_producto" serial PRIMARY KEY,
  "precio" integer,
  "nombre" varchar
);

CREATE TABLE "clientes" (
  "id_cliente" serial PRIMARY KEY,
  "nombre" varchar,
  "genero" varchar
);

CREATE TABLE "hechos_compras" (
  "id_gasto" serial PRIMARY KEY,
  "id_insumo" integer,
  "cantidad" integer,
  "fecha" timestamp
);

CREATE TABLE "insumos" (
  "id_insumo" serial PRIMARY KEY,
  "nombre" varchar,
  "precio" integer,
  "medida" varchar
);

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("id_cliente") REFERENCES "clientes" ("id_cliente");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("id_vendedor") REFERENCES "vendedores" ("id_vendedor");

ALTER TABLE "hechos_ventas" ADD FOREIGN KEY ("id_producto") REFERENCES "productos" ("id_producto");

ALTER TABLE "hechos_compras" ADD FOREIGN KEY ("id_insumo") REFERENCES "insumos" ("id_insumo");
