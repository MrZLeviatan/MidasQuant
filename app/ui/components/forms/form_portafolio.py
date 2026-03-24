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

from app.services.portafolios.portafolio_service import obtener_todos_los_portafolios


# Carga los datos del Portafolio seleccionado en el comboBox
def cargar_configuracion_previa():
    """
    Callback para cargar datos del portafolio seleccionado.
    """
    # Se obtiene el objeto seleccionado del Session State
    seleccion = st.session_state["selector_portafolio"]

    # Si se selecciona un portafolio existente, cargar su configuración
    if seleccion and seleccion != "Seleccionar portafolio existente...":

        # Se actualiza automáticamente los espacios asociados a los 'key'
        st.session_state["tickers"] = seleccion["tickers"]
        st.session_state["fecha_inicio"] = seleccion["fecha_inicio"]
        st.session_state["fecha_fin"] = seleccion["fecha_fin"]


# Formulario específico para portafolio
def form_portafolio():
    """
    Renderizar inputs del formulario y retorna los valores.
    Incluye botón para autocompletar 20 tickers.

    Complejidad: O(1) - No depende de la cantidad de datos.
    """

    # Nombre del portafolio
    st.text_input(
        "Nombre Único del portafolio",
        placeholder="Ej: Portafolio Tecnológico",
        key="nombre"
    )

    # Fila de autocompletado (Botón + Combobox)
    col_btn, col_combo = st.columns([1, 2.5])

    # Botón para autocompletar con 20 tickers reales
    with col_btn:
        if st.button("Autocompletar con 20 tickers reales"):
            st.session_state.tickers = ", ".join(TICKERS_REALES)
            st.rerun()

    # ComboBox de los portafolios creados
    with col_combo:
        # Obtener datos de los portafolios en la BD
        opciones = obtener_todos_los_portafolios()

        # Formatear el texto para mostrar: "Nombre (Creado: YYYY-MM-DD)"
        st.selectbox(
            "Cargar configuración existente:",
            # Formato del comboBox
            options=["Cargar configuración existente..."] + opciones,
            format_func=lambda x: f"{x['nombre']} ({x['fecha_creacion']})"
            if isinstance(x, dict) else x,
            key="selector_portafolio",
            # Dispara la lógica de autorelleno
            on_change=cargar_configuracion_previa,
            # Quita el Titulo visual
            label_visibility="collapsed"
        )

    # Tickers de los activos
    st.text_area(
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
    st.date_input(
        "Fecha fin (mínimo 5 años de diferencia con fecha inicio)",
        # Calculamos el mínimo para la fecha fin dinámicamente
        min_value=fecha_inicio + timedelta(days=5 * 366),
        key="fecha_fin"
    )

    # Retornamos los valores actuales del state
    return (
        st.session_state["nombre"],
        st.session_state["tickers"],
        st.session_state["fecha_inicio"],
        st.session_state["fecha_fin"]
    )
