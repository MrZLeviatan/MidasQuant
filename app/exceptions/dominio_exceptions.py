# Base de excepciones para errores relacionados a las reglas del dominio
from app.exceptions.base_exceptions import DominioError


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


# Excepciones específicas para validaciones de Minimo de Activos en Portafolio
class MinimoActivosError(DominioError):
    """
    Excepción lanzada cuando un portafolio no cumple con el
    número mínimo de activos requerido.

    Regla de negocio:
    - Un portafolio debe contener al menos 20 activos para ser considerado válido.
    """
    def __init__(self, minimo: int = 20, actual: int = 0):
        super().__init__(
            message=(
                f"El portafolio debe contener al menos {minimo} activos. "
                f"Actual: {actual}."
            ),
            code="MINIMO_ACTIVOS_INVALIDO"
        )

        self.minimo = minimo
        self.actual = actual


# Excepciones específicas para validación de tickers en el servicio de portafolio
class TickerInvalidoError(DominioError):
    """
    Excepción personalizada para indicar que un ticker es inválido.

    Reglas de validación:
    - Solo caracteres alfanuméricos.
    - Longitud entre 1 y 10 caracteres.
    """
    def __init__(self, ticker: str, motivo: str):
        super().__init__(
            message=f"Ticker inválido: '{ticker}'. Motivo: {motivo} ",
            code="TICKER_INVALIDO"
        )
    # Guardamos contexto adicional
        self.ticker = ticker
        self.motivo = motivo


# Excepción para indicar que la lista de tickers se encuentra vacía
class ListaTickersVaciaError(DominioError):
    """
    Excepción lanzada cuando la lista de tickers está vacía en un contexto
    donde se requiere al menos un valor.
    """
    def __init__(self):
        super().__init__(
            message="La lista de tickers no puede estar vacía.",
            code="LISTA_TICKERS_VACIA"
        )
