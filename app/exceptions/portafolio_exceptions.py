from .base.dominio_exception import DominioError


# Excepciones específicas para validaciones de Minimo de Activos en Portafolio
class MinimoActivosError(DominioError):
    """
    Excepción lanzada cuando un portafolio no cumple con el
    número mínimo de activos requerido.

    Regla de negocio:
    - Un portafolio debe contener al menos 20 activos para ser considerado válido.
    """
    def __init__(self, minimo: int = 20, actual: int = 0):
        super().__init__(
            message=(
                f"El portafolio debe contener al menos {minimo} activos. "
                f"Actual: {actual}."
            ),
            code="MINIMO_ACTIVOS_INVALIDO"
        )

        self.minimo = minimo
        self.actual = actual
