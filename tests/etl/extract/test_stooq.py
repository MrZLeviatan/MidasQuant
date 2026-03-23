"""
Objetivos:
- Validar comportamiento del motor Stooq
- Parsing CSV correcto
- Validación de esquema
"""

from datetime import date
# Se testea directamente el motor interno.
from app.etl.extract.extractor_mercados_publicos import ExtractorFinanciero

# TESTS


# Test de flujo exitoso del motor
def test_stooq_ok(mocker):
    """
    Debe simular la extracción correcta del motor Stooq
    """
    # Simula respuesta válida en formato CSV.
    csv_data = """Date,Open,High,Low,Close,Volume
2023-01-01,10,15,5,12,100
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
    datos = extractor._motor_stooq("AAPL", date(2023, 1, 1), date(2023, 1, 2))
    # Verifica que parseó correctamente 1 registro.
    assert len(datos) == 1
    assert datos[0]["close"] == 12


# Test de CSV vacío
def test_stooq_vacio(mocker):
    """
    Debe simular la detección de CSV vacío
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = ""

    extractor = ExtractorFinanciero()
    datos = extractor._motor_stooq("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert datos == []


# Test de datos corruptos
def test_stooq_csv_invalido(mocker):
    """
    Debe ignorar fila, no romper
    """
    # Simulación de un CSV en mal formato
    csv_data = "mal formato"

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = csv_data

    extractor = ExtractorFinanciero()

    # no debería romper, solo devolver vacío
    datos = extractor._motor_stooq("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert datos == []
