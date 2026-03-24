"""
Módulo de excepciones del sistema.

Expone una API pública simplificada para importar excepciones
sin necesidad de conocer la estructura interna del paquete.
"""

# Base de las excepciones
from app.exceptions.base_exceptions import (
    BDError,
    DominioError,
    FuenteError
)


# Excepciones relacionadas a las reglas del dominio
from app.exceptions.dominio_exceptions import (
    RangoFechasError,
    HorizonteInvalidoError,
    TickerInvalidoError,
    ListaTickersVaciaError,
    MinimoActivosError
)


# Excepciones relacionadas al manejo de la BD
from app.exceptions.database_exceptions import (
    NombreDuplicadoError,
    RecursoNoEncontrado
)

# Excepciones relacionadas a las fuentes de extracción
from app.exceptions.fuentes_exceptions import (
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
    "ExtraccionFallidaError",
    "RecursoNoEncontrado"
]
