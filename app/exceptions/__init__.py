"""
Módulo de excepciones del sistema.

Expone una API pública simplificada para importar excepciones
sin necesidad de conocer la estructura interna del paquete.
"""

# Base
from app.exceptions.base.dominio_exception import DominioError
from app.exceptions.base.bd_exception import BDError
from app.exceptions.base.fuente_exception import FuenteError


# Date exceptions
from app.exceptions.date_exceptions import (
    RangoFechasError,
    HorizonteInvalidoError
)

# Text exceptions
from app.exceptions.text_exceptions import (
    TickerInvalidoError,
    ListaTickersVaciaError
)

# Portafolio exceptions
from app.exceptions.portafolio_exceptions import (
    MinimoActivosError
)

# Duplicación exceptions
from app.exceptions.informacion_exceptions import (
    NombreDuplicadoError
)

# Fuentes de extracción exceptions
from app.exceptions.extraccion_exceptions import (
    YahooError,
    StooqError,
    MarketWatchError,
    ExtraccionFallidaError
)


# Definición de la API pública del módulo
__all__ = [
    "DominioError",
    "BDError",
    "FuenteError",
    "RangoFechasError",
    "HorizonteInvalidoError",
    "TickerInvalidoError",
    "ListaTickersVaciaError",
    "MinimoActivosError",
    "NombreDuplicadoError",
    "YahooError",
    "StooqError",
    "MarketWatchError",
    "ExtraccionFallidaError"
]
