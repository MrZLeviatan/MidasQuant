"""
Objetivos:
- Validar la clasificación de datos (nulos, inválidos, anómalos)
- Validar métricas de calidad
- Validar diagnóstico final
"""

import pytest
# Importación de la función lógica
from app.etl.transform.quality_audit import auditar_calidad_series


# Las fixtures de Pytest permiten crear un entorno de datos controlado y reutilizable.
@pytest.fixture
def dataset_mock():
    # Retorna un diccionario que simula la salida del módulo de alineación.
    return {
        "ACTIVO_LIMPIO": [
            {"fecha": "2024-01-01", "valor": 100},
            {"fecha": "2024-01-02", "valor": 102},
            {"fecha": "2024-01-03", "valor": 101},
        ],

        "ACTIVO_CON_NULOS": [
            {"fecha": "2024-01-01", "valor": 100},
            {"fecha": "2024-01-02", "valor": None},
            {"fecha": "2024-01-03", "valor": None},
        ],

        "ACTIVO_INVALIDO": [
            {"fecha": "2024-01-01", "valor": 100},
            {"fecha": "2024-01-02", "valor": -50},
            {"fecha": "2024-01-03", "valor": 101},
        ],

        "ACTIVO_ANOMALO": [
            {"fecha": "2024-01-01", "valor": 100},
            {"fecha": "2024-01-02", "valor": 200},  # +100%
            {"fecha": "2024-01-03", "valor": 210},
        ],

        "ACTIVO_VACIO": [],

        "ACTIVO_UNICO": [
            {"fecha": "2024-01-01", "valor": 100}
        ]
    }


# Verifica que el diccionario de salida contenga las claves obligatorias requeridas.
def test_estructura_resultado(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)

    assert "ACTIVO_LIMPIO" in resultado
    assert "serie" in resultado["ACTIVO_LIMPIO"]
    assert "calidad" in resultado["ACTIVO_LIMPIO"]
    assert "diagnostico" in resultado["ACTIVO_LIMPIO"]


# Valida que la bandera 'es_nulo' se active correctamente ante valores None.
def test_deteccion_nulos(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    serie = resultado["ACTIVO_CON_NULOS"]["serie"]

    # Generador para contar cuántos elementos fueron marcados como nulos.
    nulos = sum(1 for x in serie if x["es_nulo"])
    assert nulos == 2


# Valida que los precios <= 0 sean marcados como 'es_invalido'.
def test_deteccion_invalidos(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    serie = resultado["ACTIVO_INVALIDO"]["serie"]
    invalidos = sum(1 for x in serie if x["es_invalido"])
    assert invalidos == 1


# Verifica la lógica de variación porcentual para detectar saltos bruscos (anomalías).
def test_deteccion_anomalias(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    serie = resultado["ACTIVO_ANOMALO"]["serie"]
    anomalias = sum(1 for x in serie if x["es_anomalo"])
    assert anomalias == 1


# Comprueba la exactitud de los cálculos estadísticos.
def test_metricas_calidad(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    calidad = resultado["ACTIVO_CON_NULOS"]["calidad"]
    # pytest.approx se usa para evitar errores de precisión de punto flotante
    assert calidad["total_registros"] == 3
    assert calidad["pct_nulos"] == pytest.approx(2 / 3)
    assert calidad["pct_invalidos"] == 0
    assert calidad["pct_anomalias"] == 0


# Verifica que si los nulos superan el 20%, el estado sea DEFICIENTE.
def test_diagnostico_deficiente(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    estado = resultado["ACTIVO_CON_NULOS"]["diagnostico"]["estado_calidad"]
    assert estado == "DEFICIENTE"


# Verifica que si hay anomalías excesivas (>10%), el estado sea RIESGOSO.
def test_diagnostico_riesgoso(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    estado = resultado["ACTIVO_ANOMALO"]["diagnostico"]["estado_calidad"]
    assert estado == "RIESGOSO"


# Asegura que un activo perfecto reciba el diagnóstico ACEPTABLE y métricas en cero.
def test_activo_limpio(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)

    calidad = resultado["ACTIVO_LIMPIO"]["calidad"]
    estado = resultado["ACTIVO_LIMPIO"]["diagnostico"]["estado_calidad"]

    assert calidad["pct_nulos"] == 0
    assert calidad["pct_invalidos"] == 0
    assert calidad["pct_anomalias"] == 0
    assert estado == "ACEPTABLE"


# Control de errores para listas vacías (evita división por cero en el código).
def test_activo_vacio(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)

    calidad = resultado["ACTIVO_VACIO"]["calidad"]

    assert calidad["total_registros"] == 0


# Comprueba que el algoritmo no intente calcular anomalías si no hay un precio previo
def test_activo_unico(dataset_mock):
    resultado = auditar_calidad_series(dataset_mock)
    serie = resultado["ACTIVO_UNICO"]["serie"]
    # all() asegura que CADA elemento de la serie cumpla con no tener anomalías.
    assert all(not x["es_anomalo"] for x in serie)
