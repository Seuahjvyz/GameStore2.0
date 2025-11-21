--
-- PostgreSQL database dump
--

\restrict 1N0SQZvPTGvKbdlCMrHJMtgu1aQkDUTMT4W2u57kqqfZX1OLnFAqgItV9KNl7J2

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: carrito; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.carrito (
    id_carrito integer NOT NULL,
    usuario_id integer,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    activo boolean DEFAULT true
);


--
-- Name: carrito_id_carrito_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.carrito_id_carrito_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: carrito_id_carrito_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.carrito_id_carrito_seq OWNED BY public.carrito.id_carrito;


--
-- Name: carrito_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.carrito_items (
    id_item integer NOT NULL,
    carrito_id integer,
    producto_id integer,
    cantidad integer DEFAULT 1,
    precio_unitario numeric(10,2),
    fecha_agregado timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: carrito_items_id_item_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.carrito_items_id_item_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: carrito_items_id_item_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.carrito_items_id_item_seq OWNED BY public.carrito_items.id_item;


--
-- Name: categorias; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categorias (
    id_categoria integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text
);


--
-- Name: categorias_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categorias_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categorias_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categorias_id_categoria_seq OWNED BY public.categorias.id_categoria;


--
-- Name: pedido_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pedido_items (
    id_item integer NOT NULL,
    pedido_id integer,
    producto_id integer,
    cantidad integer,
    precio_unitario numeric(10,2)
);


--
-- Name: pedido_items_id_item_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pedido_items_id_item_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pedido_items_id_item_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pedido_items_id_item_seq OWNED BY public.pedido_items.id_item;


--
-- Name: pedidos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pedidos (
    id_pedido integer NOT NULL,
    usuario_id integer,
    fecha_pedido timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total numeric(10,2),
    estado character varying(50) DEFAULT 'pendiente'::character varying,
    direccion_envio text
);


--
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pedidos_id_pedido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pedidos_id_pedido_seq OWNED BY public.pedidos.id_pedido;


--
-- Name: productos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.productos (
    id_producto integer NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion text,
    precio numeric(10,2) NOT NULL,
    stock integer DEFAULT 0,
    imagen character varying(500),
    categoria_id integer,
    activo boolean DEFAULT true,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: productos_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.productos_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: productos_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.productos_id_producto_seq OWNED BY public.productos.id_producto;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id_rol integer NOT NULL,
    nombre character varying(30)
);


--
-- Name: roles_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_id_rol_seq OWNED BY public.roles.id_rol;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    nombre character varying(50),
    correo character varying(100) NOT NULL,
    nombre_usuario character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso timestamp without time zone,
    telefono character varying(15),
    rol_id integer NOT NULL
);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_usuario_seq OWNED BY public.usuarios.id_usuario;


--
-- Name: carrito id_carrito; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito ALTER COLUMN id_carrito SET DEFAULT nextval('public.carrito_id_carrito_seq'::regclass);


--
-- Name: carrito_items id_item; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito_items ALTER COLUMN id_item SET DEFAULT nextval('public.carrito_items_id_item_seq'::regclass);


--
-- Name: categorias id_categoria; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categorias ALTER COLUMN id_categoria SET DEFAULT nextval('public.categorias_id_categoria_seq'::regclass);


--
-- Name: pedido_items id_item; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedido_items ALTER COLUMN id_item SET DEFAULT nextval('public.pedido_items_id_item_seq'::regclass);


--
-- Name: pedidos id_pedido; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedidos ALTER COLUMN id_pedido SET DEFAULT nextval('public.pedidos_id_pedido_seq'::regclass);


--
-- Name: productos id_producto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.productos ALTER COLUMN id_producto SET DEFAULT nextval('public.productos_id_producto_seq'::regclass);


--
-- Name: roles id_rol; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN id_rol SET DEFAULT nextval('public.roles_id_rol_seq'::regclass);


--
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_id_usuario_seq'::regclass);


--
-- Data for Name: carrito; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.carrito (id_carrito, usuario_id, fecha_creacion, activo) FROM stdin;
1	4	2025-11-20 19:36:23.661371	t
\.


--
-- Data for Name: carrito_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.carrito_items (id_item, carrito_id, producto_id, cantidad, precio_unitario, fecha_agregado) FROM stdin;
1	1	1	10	8799.00	2025-11-20 19:36:23.718335
2	1	2	1	17755.99	2025-11-20 20:04:53.251013
\.


--
-- Data for Name: categorias; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categorias (id_categoria, nombre, descripcion) FROM stdin;
1	Consolas	Consolas de videojuegos
2	Juegos	Videojuegos físicos y digitales
3	Controles	Controles y mandos
4	Accesorios	Accesorios gaming
\.


--
-- Data for Name: pedido_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pedido_items (id_item, pedido_id, producto_id, cantidad, precio_unitario) FROM stdin;
\.


--
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pedidos (id_pedido, usuario_id, fecha_pedido, total, estado, direccion_envio) FROM stdin;
\.


