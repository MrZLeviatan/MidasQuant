from .base.dominio_exception import DominioError


# Excepciones específicas para validación de tickers en el servicio de portafolio
class TickerInvalidoError(DominioError):
    """
    Excepción personalizada para indicar que un ticker es inválido.

    Reglas de validación:
    - Solo caracteres alfanuméricos.
    - Longitud entre 1 y 10 caracteres.
    """
    def __init__(self, ticker: str, motivo: str):
        super().__init__(
            message=f"Ticker inválido: '{ticker}'. Motivo: {motivo} ",
            code="TICKER_INVALIDO"
        )
    # Guardamos contexto adicional
        self.ticker = ticker
        self.motivo = motivo


# Excepción para indicar que la lista de tickers se encuentra vacía
class ListaTickersVaciaError(DominioError):
    """
    Excepción lanzada cuando la lista de tickers está vacía en un contexto
    donde se requiere al menos un valor.
    """
    def __init__(self):
        super().__init__(
            message="La lista de tickers no puede estar vacía.",
            code="LISTA_TICKERS_VACIA"
        )
