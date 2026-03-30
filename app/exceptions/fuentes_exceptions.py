# Base de excepciones para errores relacionados a las fuentes de extracción de datos
from app.exceptions.base_exceptions import FuenteError

# El Union es la variable "||" en Python
from typing import Union


class YahooError(FuenteError):
    """
    Representa un error durante la extracción de datos desde Yahoo Finance.

    Reglas de validación:
    - El ticker debe ser válido según las reglas de Yahoo Finance / Search.
    - El error puede ocurrir en diferentes etapas del proceso de extracción
    """
    def __init__(
            self,
            ticker: str,
            etapa: str,
            message: str,
            detail: Union[Exception, str],
            code: str = "YAHOO_ERROR"
    ):
        # Guardamos el ticker dentro del detalle para no perder contexto técnico
        tecnico = {"ticker": ticker, "trace": str(detail)}

        super().__init__(
            fuente="Yahoo Finance / Search",
            etapa=etapa,
            message=message,
            code=code,
            detail=tecnico
        )
        self.ticker = ticker


class StooqError(FuenteError):
    """
    Representa un error durante la extracción de datos desde Stooq.

    Reglas de validación:
    - El ticker debe ser válido según las reglas de Stooq.
    - El error puede ocurrir en diferentes etapas del proceso de extracción
    """
    def __init__(
        self,
        ticker: str,
        etapa: str,
        message: str,
        detail: Union[Exception, str],
        code: str = "STOOQ_ERROR"
    ):
        tecnico = {"ticker": ticker, "trace": str(detail)}

        super().__init__(
            fuente="Stooq",
            etapa=etapa,
            message=message,
            code=code,
            detail=tecnico
        )
        self.ticker = ticker


class ExtraccionFallidaError(Exception):
    """
    Excepción lanzada cuando ninguna fuente logra devolver datos válidos.

    Reglas de validación:
    - Se lanza cuando todas las fuentes de extracción intentadas
        para un ticker específico fallan
    """
    def __init__(self, ticker: str, errores: list[FuenteError]):
        self.ticker = ticker
        self.errores = errores

        # El mensaje para el usuario general Ui
        mensaje_ui = (
            f"No se pudo obtener información del activo '{ticker}'. "
            f"Intenta nuevamente más tarde o verifica el ticker."
        )

        # En 'detail' guardamos la lista de lo que falló en cada fuente
        detalle_tecnico = {
            "ticker": ticker,
            "intentos": [e.to_dict() for e in errores]
        }

        super().__init__(
            mensaje_ui,
            code="EXTRACCION_FALLIDA",
            detail=detalle_tecnico
        )
