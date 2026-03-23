"""
Objetivos:
- Validar comportamiento del motor MarketWatch
- Parsing CSV correcto
- Detección de bloqueo (HTML)
- Validación de esquema
"""
# Importar pytest para manejo de pruebas y aserciones
import pytest

from datetime import date

# Se testea directamente el motor interno.
from app.etl.extract.extractor_mercados_publicos import ExtractorFinanciero
from app.exceptions import MarketWatchError

# TESTS


# Test de flujo exitoso del motor
def test_marketwatch_ok(mocker):
    """
    Debe simular la extracción correcta del motor MarketWatch
    """
    # Simula respuesta válida en formato CSV.
    csv_data = """Date,Open,High,Low,Close,Volume
01/01/2023,10,15,5,12,100
"""
    # Intercepta cualquier llamado a `request.get`
    mock_get = mocker.patch("requests.get")
    # Simula respuesta exitosa HTTP
    mock_get.return_value.status_code = 200
    # Simula el cuerpo de la respuesta CSV
    mock_get.return_value.text = csv_data

    # Instancia al extractor real
    extractor = ExtractorFinanciero()
    # Ejecuta el motor directamente.
    datos = extractor._motor_marketwatch("AAPL", date(2023, 1, 1), date(2023, 1, 2))
    # Verifica que parseó correctamente 1 registro.
    assert len(datos) == 1
    assert datos[0]["close"] == 12


# Test de datos corruptos
def test_marketwatch_csv_corrupto(mocker):
    """
    Debe simular la extracción correcta del motor MarketWatch.
    Debe ignorar fila, no romper
    """
    # Simulación de un CSV corrupto
    csv_data = """Date,Open,High,Low,Close,Volume
01/01/2023,10,15,5,INVALID,100
"""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = csv_data

    extractor = ExtractorFinanciero()
    datos = extractor._motor_marketwatch("AAPL", date(2023, 1, 1), date(2023, 1, 2))
    assert len(datos) == 0


# Test de bloqueo por HTML
def test_marketwatch_html(mocker):
    """
    Debe simular la detección de un bloqueo
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    # Simula la respuesta HTML
    mock_get.return_value.text = "<html>blocked</html>"

    extractor = ExtractorFinanciero()
    # Espera la excepción de la fuente
    with pytest.raises(MarketWatchError):
        extractor._motor_marketwatch("AAPL", date(2023, 1, 1), date(2023, 1, 2))


# Test de columnas inválidas
def test_marketwatch_columnas_invalidas(mocker):
    """
    Debe simular la detección de columnas inválidas en el CSV
    """
    # Simula un CSV incompleto
    csv_data = "Date,Open\n01/01/2023,10"

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = csv_data

    extractor = ExtractorFinanciero()

    with pytest.raises(MarketWatchError):
        extractor._motor_marketwatch("AAPL", date(2023, 1, 1), date(2023, 1, 2))


# Test de CSV vacío
def test_marketwatch_vacio(mocker):
    """
    Debe simular la detección de CSV vacío
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = ""

    extractor = ExtractorFinanciero()

    datos = extractor._motor_marketwatch("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert datos == []
