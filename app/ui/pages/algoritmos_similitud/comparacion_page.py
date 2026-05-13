"""
Página de comparación de activos financieros (HU11 - HU)

Responsabilidades:
- Mostrar portafolios con ETL completado.
- Permitir seleccionar un portafolio.
- Permitir seleccionar exactamente 2 activos.
- Mostrar gráfica de comparativa entre los 2 activos.
- Mostrar resultados de análisis de algoritmos de similitud.
"""

# Librería principal UI
import streamlit as st

# Pandas SOLO en UI
import pandas as pd

import plotly.express as px

# Servicio comparación
from app.services.comparacion.comparacion_service import (
    obtener_series_comparacion
)

# Servicios
from app.services.portafolios.portafolio_service import (
    obtener_portafolios_con_etl,
    obtener_activos_comparacion
)

# Componentes UI
from app.ui.components.tables.tabla_portafolio_comparacion import (
    mostrar_tabla_portafolios_comparacion
)

# Importación del servicio de comparación
from app.ui.components.tables.tabla_activos_comparacion import (
    mostrar_tabla_activos_comparacion
)

# Paneles de información
from app.ui.components.information.distancia_euclidiana_panel import (
    render_euclidean_similarity_panel
)

from app.ui.components.information.correlacion_pearson_panel import (
    render_pearson_similarity_panel
)

from app.ui.components.information.dtw_panel import (
    render_dtw_panel
)

from app.ui.components.information.similitud_coseno_panel import (
    render_cosine_similarity_panel
)

# Feedback visual
from app.ui.components.feedback.alerts import mostrar_error


