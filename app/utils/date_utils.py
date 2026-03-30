"""
Responsabilidades:
- Validar rangos de fechas
- Calcular diferencia entre fechas
- Verificar reglas de negocio (horizonte mínimo)
"""

# Importamos el date para manejo de fechas en precisión.
from datetime import date

# Importar excepciones personalizadas para manejo de errores específicos
from app.exceptions import (
    RangoFechasError,
    HorizonteInvalidoError,
    RangoFechaFinError
)


def calcular_diferencia_anios(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula la diferencia en años entre dos fechas, considerando un año como 366 días.

    Complejidad: O(1) - Operación constante, ya que solo se realizan cálculos básicos.
    """

    # Calculamos la diferencia en días
    dias = (fecha_fin - fecha_inicio).days

    # Convertimos los días a años (aproximadamente)
    return dias / 365


def validar_rango_fechas(fecha_inicio: date, fecha_fin: date) -> None:
    """
    Valida que el rango entre dos fechas sea valido.

    Reglas de negocio:
    - fecha_inicio < fecha_fin

    Complejidad: O(1) - Operación constante, ya que solo se realiza una comparación.
    """

    # Validamos que la fecha de inicio sea menor que la fecha de fin
    if fecha_inicio >= fecha_fin:
        raise RangoFechasError(
            # Pasamos las fechas al campo 'detail' para auditoría técnica
            detail={
                "fecha_inicio_recibida": str(fecha_inicio),
                "fecha_fin_recibida": str(fecha_fin)
            }
        )


def validar_horizonte_minimo(
        fecha_inicio: date,
        fecha_fin: date, min_anios: int = 5
) -> None:
    """
    Valida que el rango de fechas cumpla con un horizonte mínimo establecido por el
        negocio (5 años).

    Complejidad: O(1) - Operación constante, ya que solo se realizan cálculos básicos
        y una comparación.
    """

    # Se obtiene la diferencia en años entre las dos fechas
    diferencia = calcular_diferencia_anios(fecha_inicio, fecha_fin)

    """
    Validamos que la diferencia en años sea al menos igual al horizonte mínimo.
    - Si la diferencia es menor, se lanza un error indicando el rango mínimo requerido.
    - Si la diferencia es suficiente, no se realiza ninguna acción.
    """
    if diferencia < min_anios:
        raise HorizonteInvalidoError(min_anios=min_anios, diferencia=diferencia)


def validar_fecha_futura(fecha_fin: date) -> None:
    """
    Validación de rango de fechas para la prohibición de fechas futuras.
    """
    hoy = date.today()
    if fecha_fin > hoy:
        raise RangoFechaFinError(
            fecha_fin=fecha_fin,
            detail={"fecha_actual": str(hoy), "fecha_fin_intentada": str(fecha_fin)}
        )
