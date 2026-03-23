"""
Componente de formulario para capturar datos del portafolio.

Responsabilidad:
- Centralizar inputs de usuario
- Reutilizable en crear, editar, etc.
"""
# Importaciones de librerías
import streamlit as st
from datetime import timedelta

from app.constants.tickers import TICKERS_REALES


# Formulario específico para portafolio
def form_portafolio():
    """
    Renderizar inputs del formulario y retorna los valores.
    Incluye botón para autocompletar 20 tickers.

    Complejidad: O(1) - No depende de la cantidad de datos.
    """

    # Nombre del portafolio
    nombre = st.text_input(
        "Nombre del portafolio",
        placeholder="Ej: Portafolio Tecnológico",
        key="nombre"
    )

    # Botón para autocompletar con 20 tickers reales
    if st.button("Autocompletar con 20 tickers reales"):
        st.session_state.tickers = ", ".join(TICKERS_REALES)
        st.rerun()

    # Tickers de los activos
    tickers = st.text_area(
        "Activos / Tickers (separados por coma, mínimo 20)",
        placeholder="AAPL, MSFT, GOOGL, TSLA...",
        key="tickers"
    )

    # Input de fecha de inicio
    fecha_inicio = st.date_input(
        "Fecha inicio",
        key="fecha_inicio"
    )

    # Input de fecha fin, mínimo permitido: fecha inicio + 5 años
    fecha_fin = st.date_input(
        "Fecha fin (mínimo 5 años de diferencia con fecha inicio)",
        min_value=fecha_inicio + timedelta(days=5 * 366),
        key="fecha_fin"
    )

    # Retornar los valores capturados
    return nombre, tickers, fecha_inicio, fecha_fin
