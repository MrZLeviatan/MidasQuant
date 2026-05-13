import math
from typing import List


def calcular_desviacion_estandar(valores: List[float]) -> float:
    """
    Calcula la desviación estándar poblacional.

    Fórmula:
        σ = sqrt( (1/n) * Σ(xi - μ)^2 )

    Donde:
        μ = media de los valores
        xi = cada dato de la serie
    """
    # Captura la cantidad de elementos (n) para promediar y normalizar.
    n = len(valores)

    # Evitar división por 0
    if n == 0:
        return 0.0

    # Suma total dividida entre el número de datos.
    media = sum(valores) / n

    # # Cálculo de la varianza
    varianza = sum((x - media) ** 2 for x in valores) / n

    return math.sqrt(varianza)