--
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.productos (id_producto, nombre, descripcion, precio, stock, imagen, categoria_id, activo, fecha_creacion) FROM stdin;
1	Nintendo Switch 2	Consola Nintendo Switch 2 con 32GB	8799.00	10	/static/img/Nintendo_Switch_2.jpeg	1	t	2025-11-20 12:07:12.273763
2	PlayStation 5 Pro	Consola PlayStation 5 Pro 1TB	17755.99	5	/static/img/PlayStation_5_pro.png	1	t	2025-11-20 12:07:12.273763
3	Control Xbox Inalámbrico White	Control Xbox Series X/S color blanco	1496.99	20	/static/img/Imagenes/controlxboxwhite.png	3	t	2025-11-20 12:07:12.273763
4	Audífonos Gamer	Audífonos gaming profesionales 7.1	760.00	15	/static/img/Audifonos_Gamer.jpg	4	t	2025-11-20 12:07:12.273763
5	FC26	Control inalámbrico FC26	1399.00	8	/static/img/FC26.jpeg	3	t	2025-11-20 12:07:12.273763
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles (id_rol, nombre) FROM stdin;
1	Administrador
2	Cliente
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id_usuario, nombre, correo, nombre_usuario, password, fecha_registro, ultimo_acceso, telefono, rol_id) FROM stdin;
1	Amron	amor@gmail.com	Amron08	Amorcito20	2025-11-17 22:42:40.71055	\N	1234567890	1
4	\N	normajimenezmartinez04@gmail.com	normajm	pbkdf2:sha256:600000$zndoArKOTrxqRBsg$4e0389687c83ed929d57da4253cf26a7c9b4c7355257a59374a3995edc5cf84d	2025-11-18 17:26:22.779887	\N	\N	2
5	\N	admin@farmacia.com	normajmc	pbkdf2:sha256:600000$WkPD5rqpKJ5onuYb$1a420b5262362204b51ac6477bec1bc997f8968404db305af6ffe72633d06146	2025-11-18 17:29:42.373709	\N	\N	2
6	\N	normajimenezmartinez09@gmail.com	normajmcc	pbkdf2:sha256:600000$zLD0MxFDrl9hb1x5$ef4ffefe9e6cd6abf07f60beecbe3e0ce44aedbc1d8e142d038cea7c78f8fe04	2025-11-18 17:34:05.885681	\N	\N	2
7	\N	q@gmail.com	123122	pbkdf2:sha256:600000$LdXUQq48XpMGK340$d061a0ca0a30439a0396c2bb015fbe8f7f29a6aedbd423aa2f2d6eec33df3b14	2025-11-18 18:24:00.424661	\N	\N	2
8	\N	dzgarcia@gmail.com	Diego_r	pbkdf2:sha256:600000$iKxgDjFT3LiN6uw8$b668fbed22a03cfaed539e9a46e06aac10fbf4b836e4845003848a954c55ad6f	2025-11-18 18:50:37.144424	\N	\N	2
\.


--
-- Name: carrito_id_carrito_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.carrito_id_carrito_seq', 1, true);


--
-- Name: carrito_items_id_item_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.carrito_items_id_item_seq', 2, true);


--
-- Name: categorias_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categorias_id_categoria_seq', 4, true);


--
-- Name: pedido_items_id_item_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pedido_items_id_item_seq', 1, false);


--
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pedidos_id_pedido_seq', 1, false);


--
-- Name: productos_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.productos_id_producto_seq', 5, true);


--
-- Name: roles_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_id_rol_seq', 2, true);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 8, true);


--
-- Name: carrito_items carrito_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito_items
    ADD CONSTRAINT carrito_items_pkey PRIMARY KEY (id_item);


--
-- Name: carrito carrito_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT carrito_pkey PRIMARY KEY (id_carrito);


--
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id_categoria);


--
-- Name: pedido_items pedido_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedido_items
    ADD CONSTRAINT pedido_items_pkey PRIMARY KEY (id_item);


--
-- Name: pedidos pedidos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_pkey PRIMARY KEY (id_pedido);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id_producto);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- Name: usuarios usuarios_nombre_usuario_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_nombre_usuario_key UNIQUE (nombre_usuario);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: carrito_items carrito_items_carrito_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito_items
    ADD CONSTRAINT carrito_items_carrito_id_fkey FOREIGN KEY (carrito_id) REFERENCES public.carrito(id_carrito);


--
-- Name: carrito_items carrito_items_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito_items
    ADD CONSTRAINT carrito_items_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id_producto);


--
-- Name: carrito carrito_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT carrito_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id_usuario);


--
-- Name: pedido_items pedido_items_pedido_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedido_items
    ADD CONSTRAINT pedido_items_pedido_id_fkey FOREIGN KEY (pedido_id) REFERENCES public.pedidos(id_pedido);


--
-- Name: pedido_items pedido_items_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedido_items
    ADD CONSTRAINT pedido_items_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id_producto);


--
-- Name: pedidos pedidos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id_usuario);


--
-- Name: productos productos_categoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categorias(id_categoria);


--
-- Name: usuarios usuarios_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id_rol);


--
-- PostgreSQL database dump complete
--

\unrestrict 1N0SQZvPTGvKbdlCMrHJMtgu1aQkDUTMT4W2u57kqqfZX1OLnFAqgItV9KNl7J2

