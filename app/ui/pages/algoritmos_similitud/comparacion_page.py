"""
Página de comparación de activos financieros.

Responsabilidades:
- Mostrar portafolios con ETL completado.
- Permitir seleccionar un portafolio.
- Permitir seleccionar exactamente 2 activos.
- Preparar la interacción para algoritmos comparativos.
"""

# Librería principal UI
import streamlit as st

# Servicios
from app.services.portafolios.portafolio_service import (
    obtener_portafolios_con_etl,
    obtener_activos_comparacion
)

# Componentes UI
from app.ui.components.tables.tabla_portafolio_comparacion import (
    mostrar_tabla_portafolios_comparacion
)

from app.ui.components.tables.tabla_activos_comparacion import (
    mostrar_tabla_activos_comparacion
)

# Feedback visual
from app.ui.components.feedback.alerts import mostrar_error


def render():
    """
    Renderiza la pantalla de comparación de activos financieros.
    """

    # CONFIGURACIÓN GENERAL
    st.title("📈 Comparación de Similitud de Activos")

    st.markdown("""
    Compare el comportamiento histórico entre dos activos financieros
    pertenecientes a un mismo portafolio utilizando algoritmos de similitud
    de series de tiempo.
    """)

    st.divider()

    # Inicializa el estado para persistir los activos seleccionados
    if "comparacion_activos" not in st.session_state:
        st.session_state.comparacion_activos = []

    # CUERPO PRINCIPAL
    try:

        # OBTENER PORTAFOLIOS
        data = obtener_portafolios_con_etl()

        # Si no hay datos, se guía al usuario sobre cómo generarlos.
        if not data:

            st.warning(
                "⚠️ No existen portafolios con proceso ETL completado."
            )
            st.info(
                """
                Para habilitar el módulo de comparación:

                1. Cree un portafolio.
                2. Ejecute el proceso ETL.
                3. Regrese a esta pantalla.
                """
            )
            return

        # PANEL SUPERIOR DE MÉTRICAS
        total_portafolios = len(data)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Portafolios Disponibles",
                value=total_portafolios
            )

        with col2:
            st.metric(
                label="Estado ETL",
                value="Completado"
            )

        with col3:
            st.metric(
                label="Activos Comparables",
                value="2 Máximo"
            )

        st.divider()

        # SECCIÓN PORTAFOLIOS
        with st.container(border=True):

            st.subheader("📂 Selección de Portafolio")

            st.caption(
                """
                Seleccione un portafolio con información enriquecida
                mediante ETL para visualizar sus activos financieros.
                """
            )

            id_portafolio, nombre_portafolio = (
                mostrar_tabla_portafolios_comparacion(data)
            )

        # SI EXISTE PORTAFOLIO SELECCIONADO
        if id_portafolio:

            st.divider()

            # Obtener activos para comparación según portafolio seleccionado
            activos = obtener_activos_comparacion(
                id_portafolio
            )

            # PANEL DE ACTIVOS
            with st.container(border=True):

                st.subheader("💹 Selección de Activos")

                st.caption(
                    """
                    Seleccione exactamente 2 activos financieros
                    para ejecutar el análisis comparativo.
                    """
                )

                seleccionados = (
                    mostrar_tabla_activos_comparacion(
                        activos,
                        nombre_portafolio
                    )
                )

            # RESUMEN DE SELECCIÓN
            st.divider()

            total_seleccionados = len(seleccionados)

            # ESTADO VACÍO
            if total_seleccionados == 0:

                st.info(
                    """
                    Seleccione dos activos financieros para
                    habilitar el análisis comparativo.
                    """
                )

            # UN SOLO ACTIVO
            elif total_seleccionados == 1:

                st.warning(
                    f"""
                    Actualmente solo hay 1 activo seleccionado:

                    • {seleccionados[0]}

                    Debe seleccionar un segundo activo.
                    """
                )

            # DOS ACTIVOS (CORRECTO)
            elif total_seleccionados == 2:

                activo_1 = seleccionados[0]
                activo_2 = seleccionados[1]

                st.success(
                    f"""
                    Comparación preparada correctamente.

                    Activos seleccionados:
                    • {activo_1}
                    • {activo_2}
                    """
                )

                # TARJETAS VISUALES
                col1, col2 = st.columns(2)

                with col1:

                    with st.container(border=True):

                        st.markdown("### 📊 Activo 1")
                        st.markdown(f"#### {activo_1}")

                        st.caption(
                            "Activo base para análisis comparativo."
                        )

                with col2:

                    with st.container(border=True):

                        st.markdown("### 📊 Activo 2")
                        st.markdown(f"#### {activo_2}")

                        st.caption(
                            "Activo objetivo para análisis comparativo."
                        )

                st.divider()

                # BOTÓN PRINCIPAL
                col_btn1, col_btn2, col_btn3 = st.columns(
                    [1, 2, 1]
                )

                with col_btn2:

                    st.button(
                        "Iniciar Comparación",
                        type="primary",
                        use_container_width=True
                    )

            # MÁS DE DOS
            else:

                st.error(
                    """
                    ❌ Solo se permite seleccionar un máximo
                    de 2 activos financieros.
                    """
                )

    # MANEJO DE ERRORES
    except Exception as e:

        mostrar_error(
            f"Error al cargar el módulo de comparación: {str(e)}"
        )
