"""
Responsabilidades:
- Normalizar entrada de tickers
- Limpiar strings ingresados por el usuario
- Garantizar consistencia en identificadores de activos
"""

# Importar excepciones personalizadas para manejo de errores específicos
from app.exceptions import TickerInvalidoError

# Importamos re para validación de formato de tickers
import re


def normalizar_tickers(tickers_input: str) -> list[str]:
    """
    Procesa una cadena de texto con tickers y la convierte en una lista limpia.

    Reglas:
    - Separar por coma
    - Eliminar espacios en blanco
    - Convertir a mayúsculas
    - Eliminar duplicados

    Complejidad: O(n) (por las iteraciones para limpiar y eliminar duplicados)
    """

    # Validar entrada vacía
    if not tickers_input or not tickers_input.strip():
        return []

    # Divide el string por comas para obtener una lista de tickers
    ticker_list = tickers_input.split(",")

    """
    Limpieza y Normalización

    - for ticker in ticker_list: Itera sobre cada ticker en la lista.
    - ticker.strip(): Elimina espacios en blanco al inicio y al final del ticker.
    - ticker.upper(): Convierte el ticker a mayúsculas para estandarizar.
    - if ticker.strip(): Asegura que no se incluyan  vacíos después de eliminar espacios
    """
    tickers_limpios = [
        ticker.strip().upper() for ticker in ticker_list if ticker.strip()
    ]

    """
    Eliminar duplicados manteniendo orden

    - dict.fromkeys(tickers_limpios): Convierte la lista en un diccionario.
    - list(...): Convierte el diccionario de nuevo a una lista, eliminando duplicados
    pero manteniendo el orden original.
    """
    return list(dict.fromkeys(tickers_limpios))


def validar_ticker_formato(ticker: str) -> None:
    """
    Recibe un ticker y verifica si cumple con el formato esperado.

    Reglas:
    - Solo letras, números y caracteres permitidos (puntos, guiones)
    - Longitud razonable (1 a 12 caracteres)

    Complejidad: O(n) (por la iteración en el ticker para la  validación de caracteres)
    """

    # Validar que el ticker no esté vacío
    if not ticker:
        raise TickerInvalidoError(
            ticker="VACÍO", motivo="El ticker no puede estar vacío / blanco"
        )

    # Valida el tamaño del ticker.
    if not (1 <= len(ticker) <= 12):
        raise TickerInvalidoError(
            ticker=ticker,
            motivo=f""""
            Longitud inválida ({len(ticker)}). Debe ser entre 1 y 12 caracteres.
            """
        )

    """
    Usamos Regex para validar letras, números, puntos y guiones.
    - re.match(): Verifica si el ticker coincide con el patrón especificado [A-Z...].
        -r'^[A-Z..]+$': El patrón permite solo letras mayúsculas, números, puntos,
            guiones y signos de igual.
    - ticker.upper(): Convertimos el ticker a mayúsculas para validar.

    """
    if not re.match(r'^[A-Z0-9.\-=]+$', ticker.upper()):
        raise TickerInvalidoError(
            ticker=ticker,
            motivo="""
            Contiene caracteres no permitidos. Use solo letras, números, '.', '-' o '='
            """
        )

    return True
