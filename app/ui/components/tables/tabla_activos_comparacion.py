"""
Tabla interactiva para selección de activos.
"""

# Librería principal para la construcción de la interfaz web
import streamlit as st
# Herramienta utilizada para manipulación de datos de la UI.
import pandas as pd


def mostrar_tabla_activos_comparacion(
    data: list[dict],
    nombre_portafolio: str
):
    """
    Renderiza una interfaz de selección de activos con límite de concurrencia.
    """

    # Título dinámico para contextualizar al usuario según el portafolio cargado.
    st.subheader(
        f"Activos del Portafolio: {nombre_portafolio}"
    )

    # Si la lista está vacía, evita procesar un DataFrame inexistente.
    if not data:
        st.info(
            "Este portafolio no posee activos."
        )
        return []

    # Mantiene la persistencia de los IDs seleccionados entre los re-renderizados
    if "activos_seleccionados" not in st.session_state:
        st.session_state["activos_seleccionados"] = []

    # Convierte la lista de diccionarios de la BD en un objeto DataFrame.
    df = pd.DataFrame(data)

    # Renombra columnas técnicas a etiquetas amigables para el usuario final.
    df = df.rename(columns={
        "ticker": "Ticker",
        "nombre": "Nombre",
        "tipo_activo": "Tipo",
        "mercado": "Mercado"
    })

    # Activos ya seleccionados
    seleccion_actual = (
        st.session_state["activos_seleccionados"]
    )

    # Marca como True los checkboxes de activos (Persistencia Visual)
    df["Seleccionar"] = df["Ticker"].isin(
        seleccion_actual
    )

    # TABLA INTERACTIVA

    # Se deshabilita la edición en columnas para que solo el checkbox sea clickable.
    edited_df = st.data_editor(
        df,
        key="tabla_activos_comparacion",
        width="stretch",
        height=380,
        column_config={
            "Seleccionar":
                st.column_config.CheckboxColumn(
                    "Seleccionar",
                    help="Seleccione máximo 2 activos",
                    default=False
                )
        },
        disabled=[
            "Ticker",
            "Nombre",
            "Tipo",
            "Mercado"
        ]
    )

    # Recupera la lista de tickers marcados por el usuario.
    seleccionados = edited_df[
        edited_df["Seleccionar"]
    ]["Ticker"].tolist()

    # Guarda la selección válida actual.
    st.session_state[
        "activos_seleccionados"
    ] = seleccionados

    # Entrega la lista de activos para ser procesada por otros módulos.
    return seleccionados
