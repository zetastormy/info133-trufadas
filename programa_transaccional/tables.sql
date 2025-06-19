CREATE TABLE "vendedor" (
  "id_vendedor" SERIAL PRIMARY KEY,
  "nombre" VARCHAR,
  "correo" VARCHAR
);

CREATE TABLE "producto" (
  "id_producto" SERIAL PRIMARY KEY,
  "nombre" VARCHAR,
  "precio" INTEGER,
  "borrado" BOOLEAN DEFAULT FALSE
);

CREATE TABLE "cliente" (
  "id_cliente" SERIAL PRIMARY KEY,
  "nombre" VARCHAR,
  "genero" VARCHAR
);

CREATE TABLE "insumo" (
  "id_insumo" serial PRIMARY KEY,
  "nombre" VARCHAR,
  "precio" INTEGER,
  "unidad_medida" VARCHAR
);

CREATE TABLE "reposicion_insumo" (
  "id_reposicion" SERIAL PRIMARY KEY,
  "id_insumo" INTEGER,
  "fecha" TIMESTAMP,
  "cantidad" INTEGER,
  CONSTRAINT fk_insumo FOREIGN KEY (id_insumo) REFERENCES insumo(id_insumo)
);

CREATE TABLE "venta" (
	"id_venta" SERIAL PRIMARY KEY,
	"monto" INTEGER,
	"medio_pago" VARCHAR,
	"fecha" TIMESTAMP,
	"id_vendedor" INTEGER,
	"id_cliente" INTEGER,
	CONSTRAINT fk_vendedor FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor),
	CONSTRAINT fk_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) 
);

CREATE TABLE "vender" (
	"id_venta" INTEGER,
	"id_producto" INTEGER,
	"cantidad" INTEGER,
	CONSTRAINT fk_venta FOREIGN KEY (id_venta) REFERENCES venta(id_venta),
	CONSTRAINT fk_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
	PRIMARY KEY (id_venta, id_producto)
);
