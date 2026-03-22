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
