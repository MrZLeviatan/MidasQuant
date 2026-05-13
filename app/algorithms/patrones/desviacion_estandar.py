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

    n = len(valores)
    if n == 0:
        return 0.0

    media = sum(valores) / n

    varianza = sum((x - media) ** 2 for x in valores) / n

    return math.sqrt(varianza)


def clasificar_riesgo(desviacion: float) -> str:
    """
    Clasifica el activo según su desviación estándar.
    """

    if desviacion < 1.5:
        return "Estandar"
    elif desviacion < 3.0:
        return "Moderado"
    else:
        return "Agresivo"
