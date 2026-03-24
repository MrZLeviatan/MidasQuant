"""
Objetivos:
- Validar la validación del formato OHLCV
"""
from datetime import date
# Se testea directamente el motor interno.

from app.etl.extract.market_data_extractor import OHLCVValidador

# TESTS


# Test de flujo exitoso de la validación
def test_validador_valido():
    """
    Debe simular la validación del OHLCV de un dato
    """
    # Simula los datos de entrada de un ticker
    data = [
        {
            "fecha": date(2023, 1, 1), "open": 10,
            "high": 15, "low": 5, "close": 12, "volumen": 100
        }
    ]
    # Ejecuta el motor directamente.
    resultado = OHLCVValidador.validar(data)
    # Verifica la validación correctamente
    assert len(resultado) == 1


# Test de un OHLC invalido
def test_validador_ohlc_invalido():
    data = [
        {
            "fecha": date(2023, 1, 1), "open": 20, "high": 10,
            "low": 5, "close": 12, "volumen": 100
        }
    ]
    resultado = OHLCVValidador.validar(data)
    assert resultado == []


# Test de un OHLCV con volumen negativo
def test_validador_volumen_negativo():
    data = [
        {
            "fecha": date(2023, 1, 1), "open": 10,
            "high": 15, "low": 5, "close": 12, "volumen": -100
        }
    ]
    resultado = OHLCVValidador.validar(data)
    assert resultado == []
