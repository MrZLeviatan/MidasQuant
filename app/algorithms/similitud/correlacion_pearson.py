"""
Implementación del algoritmo de Correlación de Pearson
para series temporales financieras. (HU14)

Responsabilidades:
- Calcular correlación lineal entre dos series.
- Medir relación estadística entre activos.
"""

# Librería matemática estándar (Para la raíz cuadrada)
from math import sqrt

# Importación de excepción
from app.exceptions import (
    FalloLongitudError,
    ObjetoVacio
)


def calcular_correlacion_pearson(
    serie_1: list[float],
    serie_2: list[float]
) -> float:
    """
    Calcula la correlación de Pearson entre dos series.

    Complejidad: O(n) - Itera una vez
    - Espacial: O(1)
    """

    # Validar longitud de series
    # La correlación Pearson requiere vectores de igual tamaño
    if (len(serie_1) != len(serie_2)):
        raise FalloLongitudError(
            longitud_1=len(serie_1),
            longitud_2=len(serie_2),
            detalle_adicional="Fallo en el algoritmo Distancia Euclidiana"
        )

    # Sacar la longitud de la serie 1
    n = len(serie_1)

    # Evitar división por cero
    if n == 0:
        raise ObjetoVacio(
            objeto_nombre="serie_comparativa"
        )

    # Se calcula las medias aritméticas necesarias para hallar las desviaciones
    promedio_x = sum(serie_1) / n
    promedio_y = sum(serie_2) / n

    # Acumular la covarianza (suma de productos de desviaciones)
    numerador = 0.0

    # Acumular la suma de cuadrados (para el calculo de la desviación estándar)
    suma_x = 0.0
    suma_y = 0.0

    for i in range(n):

        # Cálculo de la distancia de cada punto respecto a su media
        dx = serie_1[i] - promedio_x
        dy = serie_2[i] - promedio_y

        # Acumulación de productos
        numerador += dx * dy

        # Acumulación de potencia para normalizar la varianza.
        suma_x += dx ** 2
        suma_y += dy ** 2

    # Representa la variabilidad de la desviaciones estándar
    denominador = sqrt(suma_x) * sqrt(suma_y)

    # Protección matemática
    if denominador == 0:
        return 0.0

    # Cálculo final del coeficiente, el valor resultante estará siempre entre -1 y 1
    correlacion = numerador / denominador

    # Retorno redondeado para consistencia de datos
    return round(correlacion, 6)
