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
