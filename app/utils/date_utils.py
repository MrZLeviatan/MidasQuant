"""
Responsabilidades:
- Validar rangos de fechas
- Calcular diferencia entre fechas
- Verificar reglas de negocio (horizonte mínimo)
"""

from datetime import date


# Recibe dos fechas y devuelve la diferencia en años
def calcular_diferencia_anios(fecha_inicio: date, fecha_fin: date) -> float:
    """
    Calcula la diferencia en años entre dos fechas.

    Complejidad: O(1) - Operación constante, ya que solo se realizan cálculos básicos.
    """

    # Calculamos la diferencia en días
    dias = (fecha_fin - fecha_inicio).days

    # Convertimos los días a años (aproximadamente)
    return dias / 365


# Recibe dos fechas y valida que el rango sea correcto
def validar_rango_fechas(fecha_inicio: date, fecha_fin: date) -> None:
    """
    Valida que el rango de fechas sea correcto.

    Reglas:
    - fecha_inicio < fecha_fin

    Complejidad: O(1) - Operación constante, ya que solo se realiza una comparación.
    """

    # Validamos que la fecha de inicio sea menor que la fecha de fin
    if fecha_inicio >= fecha_fin:
        raise ValueError("La fecha de inicio debe ser menor que la fecha de fin.")


# Recibe dos fechas y valida que el rango cumpla con un horizonte mínimo (5 años)
def validar_horizonte_minimo(fecha_inicio: date,
                             fecha_fin: date, min_anios: int = 5) -> None:
    """
    Valida que el rango de fechas cumpla con un horizonte mínimo.

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
        raise ValueError(
            f"El rango de fechas debe ser al menos de {min_anios} años. "
            f"Actual: {diferencia:.2f} años."
        )
