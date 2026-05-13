"""
Componente de formulario para capturar datos del portafolio.

Responsabilidad:
- Centralizar inputs de usuario
- Reutilizable en crear, editar, etc.
"""
# Importaciones de librerías
import streamlit as st

# Importación de los Tickers quemados
from app.constants.tickers import TICKERS_REALES

# Importación del servicio para obtener portafolios existentes
from app.services.portafolios.portafolio_service import obtener_todos_los_portafolios


def cargar_configuracion_previa():
    """
    Callback para cargar datos del portafolio seleccionado (en el comboBox).
    """
    # Se obtiene el objeto seleccionado del Session State
    seleccion = st.session_state["selector_portafolio"]

    # Si se selecciona un portafolio existente, cargar su configuración
    if seleccion and seleccion != "Seleccionar portafolio existente...":

        # Se actualiza automáticamente los espacios asociados a los 'key'
        st.session_state["tickers"] = seleccion["tickers"]
        st.session_state["fecha_inicio"] = seleccion["fecha_inicio"]
        st.session_state["fecha_fin"] = seleccion["fecha_fin"]


def form_portafolio():
    """
    Renderizar los componentes visuales del formulario para el registro del Portafolio.
    """

    # Nombre del portafolio
    st.text_input(
        "Nombre Único del portafolio",
        placeholder="Ej: Portafolio Tecnológico",
        key="nombre"
    )

    # Fila de autocompletado (Botón + Combobox)
    col_btn, col_combo = st.columns([1.5, 2.5])

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
        key="tickers",
        help="Ingrese los símbolos bursátiles separados por comas."
    )

    # Lógica de Fechas con Restricción de Negocio (5 años mínimo)

    # Input de fecha de inicio
    fecha_inicio = st.date_input(
        "Fecha inicio",
        key="fecha_inicio"
    )

    # Calcular dinámico del límite superior de fecha fin (mínimo 5 años después)
    min_fecha_fin = sumar_5_anios(fecha_inicio)

    # Si no existe en session_state, inicializar
    if "fecha_fin" not in st.session_state:
        st.session_state["fecha_fin"] = min_fecha_fin

    # Validación de consistencia: evita que fecha_fin sea menor al mínimo permitido
    if st.session_state["fecha_fin"] < min_fecha_fin:
        st.session_state["fecha_fin"] = min_fecha_fin

    # Render del input ya consistente
    st.date_input(
        "Fecha fin (mínimo 5 años de diferencia con fecha inicio)",
        min_value=min_fecha_fin,
        key="fecha_fin"
    )

    # Retornamos los valores actuales del state
    return (
        st.session_state["nombre"],
        st.session_state["tickers"],
        st.session_state["fecha_inicio"],
        st.session_state["fecha_fin"]
    )


def sumar_5_anios(fecha):
    """
    Suma 5 años a una fecha dada, manejando casos de años bisiestos.
    - Si la fecha es 29 de febrero, se ajusta a 28 de febrero
    """
    try:
        # Intenta cambiar el año sumándole 5 al actual
        return fecha.replace(year=fecha.year + 5)
    except ValueError:
        # Si la fecha es 29 de febrero, se ajusta a 28 de febrero
        return fecha.replace(month=2, day=28, year=fecha.year + 5)
