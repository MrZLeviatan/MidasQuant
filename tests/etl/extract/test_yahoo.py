"""
Objetivos:
- Validar comportamiento del motor Yahoo Finance
- Parsing JSON correcto
- Validación de esquema
"""

# Importar pytest para manejo de pruebas y aserciones
import pytest
from datetime import date

# Se testea directamente el motor interno.
from app.etl.extract.market_data_extractor import ExtractorFinanciero
from app.exceptions import YahooError


# Test de flujo exitoso del motor
def test_yahoo_ok(mocker):
    # Simulación respuesta valida en formato JSON.
    fake_json = {
        "chart": {
            "result": [{
                "timestamp": [1672531200],
                "indicators": {
                    "quote": [{
                        "open": [10],
                        "high": [15],
                        "low": [5],
                        "close": [12],
                        "volume": [100]
                    }]
                }
            }]
        }
    }

    # Intercepta cualquier llamado a `request.get`
    mock_get = mocker.patch("requests.get")
    # Simula respuesta exitosa HTTP
    mock_get.return_value.status_code = 200
    # Simula el cuerpo de la respuesta en JSON
    mock_get.return_value.json.return_value = fake_json

    # Instancia al extractor real
    extractor = ExtractorFinanciero()
    # Ejecuta el motor directamente.
    datos = extractor._motor_yahoo("AAPL", date(2023, 1, 1), date(2023, 1, 2))
    # Verifica que parseó correctamente 1 registro.
    assert len(datos) == 1
    assert datos[0]["close"] == 12


# Test de API caída
def test_yahoo_api_error(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = Exception("API caída")

    extractor = ExtractorFinanciero()

    with pytest.raises(YahooError):
        extractor._motor_yahoo("AAPL", date(2023, 1, 1), date(2023, 1, 2))


# Test de JSON en formato invalido
def test_yahoo_json_invalido(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {}

    extractor = ExtractorFinanciero()
    datos = extractor._motor_yahoo("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert datos == []
