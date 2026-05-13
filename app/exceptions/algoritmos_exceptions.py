# Importación de la base de las excepciones de la BD.
from app.exceptions.base_exceptions import AlgoritmoError

# Para el manejo de tipos en las excepciones personalizadas
from typing import Any


class FalloLongitudError(AlgoritmoError):
    """
    Excepción personalizada para indicar que la longitud entre dos
    series es diferente.

    Regla de validación:
    - Las series deben tener exactamente el mismo número de puntos
        para ser comparadas o normalizadas correctamente.
    """
    def __init__(
        self,
        longitud_1: int,
        longitud_2: int,
        detalle_adicional: Any = None
    ):
        # Definimos un mensaje amigable para el usuario
        mensaje_ui = "Las series comparadas no tienen la misma cantidad de datos."

        # Definimos un código de error específico para este caso
        codigo_error = "SERIES_LONGITUD_DESALINEADA"

        # Construimos el detalle técnico para los logs
        datos_tecnicos = {
            "longitud_serie_1": longitud_1,
            "longitud_serie_2": longitud_2,
            "diferencia": abs(longitud_1 - longitud_2),
            "contexto": detalle_adicional
        }

        # Llamamos al constructor de AlgoritmoError
        # Pasamos el nombre del proceso como 'algoritmo'
        super().__init__(
            algoritmo="Alineación de Series Temporales",
            message=mensaje_ui,
            code=codigo_error,
            detail=datos_tecnicos
        )
