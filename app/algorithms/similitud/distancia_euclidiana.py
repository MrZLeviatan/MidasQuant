"""
Implementación del algoritmo de distancia euclidiana
para series temporales financieras. (HU13)

Responsabilidades:
- Calcular distancia entre dos vectores numéricos.
- Mantener independencia total de UI y BD.
"""

# Librería matemática estándar (para la raíz cuadrada)
import math

# Importaciones de excepciones
from app.exceptions import (
    FalloLongitudError
)


def calcular_distancia_euclidiana(
    serie_1: list[float],
    serie_2: list[float]
):
    """
    Calcular la distancia euclidiana entre dos series temporales

    Fórmula:
        d(x,y) = sqrt(sum((xi - yi)^2))

    Complejidad: O(n) - El algoritmo realiza una iteración lineal
    Complejidad Espacial: O(1) - No se crean estructuras de datos adicionales
    """

    # Validar longitud de series
    # La distancia euclidiana requiere vectores de igual tamaño
    if (len(serie_1) != len(serie_2)):
        raise FalloLongitudError(
            longitud_1=len(serie_1),
            longitud_2=len(serie_2),
            detalle_adicional="Fallo en el algoritmo Distancia Euclidiana"
        )

    # Acumulador principal para la sumatoria de cuadrados
    suma = 0.0

    """
    Recorrer ambas series simultáneamente

    Uso de `zip` para iterar en paralelo, crea un generador eficiente de tuplas (x,y)
    """
    for x, y in zip(serie_1, serie_2):

        # Diferencia entre puntos
        diferencia = x - y

        # Elevación al cuadrado para eliminar signos negativos y penalizar desviaciones.
        suma += diferencia ** 2

    # Distancia final
    distancia = math.sqrt(suma)

    # Retorno del valor con redondeo de 6 decimales para evitar ruido de coma flotante.
    return round(distancia, 6)
