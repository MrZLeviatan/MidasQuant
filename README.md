<h1 align="center">

_MidasQuant - Proyecto Análisis de Algoritmos_

![Python](https://img.shields.io/badge/python-3.11+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)

</h1>

Sistema para el análisis algorítmico de series de tiempo financieras (acciones y ETFs), basado en la implementación explícita de algoritmos clásicos para evaluar su comportamiento histórico, eficiencia computacional y complejidad formal, utilizando datos obtenidos dinámicamente mediante peticiones HTTP para garantizar reproducibilidad.

<br>

## Tabla de Contenido

- [Tabla de Contenido](#tabla-de-contenido)
- [Descripción formal del Proyecto](#descripción-formal-del-proyecto)
  - [Descripción General](#descripción-general)
  - [Alcance Técnico](#alcance-técnico)
  - [Documentación de Software](#documentación-de-software)
- [Requisitos Software](#requisitos-software)
- [Instalación](#instalación)
  - [1. Clonar el Repositorio](#1-clonar-el-repositorio)
  - [2. Verificar la versión de Python](#2-verificar-la-versión-de-python)
  - [3. Crear un entorno virtual](#3-crear-un-entorno-virtual)
  - [4. Instalar dependencias del proyecto](#4-instalar-dependencias-del-proyecto)
  - [5. Ejecutar la aplicación web](#5-ejecutar-la-aplicación-web)

<Br>

---

## Descripción formal del Proyecto

**Proyecto Análisis Algorítmico de Series de Tiempo Financieras**

**Programa:** Ingeniería de Sistemas y Computación

**Asignatura:** Análisis de Algoritmos

**Universidad:** Universidad del Quindío

<br>

### Descripción General

El presente proyecto tiene como finalidad el diseño e implementación de una aplicación web orientada al análisis algorítmico de series de tiempo financieras, utilizando datos históricos reales de acciones y ETFs obtenidos mediante procesos automatizados de extracción desde fuentes públicas autorizadas.

El sistema permite:

- Ejecutar un proceso completo de Extracción, Transformación y Carga (ETL).
- Implementar explícitamente algoritmos clásicos de similitud entre series temporales.
- Analizar patrones de comportamiento mediante técnicas de ventana deslizantes.
- Calcular métricas de riesgo como volatilidad histórica.
- Visualizar resultados a través de un dashboard interactivo.
- Generar reportes técnicos en formatos PDF.

El enfoque central del proyecto no es únicamente la construcción de una herramienta funcional, sino el análisis formal del comportamiento computacional de los algoritmos implementados, incluyendo su fundamentación matemática y estudio de complejidad temporal y espacial.

El sistema garantiza reproducibilidad total: cualquier evaluador puede ejecutar el proyecto desde cero y reconstruir el dataset maestro y los resultados sin intervención manual.

<Br>

### Alcance Técnico

El proyecto abarca:

- Descarga automatizada de datos históricos financieros (mínimo 5 años, mínimo 20 activos).
- Implementación manual de algoritmos de similitud (sin uso de funciones encapsuladas de alto nivel).
- Clasificación de activos según métricas de riesgo calculadas algorítmicamente.
- Construcción de visualizaciones financieras (mapa de calor, gráficos de velas, medias móviles).
- Despliegue como aplicación web funcional.

<br>

### Documentación de Software

La documentación formal del proyecto se encuentra organizada y mantenida en Notion, donde se detallan los siguientes documentos:

- Planteamiento del problema
- Especificación de requisitos
- Especificación casos de uso del sistema
- Informe general del sistema
- Prototipo del sistema
- Plan de pruebas
- Manual de configuración BD
- Manual técnico de configuración
- Manual de usuario

Enlace a la documentación completa:
[Documentación Notion]()

El presente repositorio contiene la implementación técnica del sistema y la información necesaria para su ejecución y validación.

<br>

---

## Requisitos Software

- Python 3.11+
- Gestor de dependencias (pip)
- Librerías estándar para:
  - Solicitudes HTTP
  - Procesamiento de JSON/CSV
  - Manipulación de estructuras de datos
  - Visualización financiera
  - Generación de reportes PDF
- Streamlit para la interfaz web

<br>

---

## Instalación

Esta sección describe el proceso necesario para configurar el entorno de ejecución del proyecto y desplegar la aplicación web localmente. El sistema está desarrollado en Python y utiliza Streamlit como framework para la construcción del dashboard interactivo.

#### 1. Clonar el Repositorio

Primero, se debe clonar el repositorio del proyecto desde el sistema de control de versiones.

```bash
git clone https://github.com/MrZLeviatan/MidasQuant.git
cd MidasQuant
```

Esto descargará el código fuente completo del proyecto en el entorno local.

<br>

#### 2. Verificar la versión de Python

El proyecto requiere Python 3.11+. Para verificar la versión instalada en el sistema, ejecutar:

```bash
python --version
```

o

```bash
python3 --version
```

Si la versión instalada es inferior, se recomienda actualizar Python antes de continuar con la instalación.

<br>

#### 3. Crear un entorno virtual

Para aislar las dependencias del proyecto y evitar conflictos con otras librerías del sistema, se recomienda crear un entorno virtual.

```bash
python -m venv venv
```

Activar el entorno virtual:

En Windows:

```bash
venv\Scripts\activate
```

En Linux / macOs

```bash
source venv/bin/activate
```

<br>

#### 4. Instalar dependencias del proyecto

Una vez activado el entorno virtual, se deben instalar las librerías necesarias utilizando el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

Este archivo contiene todas las dependencias requeridas para:

- Procesamiento de datos
- Solicitudes HTTP a APIs públicas
- Visualización de datos financieros
- Construcción de la interfaz web
- Generación de reportes en PDF

<br>

#### 5. Ejecutar la aplicación web

Se puede iniciar la aplicación web basada en Streamlit en el directorio raíz del proyecto 'MidasQuant/'

```bash
python -m streamlit run app/main.py
```

Después de ejecutar este comando, la aplicación estará disponible en el navegador en una dirección similar a:

```
http://localhost:8501
```
