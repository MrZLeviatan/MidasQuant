class DominioError(Exception):
    """
    Clase base para todos los errores del dominio.
    Permite capturar errores de negocio de forma genérica.

    Atributos:
        _init_: constructor de la clase que recibe un mensaje de error y un código
        super(): llama al constructor de Exception para inicializar
    """
    def __init__(self, message: str, code: str = "DOMINIO_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class BDError(Exception):
    """
    Clase base para todos los errores de la base de datos.
    Permite capturar errores relacionados a la base de datos.

    Atributos:
        _init_: constructor de la clase que recibe un mensaje de error y un código
        super(): llama al constructor de Exception para inicializar
    """
    def __init__(self, message: str, code: str = "BD_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class FuenteError(Exception):
    """
    Clase base para todos los errores de extracción de datos financieros.
    Permite encapsular información estructurada sobre fallos en APIs externas.

    Atributos:
        _init_: constructor de la clase que recibe un mensaje de error y un código
        super(): llama al constructor de Exception para inicializar
    """
    def __init__(self, message: str, code: str = "FUENTE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

    # Implementación para los Logs
    def __str__(self):
        return f"[{self.code}] {self.message}"
