<h1 align="center">

_MidasQuant - Proyecto Análisis de Algoritmos_

![Python](https://img.shields.io/badge/python-3.11+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)

</h1>


## MidasQuant - Módulo ETL

Este módulo implementa el proceso ETL (Extract, Transform, Load) para el análisis de activos financieros dentro del proyecto MidasQuant,encargandose de orquestar la obtención de datos desde múltiples fuentes públicas, aplicar procesos de validación y normalización, y estructurar la información en formatos consistentes para su posterior análisis.  

El diseño del módulo sigue principios de bajo acoplamiento, tolerancia a fallos y separación de responsabilidades, permitiendo que cada etapa del ETL (extracción y transformación) funcione de manera independiente y escalable.  

Su objetivo es:

* Extraer datos financieros desde fuentes externas
* Transformarlos en estructuras limpias y consistentes
* Prepararlos para análisis cuantitativo

---

# Estructura del módulo

- **etl/**
  - **extract/**
    - asset_metadata_extractor.py
    - extractor_financiero.py
  - **transform/**
    - alineador_series.py
    - auditor_calidad.py

---

# 1. EXTRACT (Extracción de datos)

Esta capa se encarga de obtener información desde APIs externas sin depender de librerías como `yfinance`.

---

## 1.1 AssetMetadataExtractor

`asset_metadata_extractor.py`

El cua extrae metadatos de activos financieros como:

* Nombre
* Tipo de activo
* Mercado

### Características clave

**Failover (tolerancia a fallos)**
  Usa múltiples fuentes:

  1. Yahoo Search
  2. Stooq
  3. Yahoo Quote

**Bajo acoplamiento**
  Cada fuente está separada en métodos independientes (`_motor_*`)

**Normalización**
  Siempre retorna:

{
    "nombre": str,
    "tipo_activo": str,
    "mercado": str
}


### Complejidad

* `buscar_en_cascada`: **O(k)** (k = número de fuentes)
* Cada motor: **O(1)**

---

## 1.2 ExtractorFinanciero

`extractor_financiero.py`

Extrae datos históricos financieros (OHLCV):

* Open
* High
* Low
* Close
* Volume

### Características clave

* Validación de ticker
* Normalización por mercado (ej: activos colombianos)
* Uso directo de API de Yahoo (sin librerías externas)
* Manejo de errores robusto

---

### Flujo de extracción

1. Validar ticker
2. Preparar ticker
3. Llamar API de Yahoo
4. Procesar JSON
5. Validar datos
6. Retornar lista limpia

---

### Formato de salida

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


---

## 1.3 OHLCVValidador

Valida los datos extraídos:

Reglas:

* low ≤ open ≤ high
* low ≤ close ≤ high
* volumen ≥ 0
* sin fechas duplicadas

Ordena los datos cronológicamente

### Complejidad

* **O(n log n)** (por ordenamiento)

---

# 2. TRANSFORM (Transformación de datos)

Esta capa no extrae datos, los procesa y mejora su calidad.

---

## 2.1 Alineador de Series Temporales

`alineador_series.py`

Permite sincronizar múltiples activos en una misma línea de tiempo.

### Problema que resuelve

Cada activo tiene fechas distintas → imposible comparar directamente.

### Solución:

* Construye una **línea de tiempo maestra**
* Alinea todos los activos a esas fechas
* Usa `None` cuando faltan datos

---

### Entrada

* DB session
* Lista de activos
* Fecha inicio / fin

---

### Salida

<pre> json { "AAPL": [ { "fecha": "YYYY-MM-DD", "valor": 123.45 }, { "fecha": "YYYY-MM-DD", "valor": null } ], "TSLA": [ { "fecha": "YYYY-MM-DD", "valor": 250.10 } ] } </pre>

---

### Complejidad

* Construcción timeline: **O(n log n)**
* Alineación: **O(n × m)**
  (n fechas, m activos)

---

## 2.2 Auditor de Calidad

`auditor_calidad.py`

Analiza la calidad de los datos sin modificarlos, actuando como una capa de validación posterior a la transformación.  
Su función principal es identificar problemas en las series temporales, como datos faltantes, valores inválidos o comportamientos anómalos, permitiendo evaluar si la información es confiable antes de ser utilizada en modelos de análisis cuantitativo.

---

### Qué detecta

* Datos nulos (gaps)
* Precios inválidos (≤ 0)
* Anomalías (>30% cambio diario)

---

### Métricas generadas

{
    "total_registros": int,
    "pct_nulos": float,
    "pct_invalidos": float,
    "pct_anomalias": float
}


---

### Diagnóstico

Clasifica cada activo:

| Estado     | Condición      |
| ---------- | -------------- |
| DEFICIENTE | >20% nulos     |
| RIESGOSO   | >10% anomalías |
| ACEPTABLE  | Caso contrario |

---

### Salida completa

<pre> json id="8zddf7" { "AAPL": { "serie": [ { "fecha": "YYYY-MM-DD", "valor": 123.45 } ], "calidad": { "total_registros": 100, "pct_nulos": 0.05, "pct_invalidos": 0.01, "pct_anomalias": 0.08 }, "diagnostico": { "estado_calidad": "ACEPTABLE" } } } </pre>

---

### Complejidad

* **O(n²)** (comparaciones de variación)

Esta complejidad se debe a que, además de recorrer la serie de datos, se realizan comparaciones entre valores consecutivos para detectar cambios bruscos (anomalías).  
En escenarios con múltiples activos o grandes volúmenes de datos históricos, este proceso puede volverse costoso, ya que el número de operaciones crece rápidamente con el tamaño de la serie.

---

# Flujo completo del ETL

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
Datos listos para análisis cuantitativo
```

---

# Características del diseño

* Arquitectura modular
* Bajo acoplamiento
* Alta cohesión
* Tolerancia a fallos
* Validación de datos
* Preparado para escalabilidad

---

# Limitaciones

* Uso de APIs públicas (posibles bloqueos o rate limits)
* Dependencia de Yahoo Finance
* No incluye persistencia (eso pertenece a la capa LOAD)

---

# Posibles mejoras para las siguientes entregas

* Implementar cache de respuestas
* Añadir más fuentes
* Paralelizar extracción
* Mejorar detección de anomalías (ML)
* Agregar imputación de datos faltantes
