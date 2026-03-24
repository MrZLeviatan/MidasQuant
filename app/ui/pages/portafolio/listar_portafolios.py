"""
Página para visualizar portafolios registrados.
"""

import streamlit as st

from app.services.portafolio_service import obtener_resumen_portafolios
from app.ui.components.tables.tabla_portafolios import mostrar_tabla_portafolios
from app.ui.components.feedback.alerts import mostrar_error


def render():
    """
    Renderiza la página de listado de portafolios.
    """

    st.header("Listado de Portafolios")

    try:
        # =========================
        # OBTENER DATOS
        # =========================
        data = obtener_resumen_portafolios()

        # =========================
        # MOSTRAR TABLA
        # =========================
        mostrar_tabla_portafolios(data)

    except Exception as e:
        mostrar_error(f"Error al cargar portafolios: {str(e)}")
