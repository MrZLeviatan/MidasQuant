from app.exceptions.base_exceptions import FuenteError


# Exception propia para el manejo de Yahoo Finance.
class YahooError(FuenteError):
    """
    Excepción lanzada cuando falla la extracción de datos de Yahoo Finance.

    - original_error: Error original capturado
    """
    def __init__(self, ticker: str, original_error: Exception | str):
        super().__init__(
            message=(
                f"Error al extraer datos desde Yahoo Finance para el ticker '{ticker}'."
                f"Detalle: {str(original_error)}"
            ),
            code="YAHOO_EXTRACTION_ERROR"
        )

        self.ticker = ticker
        self.original_error = original_error


# Exception propia para el manejo de Stooq
class StooqError(FuenteError):
    """
    Excepción lanzada cuando falla la extracción de datos desde Stooq.
    """
    def __init__(self, ticker: str, original_error: Exception | str):
        super().__init__(
            message=(
                f"Error al extraer datos desde Stooq para el ticker '{ticker}'. "
                f"Detalle: {str(original_error)}"
            ),
            code="STOOQ_EXTRACTION_ERROR"
        )

        self.ticker = ticker
        self.original_error = original_error


# Exception propia para el manejo de MarketWatch
class MarketWatchError(FuenteError):
    """
    Excepción lanzada cuando falla la extracción de datos desde MarketWatch
    """
    def __init__(self, ticker: str, original_error: Exception | str):
        super().__init__(
            message=(
                f"Error al extraer datos desde MarketWatch para el ticker '{ticker}'. "
                f"Detalle: {str(original_error)}"
            ),
            code="MARKETWATCH_EXTRACTION_ERROR"
        )

        self.ticker = ticker
        self.original_error = original_error


# Exception global
class ExtraccionFallidaError(Exception):
    """
    Excepción lanzada cuando ninguna fuente logra devolver datos válidos.

    Attributes:
        ticker (str): Activo consultado
        errores (list[str]): Lista de errores por fuente
    """
    def __init__(self, ticker: str, errores: list[str]):
        message = (
            f"No se pudo obtener información para el ticker '{ticker}' "
            f"desde ninguna fuente disponible. Errores: {errores}"
        )

        super().__init__(message)

        self.ticker = ticker
        self.errores = errores
