# Importación de la base de las excepciones de la BD.
from app.exceptions.base_exceptions import BDError

# Para el manejo de tipos en las excepciones personalizadas
from typing import Any


class NombreDuplicadoError(BDError):
    """
    Excepción personalizada para indicar que un nombre es duplicado.

    Reglas de validación:
    - El nombre de un Portafolio no puede existir previamente en la base de datos.
    """
    def __init__(self, nombre_portafolio: str):

        # Guardamos el dato en detail para que aparezca en el JSON/Logs automáticamente
        detail = {"nombre_duplicado": nombre_portafolio}

        super().__init__(
            message=f"Ya existe un portafolio con el nombre '{nombre_portafolio}' ",
            code="NOMBRE_DUPLICADO",
            detail=detail
        )
    # Guardamos contexto adicional
        self.nombre_portafolio = nombre_portafolio


class RecursoNoEncontradoError(BDError):
    """
    Excepción personalizada para indicar que un objeto no fue encontrado.

    Reglas de validación:
    - Si se intenta acceder a un recurso mediante su ID y no existe en la bd,
        se lanza esta excepción.
    """
    def __init__(self, recurso: str, id_valor: Any):
        # Guardamos el contexto técnico en detail
        detail = {"recurso": recurso, "id_valor": id_valor}

        super().__init__(
            message=f"No encontrado el recurso '{recurso}' con el ID: {id_valor}",
            code="RECURSO_NO_ENCONTRADO",
            detail=detail
        )
        # Guardamos contexto adicional
        self.recurso = recurso
        self.id_valor = id_valor
