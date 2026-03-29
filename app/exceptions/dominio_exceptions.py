# Base de excepciones para errores relacionados a las reglas del dominio
from app.exceptions.base_exceptions import DominioError

from typing import Optional, Any
from datetime import date


class RangoFechasError(DominioError):
    """
    Error cuando la fecha de inicio no es menor que la fecha de fin.

    Regla de negocio:
    - La fecha de inicio debe ser estrictamente menor que la fecha de fin.
    """
    def __init__(self, detail: Optional[Any] = None):
        # Inicializa el error con un mensaje específico y un código de error.
        super().__init__(
            message="La fecha de inicio debe ser menor que la fecha de fin.",
            code="RANGO_FECHAS_INVALIDO",
            detail=detail
        )


class RangoFechaFinError(DominioError):
    """
    Error cuando la fecha de fin sobrepasa la fecha actual.

    Regla de negocio:
    - La fecha fin debe ser menor a la fecha actual
    """
    def __init__(self, fecha_fin: date, detail: Optional[Any] = None):
        # Inicializa el error con un mensaje específico y un código de error.
        super().__init__(
            message=f"La fecha fin ({fecha_fin}) no puede ser mayor a la fecha actual.",
            code="FECHA_FIN_INVALIDA",
            detail=detail
        )


class HorizonteInvalidoError(DominioError):
    """
    Error cuando el rango no cumple el horizonte mínimo requerido.

    Regla de negocio:
    - El rango entre fechas debe ser mayor al horizonte temporal mínimo requerido
        por el sistema (5 años).
    """
    def __init__(self, min_anios: int, diferencia: int):
        detail = {"min_anios_requeridos": min_anios, "diferencia_actual": diferencia}

        super().__init__(
            message=(
                f"El rango de fechas debe ser al menos de {min_anios} años,  "
                f"pero el rango proporcionado es de solo {diferencia} años."
            ),
            code="HORIZONTE_MINIMO_INVALIDO",
            detail=detail
        )


class MinimoActivosError(DominioError):
    """
    Excepción lanzada cuando un portafolio no cumple con el
    número mínimo de activos requerido.

    Regla de negocio:
    - Un portafolio debe contener al menos la cantidad de activos mínimos
        definidos por el sistema (20 activos).
    """
    def __init__(self, minimo: int = 20, actual: int = 0):
        detail = {"minimo_requerido": minimo, "activos_actuales": actual}

        super().__init__(
            message=(
                f"El portafolio debe contener al menos {minimo} activos. "
                f"Actual: {actual}."
            ),
            code="MINIMO_ACTIVOS_INVALIDO",
            detail=detail
        )
        # Guardamos contexto adicional
        self.minimo = minimo
        self.actual = actual


class TickerInvalidoError(DominioError):
    """
    Excepción personalizada para indicar que un ticker es inválido.

    Reglas de validación:
    - Solo caracteres alfanuméricos y caracteres específicos permitidos (ej: guiones).
    - Longitud entre 1 y 12 caracteres.
    """
    def __init__(self, ticker: str, motivo: str):
        detail = {"ticker": ticker, "motivo": motivo}

        super().__init__(
            message=f"Ticker inválido: '{ticker}'. Motivo: {motivo} ",
            code="TICKER_INVALIDO",
            detail=detail
        )
        # Guardamos contexto adicional
        self.ticker = ticker
        self.motivo = motivo
