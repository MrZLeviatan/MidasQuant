<h1 align="center">

_MidasQuant - Benchmarking de Ordenamiento_

</h1>

Este módulo se enfoca en el análisis comparativo de rendimiento de algoritmos de ordenamiento aplicados a series de tiempos financieras.

Su propósito es evaluar la eficiencia computacional de 12 algoritmos clásicos al procesar los datos unificados y limpios obtenidos en la etapa de ETL.

<br>

## Tabla de Contenido

- [Tabla de Contenido](#tabla-de-contenido)
- [Propósito del Análisis](#propósito-del-análisis)
  - [Criterios de Ordenamiento](#criterios-de-ordenamiento)
- [Tabla Comparativa de Complejidad](#tabla-comparativa-de-complejidad)
- [Descripción de Algoritmos](#descripción-de-algoritmos)
  - [1. TimSort](#1-timsort)
  - [2. Comb Sort](#2-comb-sort)
  - [3. Selection Sort](#3-selection-sort)
  - [4. Tree Sort](#4-tree-sort)
  - [5. Pigeonhole Sort](#5-pigeonhole-sort)
  - [6. Bucket Sort](#6-bucket-sort)
  - [7. QuickSort](#7-quicksort)
  - [8. HeapSort](#8-heapsort)
  - [9. Bitonic Sort](#9-bitonic-sort)
  - [10. Gnome Sort](#10-gnome-sort)
  - [11. Binary Insertion Sort](#11-binary-insertion-sort)
  - [12. Radix Sort](#12-radix-sort)
- [Visualización de Resultados](#visualización-de-resultados)

<br>

---

## Propósito del Análisis

El sistema busca medir el costo computacional (tiempo de ejecución) en relación con el tamaño de la muestra de datos financiera. Esto permite comprender cómo diferentes enfoques algorítmicos producen resultados distintos en términos en precisión y costo.

### Criterios de Ordenamiento

Para garantizar la integridad del análisis, los algoritmos deben seguir estas reglas de comparación:

1. **Criterio Primarios:** Fecha de cotización del activo (Ascendente).
2. **Criterio Secundario:** En caso de empate en fecha, se ordena pro Precio de Cierre (Close)

<br>

---

## Tabla Comparativa de Complejidad

A continuación, se presenta la complejidad teórica de los algoritmos solicitados para el análisis de datos.

| #   | Algoritmo             | Complejidad (Big-O) |
| --- | --------------------- | ------------------- |
| 1   | TimSort               | O(n log n)          |
| 2   | Comb Sort             | O(n²)               |
| 3   | Selection Sort        | O(n²)               |
| 4   | Tree Sort             | O(n log n)          |
| 5   | Pigeonhole Sort       | O(n + Range)        |
| 6   | Bucket Sort           | O(n + k)            |
| 7   | QuickSort             | O(n log n)          |
| 8   | HeapSort              | O(n log n)          |
| 9   | Bitonic Sort          | O(log² n)           |
| 10  | Gnome Sort            | O(n²)               |
| 11  | Binary Insertion Sort | O(n²)               |
| 12  | Radix Sort            | O(nk)               |

<br>

---

## Descripción de Algoritmos

> [!IMPORTANT]
> Aislamiento de Pruebas: Cada algoritmo se ejecuta mediante un test nativo independiente. Esto es fundamental para medir el rendimiento neto del código, eliminando el ruido visual de la interfaz de usuario y evitando la competencia por recursos de hardware (como la RAM) con otros procesos del sistema. Así garantizamos que el tiempo registrado sea lo más cercano a la realidad técnica.

> [!TIP]
> **Benchmark y Pruebas de Estrés:** Para validar el rendimiento neto y observar los tiempos de ejecución sin interferencias, puedes ejecutar el test nativo directamente desde la terminal. Esto permite ver cómo escala el algoritmo y en qué volumen de datos alcanza su límite operativo.

### 1. [TimSort](./tim_sort.py)

Algoritmo híbrido derivado del Merge Sort e Insertion Sort. Funciona encontrando sub-secuencias ya ordenadas (runs) y combinándolas. Es el estándar en Python debido a su alta eficiencia en datos del mundo real.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_tim_sort.py
```

<br>

### 2. [Comb Sort](./comb_sort.py)

Mejora del Bubble Sort que elimina los "tortugas" (valores pequeños al final de la lista) utilizando un factor de brecha (gap) que se reduce en cada iteración.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_comb_sort.py
```

<br>

### 3. [Selection Sort](./selection_sort.py)

Funciona dividiendo la lista en una parte ordenada y otra desordenada, buscando repetidamente el elemento mínimo de la parte desordenada y moviéndolo al principio.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_selection_sort.py
```

<br>

### 4. [Tree Sort](./tree_sort.py)

Construye un Árbol Binario de Búsqueda (BST) con los elementos de la lista y luego realiza un recorrido in-order para obtener los elementos ya ordenados.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_tree_sort.py
```

> [!WARNING]
> Por la estructura de datos que se manejan, es común que este algoritmo falle a cierta cantidad.

<br>

### 5. [Pigeonhole Sort](./pigeonhole_sort.py)

Algoritmo de ordenamiento no comparativo ideal cuando el rango de valores y el número de elementos son similares. Mueve elementos a "huecos" (pigeonholes) basados en su valor.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_pigeonhole_sort.py
```

<br>

### 6. [Bucket Sort](./bucket_sort.py)

Distribuye los elementos en varios "baldes" (buckets). Luego, cada balde se ordena individualmente (usando otro algoritmo o de forma recursiva). Es eficiente cuando los datos están distribuidos uniformemente.

<br>

### 7. [QuickSort](./quick_sort.py)

Basado en la técnica divide y vencerás. Elige un "pivote" y particiona la lista en dos sub-listas (menores y mayores al pivote), ordenándolas recursivamente.

<br>

### 8. [HeapSort](./heap_sort.py)

Utiliza una estructura de datos de "montículo" (heap) para encontrar el elemento máximo/mínimo y extraerlo, reconstruyendo el montículo hasta que la lista esté vacía.

<br>

### 9. [Bitonic Sort](./bitonic_sort.py)

Algoritmo de ordenamiento paralelo que construye secuencias bitónicas (que crecen y luego decrecen) para luego mezclarlas de forma ordenada.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_bitonic_sort.py
```

<br>

### 10. [Gnome Sort](./gnome_sort.py)

Similar al Insertion Sort, pero mueve un elemento a su posición correcta mediante una serie de intercambios, regresando un paso atrás cada vez que se realiza un cambio.

<br>

### 11. [Binary Insertion Sort](./binary_insertion_sort.py)

Variante del Insertion Sort que utiliza búsqueda binaria para encontrar el lugar exacto donde insertar el nuevo elemento, reduciendo el número de comparaciones.

**Ejecuta el siguiente comando para ver los resultados detallados:**

```bash
pytest -s -v tests/sorting/test_binary_insertion_sort.py
```

<br>

### 12. [Radix Sort](./radix_sort.py)

Ordena los datos procesando sus dígitos individuales (desde el menos significativo al más significativo) utilizando un algoritmo de ordenamiento estable como auxiliar (generalmente Counting Sort).

<br>

---

## Visualización de Resultados

El sistema genera automáticamente un diagrama de barras que representa los tiempos de ejecución de forma ascendente. Adicionalmente, se extraen y ordenan los 15 días con mayor volumen de negociación para cada activo procesado.

<br>
