"""
Implementación del algoritmo Dynamic Time Warping
para series temporales financieras. (HU15).

Responsabilidades:
- Comparar series temporales desfasadas.
- Encontrar similitud flexible entre secuencias.
- Calcular costo mínimo de alineación.
"""


def calcular_dtw(
    serie_1: list[float],
    serie_2: list[float]
) -> dict:
    """
    Calcula la distancia DTW entre dos series temporales.

    DTW permite comparar series aunque existan
    desplazamientos temporales.

    Complejidad Temporal: O(n²) - Iteración doble para el recorrido
    Complejidad Espacial: O(n²) - Necesita llenar una matriz nxn
    """

    n = len(serie_1)
    m = len(serie_2)

    # Matriz de costos acumulados
    matriz = []

    # Construcción manual de la matriz
    for _ in range(n + 1):

        fila = []

        for _ in range(m + 1):

            # Inicialización con infinito
            fila.append(float("inf"))

        matriz.append(fila)

    # Punto inicial
    matriz[0][0] = 0

    """
    Recorremos la matriz mediante programación dinámica

    costo_actual + mejor_camino_previo

    Esto permite construir progresivamente el camino de
        alineación óptimo.
    """
    for i in range(1, n + 1):

        for j in range(1, m + 1):

            # Diferencia absoluta entre los puntos actuales de ambas series
            costo = abs(
                serie_1[i - 1] - serie_2[j - 1]
            )

            """
            Se selecciona el menor costo acumulado entre tres
            posibles movimientos:

            - Inserción -> arriba
            - Eliminación -> izquierda
            - Match -> diagonal

            Esto permite flexibilidad temporal:
            """
            minimo_previo = min(

                matriz[i - 1][j],      # Inserción

                matriz[i][j - 1],      # Eliminación

                matriz[i - 1][j - 1]   # Match
            )

            # Valor actual de la matriz
            matriz[i][j] = costo + minimo_previo

    # La esquina inferior derecha contiene el costo mínimo total de alineación
    distancia = matriz[n][m]

    # Retorna el DTW final y la matriz completa
    return {
        "distancia": round(distancia, 4),
        "matriz": matriz
    }
