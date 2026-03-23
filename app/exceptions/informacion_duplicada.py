from app.exceptions.base.bd_exception import BDException


# Excepciones específicas para validación de tickers en el servicio de portafolio
class NombreDuplicadoError(BDException):
    """
    Excepción personalizada para indicar que un nombre es duplicado.

    Reglas de validación:
    - El nombre de un Portafolio no puede existir previamente en la base de datos.
    """
    def __init__(self, nombre_portafolio: str):
        super().__init__(
            message=f"Ya existe un portafolio con el nombre '{nombre_portafolio}' ",
            code="NOMBRE_DUPLICADO"
        )
    # Guardamos contexto adicional
        self.nombre_portafolio = nombre_portafolio
