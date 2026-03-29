"""
Define la estructura fundamental de los errores del sistema, actuando como contrato
    para todas las excepciones derivadas.
Su función principal es discriminar el flujo de información:

- Capa de Usuario (UI): Filtra y formatea mensajes amigables y seguros.
- Capa de Observabilidad (Logs): Captura detalles técnicos, trazas de error y
    contexto para depuración.
"""

# Importación para el manejo de tipos en las excepciones
from typing import Any, Optional


class AppError(Exception):
    """
    Clase base para todas las excepciones del sistema.
    Establece el contrato para el manejo de errores propios.
    Se utiliza para errores de UI y Logs.

    _init_: constructor de la clase que recibe un mensaje de error y un código
    super(): llama al constructor de Exception para inicializar

    Atributos:
        - message: Mensaje amigable para UI
        - code: Código interno del error (Define diferencias entre errores)
        - detail: Detalles técnicos para logs (y para el programador xd)
    """
    def __init__(self, message: str, code: str, detail: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict:
        """
        Convierte el error a un diccionario para su uso en UI o logs,
            dependiendo del contexto.
        """
        return {
            "message": self.message,
            "code": self.code,
            "detail": self.detail
        }


class DominioError(AppError):
    """
    Clase base para todos los errores del dominio.
    Permite capturar errores de negocio de forma genérica.
    """
    def __init__(
            self, message: str, code: str = "DOMINIO_ERROR",
            detail: Optional[Any] = None
    ):
        super().__init__(message, code, detail)


class BDError(AppError):
    """
    Clase base para todos los errores de la base de datos.
    Permite capturar errores relacionados a la base de datos.
    """
    def __init__(
            self, message: str, code: str = "DATABASE_ERROR",
            detail: Optional[Any] = None
    ):
        super().__init__(message, code, detail)


class FuenteError(AppError):
    """
    Excepción base para errores en fuentes externas (Extracción de APIs).

    Atributos:
    - fuente (str): Nombre de la fuente
    - etapa (str): Etapa donde ocurrió el error (request, parse, etc.)
    """
    def __init__(
        self,
        fuente: str,
        etapa: str,
        message: str,
        detail: str,
        code: str
    ):
        super().__init__(message, code, detail)
        self.fuente = fuente
        self.etapa = etapa

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "fuente": self.fuente,
            "etapa": self.etapa
        })
        return data
