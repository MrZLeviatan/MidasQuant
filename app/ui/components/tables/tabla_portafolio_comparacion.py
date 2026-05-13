"""
Tabla de portafolios para comparación.
"""

import streamlit as st
import pandas as pd


def mostrar_tabla_portafolios_comparacion(data: list[dict]):
    """
    Renderiza una tabla que permite la selección exclusiva de un portafolio.
    """

    # Informa al usuario si el proceso previo (ETL) no ha generado resultados.
    if not data:
        st.info(
            "No existen portafolios con ETL completado."
        )
        return None, None

    # Inicializa la variable que recordará qué portafolio está bajo análisis.
    if "portafolio_comparacion" not in st.session_state:
        st.session_state["portafolio_comparacion"] = None

    # Convertimos la respuesta del servicio en un DataFrame para manipulación ágil
    df = pd.DataFrame(data)

    # Renombrado de cabeceras para eliminar tecnicismos y mejorar la legibilidad.
    df = df.rename(columns={
        "id": "ID",
        "nombre": "Nombre",
        "fecha_creacion": "Fecha Creación",
        "fecha_inicio": "Fecha Inicio",
        "fecha_fin": "Fecha Fin"
    })

    # Compara cada fila con el estado global para pintar el checkbox activo.
    df["Seleccionar"] = df["ID"].apply(
        lambda x:
        x == st.session_state["portafolio_comparacion"]
    )

    st.subheader("Portafolios disponibles")

    # 'data_editor' permite capturar el clic en el checkbox.
    edited_df = st.data_editor(
        df,
        width="stretch",
        height=250,
        column_config={
            "Seleccionar":
                st.column_config.CheckboxColumn(
                    "Seleccionar"
                )
        },
        disabled=[
            "ID",
            "Nombre",
            "Fecha Creación",
            "Fecha Inicio",
            "Fecha Fin"
        ]
    )

    # Identifica qué fila han sido marcadas por el usuario en esta interacción.
    seleccionados = edited_df[
        edited_df["Seleccionar"]
    ]

    id_actual = st.session_state[
        "portafolio_comparacion"
    ]

    # Si el usuario selecciona uno nuevo teniendo ya uno activo, se prioriza el nuevo.
    if len(seleccionados) > 1:
        # Detecta el ID que es diferente al que ya teníamos guardado.
        nuevo_id = seleccionados[
            seleccionados["ID"] != id_actual
        ].iloc[0]["ID"]

        # Recarga la app para limpiar el checkbox anterior visualmente.
        st.session_state[
            "portafolio_comparacion"
        ] = nuevo_id

        st.rerun()

    # Si solo hay uno seleccionado pero es distinto al del estado, actualizamos.
    elif len(seleccionados) == 1:
        nuevo_id = seleccionados.iloc[0]["ID"]
        if nuevo_id != id_actual:
            st.session_state[
                "portafolio_comparacion"
            ] = nuevo_id
            st.rerun()

    # Si el usuario desmarca todo, reseteamos el estado a None.
    elif len(seleccionados) == 0:
        st.session_state[
            "portafolio_comparacion"
        ] = None

    # Recuperamos los valores finales del estado ya procesado.
    id_final = st.session_state[
        "portafolio_comparacion"
    ]

    # Si hay un ID seleccionado, buscamos su nombre para el retorno.
    nombre_final = None

    if id_final:
        nombre_final = df.loc[
            df["ID"] == id_final,
            "Nombre"
        ].values[0]

    # Facilita al llamador tanto el ID (para queries) como el Nombre (para títulos)
    return id_final, nombre_final
