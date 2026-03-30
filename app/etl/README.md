<h1 align="center">

_MidasQuant - ETL (Extra, Transform, Load)_

</h1>

Este módulo implementa el proceso ETL (Extract, Transform, Load) para el análisis de activos financieros dentro del proyecto **MidasQuant**, encargándose de orquestar la obtención de datos desde múltiples fuentes públicas, aplicar procesos de validación y normalización, y estructurar la información en formatos consistentes para su posterior análisis.

Su objetivo es:

- Extraer datos financieros desde fuentes externas
- Transformarlos en estructuras limpias y consistentes
- Prepararlos para análisis cuantitativo

<br>

## Tabla de Contenido

- [Tabla de Contenido](#tabla-de-contenido)
- [Estructura del Módulo](#estructura-del-módulo)
  - [1. etl/extract](#1-etlextract)
    - [1.1 /asset_metadata_extractor.py](#11-asset_metadata_extractorpy)
    - [1.2 /market_data_extractor.py](#12-market_data_extractorpy)
  - [2. etl/transform](#2-etltransform)
    - [2.1 /time_series_alignment.py](#21-time_series_alignmentpy)
    - [2.2 /quality_audit.py](#22-quality_auditpy)
    - [2.3 data_imputation.py](#23-data_imputationpy)
- [Flujo completo del ETL](#flujo-completo-del-etl)
- [Consideraciones de Diseñó](#consideraciones-de-diseñó)
- [Limitaciones](#limitaciones)

---

## Estructura del Módulo

El módulo de ETL está compuesto por los siguientes directorios y archivos:

### 1. [etl/extract](./extract/)

Esta capa se encarga de obtener información desde APIs externas sin depender de librerías como `yfinance`. Representa la extracción en todo el proceso ETL.

<br>

#### 1.1 [/asset_metadata_extractor.py](./extract/asset_metadata_extractor.py)

Encargado de la extracción de metadatos de los activos financieros mediante su **Ticker**.

**Responsabilidades:**

- Dado un ticker, buscar su información en múltiples fuentes en cascada
  (Yahoo Search, Stooq, Yahoo Quote).
- Normalizar la información obtenida en un formato consistente (`Nombre, Tipo Activo y Mercado`).
- Manejar errores específicos de cada fuente y acumularlos para reportar fallos detallados.
- Implementar una estrategia de failover para garantizar
  la máxima resiliencia ante bloqueos o fallos de proveedores.

**Formato De Salida:**

```JSON
[
  {
    "nombre": str,
    "TipoActivo": str,
    "Mercado": str
  }
]
```

<br>

#### 1.2 [/market_data_extractor.py](./extract/market_data_extractor.py)

Encargado de la extracción de los datos de series temporales financieras de los Activos mediante su **Ticker**.

Se encarga de validar los datos extraídos:

**Responsabilidades:**

- Extraer datos históricos de activos financieros (OHLCV) desde Yahoo Finance.
- Validar la integridad de los datos extraídos
- Reintento de 3 veces con backoff exponencial para errores
  temporales (timeouts, rate limits)

**Formato de Salida:**

```JSON
[
  {
    "fecha": date,
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volumen": float
  }
]
```

<br>

### 2. [etl/transform](./transform/)

Esta capa se encarga de la manipulación, auditoria, limpieza y transformación de los datos financieros anteriormente extraídos. Pertenece al proceso de Transformación del proceso ETL.

**Esta capa no extrae datos, los procesa y mejora su calidad.**

<br>

#### 2.1 [/time_series_alignment.py](./transform/time_series_alignment.py)

Encargado de alinear todos los datos de series temporales de los Activos en un calendario bursátil con el fin de alinear correctamente los datos de los Activos para futuros análisis.

**Responsabilidades:**

- Construir una línea temporal común (**master timeline**)
- Alinear múltiples activos sobre esa línea
- Marcar datos faltantes como None

No realiza persistencia, ni aplica limpieza (forward fill, interpolación, etc).

**Formato de Salida:**

```JSON
{
  "BTC": [
    {
      "fecha": "2026-03-27",
      "valor": 65000.50
    },
    {
      "fecha": "2026-03-28",
      "valor": 64200.10
    },
    {
      "fecha": "2026-03-29",
      "valor": null
    }
  ]
}
```

<br>

#### 2.2 [/quality_audit.py](./transform/quality_audit.py)

Encargado de analizar la calidad de los datos sin modificarlos, actuando como un auditor y validador posterior a la transformación. Su función principal es identificar problemas en las series temporales, marcarlas para posteriores evaluaciones.

**Responsabilidades:**

- Analizar series temporales alineadas para detectar y clasificar problemas de calidad.
- Generar métricas porcentuales de calidad y un diagnóstico final para cada activo.
- Finalmente generar un "informe" porcentual y un diagnóstico sobre si los datos
  de cada activo son lo suficientemente confiable para ser usado en el modelo.

**Diagnóstico:**

Se clasifica cada activo según la calidad de sus datos, considerando la proporción de valores faltantes y comportamientos anómalos detectados en la serie temporal:

| Estado     | Condición       |
| ---------- | --------------- |
| DEFICIENTE | > 20% nulos     |
| RIESGOSO   | > 10% anomalías |
| ACEPTABLE  | Caso contrario  |

**Formato de Salida:**

```JSON
{
  "AAPL": {
    "serie": [
      {
        "fecha": "2026-03-25",
        "valor": 150.0,
        "raw": { "fecha": "2026-03-25", "valor": 150.0 },
        "es_nulo": false,
        "es_invalido": false,
        "es_anomalo": false,
        "tipo_anomalia": null
      },
      {
        "fecha": "2026-03-26",
        "valor": 210.0,
        "raw": { "fecha": "2026-03-26", "valor": 210.0 },
        "es_nulo": false,
        "es_invalido": false,
        "es_anomalo": true,
        "tipo_anomalia": "SALTO_BRUSCO"
      },
    ],
    "calidad": {
      "total_registros": 4,
      "pct_nulos": 0.25,
      "pct_invalidos": 0.0,
      "pct_anomalias": 0.50
    },
    "diagnostico": {
      "estado_calidad": "DEFICIENTE"
    }
  }
}
```

<br>

#### 2.3 [data_imputation.py](./transform/data_imputation.py)

Encargado de la manipulación, limpieza y aplicación de técnicas justificadas de tratamiento a las series temporales en base a la pre-auditoria realizada a estas.

**_En este proceso se lleva también acabo el paso de Carga (Load) del proceso ETL._**

**Responsabilidades:**

- Transformar datos crudos auditados en datos financieros aptos para análisis.
- Aplicar técnicas de imputación "relleno" para corregir valores nulos,
  inválidos o anómalos.
- Mantener un registro de trazabilidad de las correcciones aplicadas.
- Persistir los datos limpios y los registros de limpieza en la base de datos.

<br>

---

## Flujo completo del ETL

```text
EXTRACT
   ↓
Metadatos + OHLCV
   ↓
TRANSFORM
   ↓
Alineación temporal
   ↓
Auditoría de calidad
   ↓
Imputación de datos
   ↓
Carga a la BD
   ↓
Datos listos para análisis cuantitativo
```

<br>

---

## Consideraciones de Diseñó

- **Arquitectura modular:** El sistema está dividido en componentes independientes (Extracción, Transformación, Auditoría) para facilitar el mantenimiento.
- **Bajo acoplamiento y Alta cohesión:** Cada módulo tiene una responsabilidad única y clara, reduciendo la dependencia entre funciones.
- **Tolerancia a fallos:** El diseño permite gestionar errores en la carga de datos o de red sin interrumpir el proceso completo del ETL.
- **Validación de datos:** Se implementan filtros de integridad que aseguran que solo la información coherente llegue a etapas de cálculo.
- **Testing:** El sistema cuenta con una suite de pruebas unitarias y de integración que validan la precisión de los cálculos financieros y la estabilidad del flujo.

<br>

---

## Limitaciones

- Uso de APIs públicas (posibles bloqueos o rate limits)
- Dependencia de Yahoo Finance
- No incluye persistencia (eso pertenece a la capa LOAD)
