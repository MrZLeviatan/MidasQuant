"""
Componente que permite la visualización de portafolios.
"""

import streamlit as st
# Librería para la manipulación visual de datos tabulares.
import pandas as pd


def mostrar_tabla_portafolios(data: list[dict]):
    """
    - Función encargada de procesar y renderizar el listado de portafolios.
    - Utiliza tipado (list[dict]) para asegurar la integridad de la entrada.
    - Gestiona la lógica de selección única.

    - Selector de portafolio (click lógico)
    """

    # Valida si la lista viene vacía, muestra mensaje informativo.
    if not data:
        st.info("No hay portafolios registrados")
        # Devolvemos dos valores nulos
        return None, None

    # Inicializa la variable de selección si no existe en la sesión.
    if "portafolio_seleccionado" not in st.session_state:
        st.session_state["portafolio_seleccionado"] = None

    # Convierte la lista en un  diccionarios en un objeto DataFrame (Matriz).
    df = pd.DataFrame(data)

    # Renombre de las columnas para alias amigables para la UI.
    df = df.rename(columns={
        "id": "ID",
        "nombre": "Nombre",
        "fecha_creacion": "Fecha Creación",
        "fecha_inicio": "Fecha Inicio",
        "fecha_fin": "Fecha Fin",
        "etl": "ETL"
    })

    # Visual ETL
    df["ETL"] = df["ETL"].map({
        "Sí": "🟢 Completado",
        "No": "🔴 Pendiente"
    })

    # Crea una columna booleana basada en el ID guardado en sesión.
    df["Seleccionar"] = df["ID"].apply(
        lambda x: x == st.session_state["portafolio_seleccionado"]
    )

    # Renderiza la tabla interactiva
    st.subheader("📂 Portafolios Registrados")
    edited_df = st.data_editor(
        df,
        width="stretch",
        # Altura fija para forzar scroll si hay muchos registros.
        height=250,
        column_config={
            # Configura la columna como checkbox para una interacción de clic simple.
            "Seleccionar": st.column_config.CheckboxColumn("Seleccionar")
        },
        disabled=[
            "ID",
            "Nombre",
            "Fecha Creación",
            "Fecha Inicio",
            "Fecha Fin",
            "ETL"
        ]
    )

    # Extrae únicamente las filas donde el usuario marcó el checkbox
    seleccionados = edited_df[edited_df["Seleccionar"]]
    id_actual = st.session_state["portafolio_seleccionado"]

    # --- CONTROL DE EXCLUSIVIDAD (LÓGICA RADIO BUTTON) ---

    # Si el usuario marca un nuevo portafolio mientras ya había uno seleccionado.
    if len(seleccionados) > 1:
        # Buscamos el ID que sea distinto al que ya teníamos guardado (el nuevo clic).
        nuevo_id = seleccionados[seleccionados["ID"] != id_actual].iloc[0]["ID"]
        st.session_state["portafolio_seleccionado"] = nuevo_id
        # Reinicia para que la tabla se redibuje con un solo check.
        st.rerun()

    # Si solo hay uno seleccionado y es distinto al actual.
    elif len(seleccionados) == 1:
        nuevo_id = seleccionados.iloc[0]["ID"]
        if nuevo_id != id_actual:
            st.session_state["portafolio_seleccionado"] = nuevo_id
            st.rerun()

    # Si el usuario desmarcó el único que estaba seleccionado.
    elif len(seleccionados) == 0 and id_actual is not None:
        st.session_state["portafolio_seleccionado"] = None
        st.rerun()

    # --- BÚSQUEDA DEL NOMBRE ---
    id_final = st.session_state["portafolio_seleccionado"]
    nombre_final = None

    if id_final:
        # Buscamos el nombre correspondiente al ID en nuestro DataFrame
        nombre_final = df.loc[df["ID"] == id_final, "Nombre"].values[0]

    # Devuelve el ID seleccionado para que otros componentes de la app lo utilicen.
    # Devuelve el nombre del Portafolio
    return id_final, nombre_final
