class BDException(Exception):
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
