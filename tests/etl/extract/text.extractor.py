"""
Objetivos:
- Validar comportamiento de la extracción (Función principal)
- Validación del esquema failover
"""

# Importar pytest para manejo de pruebas y aserciones
import pytest
from datetime import date

# Se testea directamente el motor interno.
from app.etl.extract.extractor_mercados_publicos import ExtractorFinanciero
from app.exceptions import ExtraccionFallidaError


# Test de flujo exitoso aplicando el failover
def test_extractor_ok_failover(mocker):
    # Instancia al extractor real
    extractor = ExtractorFinanciero()
    # Simulación de entrada al motor yahoo
    mocker.patch.object(extractor, "_motor_yahoo", side_effect=Exception())
    # Simulación de entrada al motor stooq
    mocker.patch.object(
        extractor, "_motor_stooq", return_value=[{"fecha": date(2023, 1, 1)}])
    # Simulación de datos de prueba
    datos = extractor.extraer("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert datos


# Test de flujo del extractor donde todas fallan
def test_extractor_falla_total(mocker):
    extractor = ExtractorFinanciero()
    # Simulación de entrada a todos los motores
    mocker.patch.object(extractor, "_motor_yahoo", side_effect=Exception())
    mocker.patch.object(extractor, "_motor_stooq", side_effect=Exception())
    mocker.patch.object(extractor, "_motor_marketwatch", side_effect=Exception())

    # Simulación de excepción en base al fallo de todos los motores
    with pytest.raises(ExtraccionFallidaError):
        extractor.extraer("AAPL", date(2023, 1, 1), date(2023, 1, 2))


# Test de flujo con datos inválidos
def test_extractor_datos_invalidos(mocker):
    extractor = ExtractorFinanciero()

    # Devuelve datos que el validador eliminará
    mocker.patch.object(extractor, "_motor_yahoo", return_value=[
        {
            "fecha": date(2023, 1, 1), "open": 20, "high": 10,
            "low": 5, "close": 12, "volumen": 100
        }
    ])

    with pytest.raises(ExtraccionFallidaError):
        extractor.extraer("AAPL", date(2023, 1, 1), date(2023, 1, 2))
