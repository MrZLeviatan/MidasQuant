<h1 align="center">

_MidasQuant - Base de Datos_

</h1>

Este módulo contiene la definición, configuración e inicialización de la capa de persistencia del sistema **MidasQuant**.

Su propósito es gestionar el almacenamiento estructurado de los datos financieros procesados, garantizando:

- Integridad de la información
- Consistencia entre entidades
- Soporte para análisis algorítmico
- Reproducibilidad del dataset

El diseño está orientado a trabajar en dos entornos:

- **Desarrollo local:** SQLite
- **Producción:** PostgreSQL

<br>

## Tabla de Contenido

- [Tabla de Contenido](#tabla-de-contenido)
- [Estructura del Módulo](#estructura-del-módulo)
  - [1. connection.py](#1-connectionpy)
  - [2. models.py](#2-modelspy)
  - [3. init\_db.py](#3-init_dbpy)
- [Modelo de Datos](#modelo-de-datos)
- [Modelo Entidad-Relación (ERD)](#modelo-entidad-relación-erd)
  - [Relaciones](#relaciones)
- [Consideraciones de Diseñó](#consideraciones-de-diseñó)
- [Inicialización de la Base de Datos](#inicialización-de-la-base-de-datos)

---

## Estructura del Módulo

El módulo de base de datos está compuesto por los siguientes archivos:

### 1. [connection.py](./connection.py)

Gestiona la conexión a la base de datos.

**Responsabilidades:**

- Configurar la conexión a **SQLite** en entorno local
- Configurar la conexión a **PostgreSQL** en producción
- Centralizar la lógica de acceso a datos
- Permitir escalabilidad y cambio de motor sin afectar el resto del sistema

<br>

### 2. [models.py](./models.py)

Define las entidades del sistema y sus relaciones.

**Responsabilidades:**

- Modelar las tablas de la base de datos
- Definir claves primarias y foráneas
- Representar relaciones entre entidades
- Mantener coherencia con el modelo lógico del proyecto

<br>

### 3. [init_db.py](./init_db.py)

Inicializa la base de datos.

**Responsabilidades:**

- Crear las tablas definidas en `models.py`
- Preparar la estructura base del sistema
- Permitir la creación reproducible del esquema desde cero

<br>

---

## Modelo de Datos

A continuación se describen las principales entidades del sistema.

<br>

1. `Activo` (assets)
   Representa un activo financiero individual (acción o ETF).

| Atributo  | Tipo          | ¿Por qué existe?                                  |
| --------- | ------------- | ------------------------------------------------- |
| id_activo | Entero (PK)   | Identificador interno eficiente para relaciones   |
| ticker    | Texto (único) | Identidad real del activo en el mercado           |
| nombre    | Texto         | Nombre descriptivo (opcional, mejora legibilidad) |
| tipo      | Texto         | Clasificación (STOCK, ETF)                        |

<br>

2. `Portafolio`
   Una configuración de activos definida por el usuario.

| Atributo       | Tipo        | ¿Por qué existe?                   |
| -------------- | ----------- | ---------------------------------- |
| id_portafolio  | Entero (PK) | Identificador único                |
| nombre         | Texto       | Permite distinguir configuraciones |
| fecha_creacion | DataTime    | Control temporal y trazabilidad    |

<br>

3. `Portafolio_Activo`
   Tabla intermedia que representa la relación entre portafolios y activos.

| Atributo             | Tipo        | ¿Por qué existe?          |
| -------------------- | ----------- | ------------------------- |
| id_portafolio_activo | Entero (PK) | Identificador único       |
| id_portafolio        | Entero (FK) | Relación con `portafolio` |
| id_activo            | Entero (FK) | Relación con `activo`     |

<br>

4. `Serie_Temporal`
   Almacena la información histórica de precios de cada activo.

| Atributo  | Tipo        | ¿Por qué existe?       |
| --------- | ----------- | ---------------------- |
| id_serie  | Entero (PK) | Identificador único    |
| id_activo | Entero (FK) | Relación con el activo |
| fecha     | Fecha       | Referencia temporal    |
| open      | Decimal     | Precio de apertura     |
| high      | Decimal     | Precio máximo          |
| low       | Decimal     | Precio mínimo          |
| close     | Decimal     | Precio de cierre       |
| volumen   | Entero      | Volumen de negociación |

<br>

5. `Configuración_Analisis`
   Almacena los parámetros de ejecución de analisis a Portafolios

| Atributo         | Tipo        | ¿Por qué existe?                      |
| ---------------- | ----------- | ------------------------------------- |
| id_configuracion | Entero (PK) | Identificador único                   |
| id_portafolio    | Entero (FK) | Relación con el portafolio a analizar |
| fecha_inicio     | Fecha       | Límite inferior del análisis          |
| fecha_fin        | Fecha       | Límite superior del análisis          |

<br>

---

## Modelo Entidad-Relación (ERD)

El siguiente diagrama representa la estructura lógica de la base de datos, incluyendo entidades, atributos y relaciones.

<p align="left">
    <img src="https://res.cloudinary.com/dehltwwbu/image/upload/v1774156048/Modelo_Entidad-Relaci%C3%B3n_ERD_kggjhm.jpg" alt="Icono de Git" />
</p>

### Relaciones

- Un **activo** tiene muchos registros en serie_temporal (1:N)
- Un **portafolio** contiene múltiples activos (N:M)
- Un **activo** puede pertenecer a múltiples portafolios (N:M)
- Un **portafolio** puede tener múltiples configuraciones de análisis (1:N)

<br>

---

## Consideraciones de Diseñó

- Se utiliza un **ID interno** para optimizar relaciones y consultas
- El campo 'ticker' es único para evitar duplicidad de activos
- La separación entre `activos` y `series_temporales` permite:
  - Escalabilidad
  - Consultas eficientes
  - Normalización del modelo
- La estructura soporta análisis de series de tiempo sin redundancia
- La estructura soporta un histórico suficientemente amplio para análisis significativos.

<br>

---

## Inicialización de la Base de Datos

La base de datos se inicializa al ejecutar el comando local:

```bash
streamlit run app/main.py
```

Pero si se desea creara de forma manual, se puede ejecutar el comando:

```bash
python database/init_db.py
```

Este proceso:

- Crea todas las tablas necesarias (De forma local)
- Define relaciones entre entidades
