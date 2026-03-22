"""
Módulo de excepciones del sistema.

Expone una API pública simplificada para importar excepciones
sin necesidad de conocer la estructura interna del paquete.
"""

# Base
from .base.dominio_exception import DominioError

# Date exceptions
from .date_exceptions import (
    RangoFechasError,
    HorizonteInvalidoError
)

# Text exceptions
from .text_exceptions import (
    TickerInvalidoError,
    ListaTickersVaciaError
)

# Portafolio exceptions
from .portafolio_exceptions import (
    MinimoActivosError
)

# Definición de la API pública del módulo
__all__ = [
    "DominioError",
    "RangoFechasError",
    "HorizonteInvalidoError",
    "TickerInvalidoError",
    "ListaTickersVaciaError",
    "MinimoActivosError"
]

print("Cargando exceptions...")