def render():
    """
    Renderiza la pantalla de comparación de activos financieros.

    Esta función:
    - Muestra el listado de Portafolios que ya realizaron el ETL.
    - Permite la selección de un portafolio para mostrar sus activos.
    - Permite la selección de dos activos para su análisis.
    - Muestra la gráfica de similitud entre los activos seleccionados.
    - Muestra el resumen de los algoritmos analizados.
    """

    # Aplica estilos CSS personalizados
    _inject_algoritmos_css()

    # Encabezado de la página y descripción
    st.markdown(
        """
        ## Comparación de Activos Financieros

        <div class="hero-subtitle">
            Analice similitud y comportamiento histórico entre
            activos financieros utilizando algoritmo de
            series temporales.
        </div>
        """, unsafe_allow_html=True
    )

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

        # Diseño de dos columnas: formulario a la izquierda, información a la derecha
        col_left, col_right = st.columns([2.2, 1])

        # Tabla de Portafolios con ya proceso ETL
        with col_left:

            # Sección Portafolios
            with st.container(border=True):

                # Banner principal de la sección
                st.subheader("📂 Selección de Portafolio")

                # Descripción breve
                st.markdown(
                    """
                    <div class="hero-subsubtitle">
                        Seleccione un portafolio con información enriquecida
                        mediante ETL para visualizar sus activos financieros.
                    </div>
                    """, unsafe_allow_html=True
                )

                id_portafolio, nombre_portafolio = (
                    mostrar_tabla_portafolios_comparacion(data)
                )

        # Panel Lateral de Información
        with col_right:

            # Contenedor de información para recomendaciones
            with st.container(border=True):
                st.subheader("ℹ️ Información")
                st.markdown(
                    """
                    ### Portafolios Disponibles

                    En este módulo únicamente se muestran portafolios
                    que poseen un proceso ETL completado correctamente.

                    #### ¿Cómo habilitar un portafolio?

                    Para que un portafolio aparezca en esta sección:

                    1. Cree un portafolio financiero.
                    2. Diríjase al módulo **Ver Portafolios y ETL**.
                    3. Ejecute el pipeline ETL del portafolio.
                    4. Espere la finalización del procesamiento.
                    """
                )

        # Si existe un portafolio seleccionado
        if id_portafolio:

            # Validaciones de cambio de portafolios
            if (
                "ultimo_portafolio" not in st.session_state
            ):

                st.session_state["ultimo_portafolio"] = None

            # Validación para que no queden guardados los activos seleccionados
            if (
                st.session_state["ultimo_portafolio"]
                != id_portafolio
            ):
                st.session_state["activos_seleccionados"] = []

                st.session_state["ultimo_portafolio"] = id_portafolio

            st.divider()

            # Obtener activos para comparación según portafolio seleccionado
            activos = obtener_activos_comparacion(
                id_portafolio
            )

            # Panel de los Activos del Portafolio
            with st.container(border=True):

                st.subheader("💹 Selección de Activos")

                # Descripción breve
                st.markdown(
                    """
                    <div class="hero-subsubtitle">
                        Seleccione exactamente 2 activos financieros
                        para ejecutar el análisis comparativo.
                    </div>
                    """, unsafe_allow_html=True
                )

                seleccionados = (
                    mostrar_tabla_activos_comparacion(
                        activos,
                        nombre_portafolio
                    )
                )

            # Resumen de Sección
            st.divider()

            total_seleccionados = len(seleccionados)

            # Ningún Activo seleccionado
            if total_seleccionados == 0:

                st.info(
                    """
                    Seleccione dos activos financieros para
                    habilitar el análisis comparativo.
                    """
                )

            # Un solo activo seleccionado
            elif total_seleccionados == 1:

                st.warning(
                    f"""
                    Actualmente solo hay 1 activo seleccionado:

                    • {seleccionados[0]}

                    Debe seleccionar un segundo activo.
                    """
                )

            # Dos Activos seleccionados (Proceso principal)
            elif total_seleccionados == 2:

                activo_1 = seleccionados[0]
                activo_2 = seleccionados[1]

                # Obtener la serie de comparación de los dos activos
                resultados_comparacion = obtener_series_comparacion(
                    id_portafolio,
                    activo_1,
                    activo_2
                )

                # Extraemos los datos obtenidos para las series
                series = resultados_comparacion["series"]

                metricas = resultados_comparacion["metricas"]

                # Convertir a DataFrame para la UI
                df_series = pd.DataFrame(series)

                # Gráfica
                st.subheader(
                    "📈 Comparación de Series Temporales"
                )

                # Descripción breve del proceso
                st.markdown(
                    """
                    <div class="hero-subsubtitle">
                        Las series temporales fueron normalizadas
                        utilizando base 100 para comparar
                        comportamiento relativo y no precios absolutos.
                    </div>
                    """, unsafe_allow_html=True
                )

                # Gráfica de similitud propia jsjs
                with st.container(border=True):

                    fig = px.line(
                        df_series,
                        x="fecha",
                        y=[
                            activo_1,
                            activo_2
                        ],
                        height=500,
                        color_discrete_sequence=[
                            "#3B82F6",
                            "#B300FF"
                        ]
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        hovermode="x unified",
                        legend_title="Activos",
                        xaxis_title="Fecha",
                        yaxis_title="Valor"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                # Separador visual
                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader(
                    "📊 Análisis de Diferentes algoritmos de similitud"
                )

                # MÉTRICAS DE LOS ALGORITMOS
                algoritmo_tab = st.tabs([
                    "Distancia Euclidiana",
                    "Correlación de Pearson",
                    "Dynamic Time Warping",
                    "Similitud por Coseno"

                ])

                # TABS: Distancia Euclidiana
                with algoritmo_tab[0]:

                    render_euclidean_similarity_panel(
                        metricas=metricas,
                        df_series=df_series,
                        activo_1=activo_1,
                        activo_2=activo_2
                    )

                # TABS: Correlación Pearson
                with algoritmo_tab[1]:

                    render_pearson_similarity_panel(
                        metricas=metricas,
                        df_series=df_series,
                        activo_1=activo_1,
                        activo_2=activo_2
                    )

                # TABS: DTW
                with algoritmo_tab[2]:

                    render_dtw_panel(
                        metricas=metricas,
                        df_series=df_series,
                        activo_1=activo_1,
                        activo_2=activo_2
                    )

                # TABS: Coseno
                with algoritmo_tab[3]:

                    render_cosine_similarity_panel(
                        metricas=metricas,
                        df_series=df_series,
                        activo_1=activo_1,
                        activo_2=activo_2
                    )

            # Más de dos activos seleccionados
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


def _inject_algoritmos_css():
    """
    Inyecta estilos personalizados para mejorar la UI.
    """

    st.markdown(
        """
        <style>

        .hero-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }

        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            font-size: 1.35rem;
            color: #A0A0A0;
            margin-bottom: 0.5rem;
        }

        .hero-subsubtitle {
            font-sizeL 1.15rem;
            color: #A0A0A0;
            margin-bottom: 0.5rem;
        }

        .stButton > button {
            border-radius: 10px;
            height: 50px;
            font-weight: 800;
        }

        div[data-testid="stContainer"] {
            border-radius: 16px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
