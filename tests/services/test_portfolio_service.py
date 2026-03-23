"""
Objetivos:
- Validar creación correcta de portafolios
- Validar reglas de negocio
- Detectar errores esperados
"""
# Importar pytest para manejo de pruebas y aserciones
import pytest

from datetime import date

# Importar la función a probar
from app.services.portafolio_service import crear_portafolio_completo

from app.exceptions import (
    MinimoActivosError,
    RangoFechasError,
    HorizonteInvalidoError,
    TickerInvalidoError
)


# DATOS DE PRUEBA

# Función auxiliar para generar tickers válidos
def generar_tickers_validos(n=20):
    """
    Genera una lista de tickers válidos.

    - [f"ACT{i}" for i in range(n)] genera una lista de strings como ACT0, ACT1
    - range(n) itera desde 0 hasta n-1, creando n tickers
    - join los une en un solo string separado por comas

    Complejidad: O(n)
    """
    return ", ".join([f"ACT{i}" for i in range(n)])


# TESTS

# Test de creación exitosa con validación de reglas de negocio
def test_creacion_portafolio_valido(db_session):
    """
    Debe crear correctamente un portafolio con datos válidos.
    """
    # Crear un portafolio con 20 activos y rango de fechas válido
    resultado = crear_portafolio_completo(
        nombre_portafolio="Portafolio Test",
        tickers_input=generar_tickers_validos(20),
        fecha_inicio=date(2015, 1, 1),
        fecha_fin=date(2021, 1, 1),
        db=db_session
    )
    # Validar que el resultado tenga la estructura esperada
    assert resultado["nombre"] == "Portafolio Test"
    # Validar que se hayan creado 20 activos
    assert len(resultado["activos"]) == 20


# Test de errores por incumplimiento de reglas de negocio (minimo activos)
def test_error_menos_de_20_activos():
    """
    Debe fallar si hay menos de 20 activos.
    """

    # Intentar crear un portafolio con solo 10 activos
    with pytest.raises(MinimoActivosError):
        crear_portafolio_completo(
            nombre_portafolio="Error Test",
            tickers_input=generar_tickers_validos(10),
            fecha_inicio=date(2015, 1, 1),
            fecha_fin=date(2021, 1, 1),
        )


# Test de errores por incumplimiento de reglas de negocio (fechas inválidas)
def test_error_fechas_invalidas():
    """
    Debe fallar si la fecha inicio es mayor o igual a la final.
    """

    # Intentar crear un portafolio con fecha inicio mayor a fecha fin
    with pytest.raises(RangoFechasError):
        crear_portafolio_completo(
            nombre_portafolio="Error Fecha",
            tickers_input=generar_tickers_validos(20),
            fecha_inicio=date(2022, 1, 1),
            fecha_fin=date(2020, 1, 1)
        )


# Test de errores por incumplimiento de reglas de negocio (horizonte menor a 5 años)
def test_error_horizonte_menor_5_anios():
    """
    Debe fallar si el rango es menor a 5 años.
    """

    # Intentar crear un portafolio con un rango de fechas de solo 2 años
    with pytest.raises(HorizonteInvalidoError):
        crear_portafolio_completo(
            nombre_portafolio="Error Horizonte",
            tickers_input=generar_tickers_validos(20),
            fecha_inicio=date(2020, 1, 1),
            fecha_fin=date(2022, 1, 1),
        )


# Test de errores por incumplimiento de reglas de negocio (ticker con formato inválido)
def test_error_ticker_invalido():
    """
    Debe fallar si se incluye un ticker con formato inválido.
    """

    ticker_validos = generar_tickers_validos(19)
    ticker_input = ticker_validos + ", $$$"

    # Intentar crear un portafolio con un ticker invalido
    with pytest.raises(TickerInvalidoError):
        crear_portafolio_completo(
            nombre_portafolio="Error Ticker",
            tickers_input=ticker_input,
            fecha_inicio=date(2015, 1, 1),
            fecha_fin=date(2021, 1, 1),
        )
