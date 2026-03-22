"""
Responsabilidades:
- Normalizar entrada de tickers
- Limpiar strings ingresados por el usuario
- Garantizar consistencia en identificadores de activos
"""

from app.exceptions import TickerInvalidoError


# Recibe una cadena de texto, la procesa y devuelve una lista de tickers normalizados.
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
    if not tickers_input:
        return []

    # Divide el string por comas para obtener una lista de tickers
    tickers = tickers_input.split(",")

    """
    Limpieza y Normalización

    - for ticker in tickers: Itera sobre cada ticker en la lista.
    - ticker.strip(): Elimina espacios en blanco al inicio y al final del ticker.
    - ticker.upper(): Convierte el ticker a mayúsculas para estandarizar.
    - if ticker.strip(): Asegura que no se incluyan  vacíos después de eliminar espacios
    """
    tickers_limpios = [ticker.strip().upper() for ticker in tickers if ticker.strip()]

    """
    Eliminar duplicados manteniendo orden

    - dict.fromkeys(tickers_limpios): Convierte la lista en un diccionario.
    - list(...): Convierte el diccionario de nuevo a una lista, eliminando duplicados
    pero manteniendo el orden original.
    """
    tickers_unicos = list(dict.fromkeys(tickers_limpios))

    return tickers_unicos


# Recibe un ticker y verifica si cumple con el formato esperado.
def validar_ticker_formato(ticker: str) -> None:
    """
    Valida el formato básico de un ticker.

    Reglas:
    - Solo letras y números
    - Longitud razonable (1 a 10 caracteres)

    Complejidad: O(n) (por la validación de caracteres)
    """

    # Validar que el ticker no esté vacío
    if not ticker:
        raise TickerInvalidoError(ticker=ticker, motivo="Ticker vacío")

    # Validar que el ticker solo contenga caracteres alfanuméricos
    if not ticker.isalnum():
        raise TickerInvalidoError(ticker=ticker,
                                  motivo="Contiene caracteres no alfanuméricos")

    # Validar la longitud del ticker
    if not (1 <= len(ticker) <= 10):
        raise TickerInvalidoError(ticker=ticker, motivo="Longitud de ticker inválida")

    return True
