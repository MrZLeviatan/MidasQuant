"""
Algoritmo de Similitud por Coseno para
series temporales financieras. (HU16)

Responsabilidades:
- Medir similitud angular entre dos vectores.
- Detectar comportamiento direccional similar.
"""

from math import sqrt


def calcular_similitud_coseno(
    serie_1: list[float],
    serie_2: list[float]
) -> dict:
    """
    Calcula la similitud por coseno entre dos series.

    Complejidad: O(n) - Iteración de longitud n (no están anidados)
    """

    # Representa la suma de los productos de los componentes
    producto_punto = 0

    for i in range(len(serie_1)):
        # Acumula la multiplicación de los valores en el mismo instante
        producto_punto += (
            serie_1[i] * serie_2[i]
        )

    # Calcula la norma euclidiana o "longitud" del primer vector.
    magnitud_1 = 0

    for valor in serie_1:
        # Suma de los cuadrados de cada elemento.
        magnitud_1 += valor ** 2
    # Aplicación de raíz cuadrada para completar la norma L2.
    magnitud_1 = sqrt(magnitud_1)

    # Calcula la norma euclidiana o "longitud" del segundo vector.
    magnitud_2 = 0

    for valor in serie_2:
        # Suma de los cuadrados de cada elemento del segundo activo.
        magnitud_2 += valor ** 2

    # Aplicación de raíz
    magnitud_2 = sqrt(magnitud_2)

    # Evitar división inválida
    if magnitud_1 == 0 or magnitud_2 == 0:
        similitud = 0

    else:
        # Fó®mula cos(0) = (A*B) / (|A|) * (|B|)
        similitud = (
            producto_punto / (magnitud_1 * magnitud_2)
        )
    # Retorno estructurado con redondeo
    return {
        "valor": round(similitud, 6)
    }
