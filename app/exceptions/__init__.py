"""
Módulo de excepciones del sistema.

Expone una API pública simplificada para importar excepciones
sin necesidad de conocer la estructura interna del paquete.
"""

# Base de las excepciones
from app.exceptions.base_exceptions import (
    AppError,
    BDError,
    DominioError,
    FuenteError
)


# Excepciones relacionadas a las reglas del dominio
from app.exceptions.dominio_exceptions import (
    RangoFechasError,
    RangoFechaFinError,
    HorizonteInvalidoError,
    TickerInvalidoError,
    MinimoActivosError,
    PortafolioSinETLError,
    InsuficientesDatosComunesError,
    ObjetoVacio
)


# Excepciones relacionadas al manejo de la BD
from app.exceptions.database_exceptions import (
    NombreDuplicadoError,
    RecursoNoEncontradoError
)

# Excepciones relacionadas a las fuentes de extracción
from app.exceptions.fuentes_exceptions import (
    YahooError,
    StooqError,
    ExtraccionFallidaError
)


"""
El __all__ ayuda a que cuando alguien haga 'from app.exceptions import *'
    solo importe lo que tú quieres.
"""
__all__ = [
    "AppError",
    "DominioError",
    "BDError",
    "FuenteError",
    "RangoFechasError",
    "HorizonteInvalidoError",
    "TickerInvalidoError",
    "MinimoActivosError",
    "NombreDuplicadoError",
    "YahooError",
    "StooqError",
    "ExtraccionFallidaError",
    "RecursoNoEncontradoError",
    "RangoFechaFinError",
    "PortafolioSinETLError",
    "InsuficientesDatosComunesError",
    "ObjetoVacio"
]
