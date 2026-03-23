# Base de excepciones para errores relacionados a las reglas del dominio
from app.exceptions.base.dominio_exception import DominioError


# Excepciones específicas para validaciones de fechas en el dominio
class RangoFechasError(DominioError):
    """
    Error cuando la fecha de inicio no es menor que la fecha de fin.

    Regla de negocio:
    - La fecha de inicio debe ser estrictamente menor que la fecha de fin.
    """
    def __init__(self):
        # Inicializa el error con un mensaje específico y un código de error.
        super().__init__(
            message="La fecha de inicio debe ser menor que la fecha de fin.",
            code="RANGO_FECHAS_INVALIDO"
        )


# Excepción para validar que el horizonte temporal mínimo se cumpla
class HorizonteInvalidoError(DominioError):
    """
    Error cuando el rango no cumple el horizonte mínimo requerido.

    Regla de negocio:
    - El rango entre fechas debe ser mayor o igual a 'min_anios' años.
    """
    def __init__(self, min_anios: int, diferencia: int):
        super().__init__(
            # Permite generar mensaje dinámicos y más informativos
            # El mensaje incluye el horizonte mínimo requerido y el horizonte actual
            message=(
                f"El rango de fechas debe ser al menos de {min_anios} años,  "
                f"pero el rango proporcionado es de solo {diferencia} años."
            ),
            code="HORIZONTE_MINIMO_INVALIDO"
        )
