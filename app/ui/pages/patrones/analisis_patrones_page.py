"""
Página de análisis de patrones financieros.

Responsabilidades:
- Mostrar portafolios con ETL completado.
- Ejecutar análisis de patrones.
- Visualizar patrones detectados.
- Mostrar sliding windows.
- Explicar comportamiento financiero.
"""

# Librería principal UI
import streamlit as st

# Pandas SOLO UI
import pandas as pd

# Plotly
import plotly.express as px
import plotly.graph_objects as go

# Servicios
from app.services.portafolios.portafolio_service import (
    obtener_portafolios_con_etl
)

from app.services.patrones.patrones_service import (
    analizar_patrones_portafolio
)

# Componentes
from app.ui.components.tables.tabla_portafolio_comparacion import (
    mostrar_tabla_portafolios_comparacion
)

# Feedback
from app.ui.components.feedback.alerts import mostrar_error


def render():
    """
    Renderiza el módulo de análisis de patrones.

    Esta función:
    - Muestra el listado de Portafolios que ya realizaron el ETL.
    - Muestra el análisis de los Patrones.
    - Muestra la explicación de cada Patron.
    """

    _inject_page_css()

    # Encabezado
    st.markdown(
        """
        ## Análisis de Patrones Financieros

        <div class="hero-subtitle">
            Detecte comportamientos repetitivos, tendencias
            y eventos de volatilidad utilizando algoritmos
            basados en Sliding Window.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    try:

        # Obtener portafolios disponibles
        portafolios = obtener_portafolios_con_etl()

        if not portafolios:

            st.warning(
                "No existen portafolios con ETL completado."
            )

            return

        # LAYOUT SUPERIOR
        col_left, col_right = st.columns([2.2, 1])

        # TABLA PORTAFOLIOS
        with col_left:

            with st.container(border=True):

                st.subheader(
                    "📂 Selección de Portafolio"
                )

                st.markdown(
                    """
                    <div class="hero-card-text">
                        Seleccione un portafolio financiero
                        para analizar patrones históricos
                        de comportamiento.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                id_portafolio, nombre_portafolio = (
                    mostrar_tabla_portafolios_comparacion(
                        portafolios
                    )
                )

        # PANEL DERECHO
        with col_right:

            with st.container(border=True):

                st.subheader("ℹ️ Información")

                st.markdown(
                    """
                    ### Algoritmos Implementados

                    Actualmente el sistema detecta:

                    - Días consecutivos al alza.

                    - Periodos de volatilidad alta.

                    #### ¿Qué es Sliding Window?

                    Es una técnica algorítmica que analiza
                    pequeñas ventanas consecutivas de datos
                    para detectar patrones repetitivos.
                    """
                )

        # VALIDAR SELECCIÓN
        if not id_portafolio:
            return

        st.divider()

        zona_resultados = st.empty()

        # Si no hay resultados o cambió el portafolio, ejecutamos
        zona_resultados = st.empty()

        # Solo necesita el placeholder para el spinner
        if (
            "patrones_resultado" not in st.session_state
            or st.session_state.get("patrones_portafolio_id") != id_portafolio
        ):
            with zona_resultados.container():
                with st.spinner(f"Calculando patrones para {nombre_portafolio}..."):
                    resultados_data = analizar_patrones_portafolio(id_portafolio)
                    st.session_state.patrones_resultado = list(resultados_data)
                    st.session_state.patrones_portafolio_id = id_portafolio
            st.rerun()

        # Directo en el flujo, SIN zona_resultados
        render_contenido_completo(st.session_state.patrones_resultado)

    except Exception as e:
        mostrar_error(f"Error en el análisis: {str(e)}")


def render_contenido_completo(resultados):
    """
    Función auxiliar que contiene toda la visualización.
    Solo se llama cuando el proceso ha terminado al 100%.
    """
    st.divider()

    # RESUMEN GENERAL
    st.subheader("📊 Resumen General del Portafolio")

    # Resumen de los patrones al alza
    total_patrones_alza = sum(
        item["analisis_patrones"]["frecuencia_patrones"] for item in resultados
    )
    # Resumen de los patrones de volatilidad
    total_volatilidad = sum(
        item["analisis_volatilidad"]["patrones_detectados"] for item in resultados
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Patrones Alcistas", total_patrones_alza)
    c2.metric("Eventos de Volatilidad", total_volatilidad)

    # Separados visual
    st.markdown("<br>", unsafe_allow_html=True)

    # TABS POR ACTIVO
    nombres_tabs = [item["ticker"] for item in resultados]
    activos_tabs = st.tabs(nombres_tabs)

    for i, activo_tab in enumerate(activos_tabs):
        with activo_tab:
            render_panel_activo(resultados[i])

    st.divider()

    st.subheader("📊 Ranking de Activos por Nivel de Riesgo")

    # ordenar por score
    activos_ordenados = sorted(
        resultados,
        key=lambda x: x.get("risk_score", 0),
        reverse=True
    )

    df_riesgo = pd.DataFrame([
        {
            "Ticker": a["ticker"],
            "Riesgo": a.get("riesgo", "N/A"),
            "Risk Score": a.get("risk_score", 0),
            "Desviación": round(a.get("desviacion_estandar", 0), 4)
        }
        for a in activos_ordenados
    ])

    st.dataframe(
        df_riesgo,
        use_container_width=True
    )


def render_panel_activo(activo: dict):
    """
    Renderiza el dashboard completo de un activo.
    """

    ticker = activo["ticker"]

    precios = activo["precios"]

    fechas = activo["fechas"]

    # Resultados de los patrones
    dias_alza = activo["analisis_patrones"]
    volatilidad = activo["analisis_volatilidad"]
    patron_2 = activo["analisis_reversion"]

    # DATAFRAME UI
    df = pd.DataFrame({
        "fecha": fechas,
        "precio": precios
    })

    # HEADER
    st.markdown(
        f"""
        ### 💹 {ticker}

        <div class="hero-card-text">
            Visualización avanzada de patrones financieros
            detectados algorítmicamente.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # MÉTRICAS PRINCIPALES
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "Datos Analizados",
            len(precios)
        )

    with c2:

        st.metric(
            "Patrones Alcistas",
            dias_alza["frecuencia_patrones"]
        )

    with c3:

        st.metric(
            "Volatilidad Alta",
            volatilidad["patrones_detectados"]
        )

    with c4:

        st.metric(
            "Racha del Alza",
            dias_alza["racha_maxima"]
        )

    with c5:

        st.metric(
            "Riesgo del Activo",
            activo.get("riesgo", "N/A")
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # GRÁFICA PRINCIPAL
    with st.container(border=True):

        st.subheader(
            "📈 Serie Temporal del Activo"
        )

        st.caption(
            """
            Evolución histórica del precio del activo.
            """
        )

        fig = px.line(
            df,
            x="fecha",
            y="precio",
            height=450
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Fecha",
            yaxis_title="Precio"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"serie_{ticker}_{len(precios)}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # TABS DE PATRONES
    tabs_patrones = st.tabs([
        "Días Consecutivos al Alza",
        "Reversión a la Media",
        "Volatilidad Alta",
        "Desviación Estándar"

    ])

    # TAB 1
    with tabs_patrones[0]:

        render_patron_alza(
            dias_alza,
            df,
            ticker
        )

    # TAB 2
    with tabs_patrones[2]:

        render_patron_volatilidad(
            volatilidad,
            df,
            ticker
        )

    with tabs_patrones[1]:
        render_patron_reversion(
            patron_2, df, ticker
        )

    with tabs_patrones[3]:
        st.subheader("📉 Desviación Estándar del Activo")

        st.markdown(
            """
            La desviación estándar mide la dispersión del precio
            respecto a su media.

            Es un indicador clave de riesgo estructural.
            """
        )

        st.metric(
            "σ (Desviación Estándar)",
            round(activo["desviacion_estandar"], 4)
        )

        st.info(
            f"""
            Clasificación del activo: **{activo.get('riesgo', 'N/A')}**
            """
        )


def render_patron_alza(
    patron: dict,
    df: pd.DataFrame,
    ticker: str
):
    """
    Renderiza patrón alcista.
    """

    st.subheader(
        "📈 Días Consecutivos al Alza"
    )

    st.markdown(
        """
        Este algoritmo detecta secuencias consecutivas
        donde el precio del activo aumenta día tras día.

        Esto permite identificar:

        - Tendencias positivas.
        - Momentum financiero.
        - Periodos de crecimiento continuo.
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Patrones Detectados",
            patron["frecuencia_patrones"]
        )

    with c2:

        st.metric(
            "Frecuencia",
            patron["promedio_racha"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):

        st.subheader(
            "🪟 Sliding Window Detectado"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["fecha"],
                y=df["precio"],
                mode="lines",
                name=ticker
            )
        )

        # Pintar ventanas detectadas
        for patron_detectado in patron["patrones"]:

            fig.add_vrect(

                x0=patron_detectado["fecha_inicio"],

                x1=patron_detectado["fecha_fin"],

                opacity=0.25
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True

        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):

        st.subheader(
            "⚙️ Complejidad Computacional"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Temporal",
                "O(n)"
            )

        with c2:

            st.metric(
                "Espacial",
                "O(k)"
            )

        st.info(
            """
            El algoritmo únicamente recorre la serie temporal una vez,
            lo que permite detectar patrones rápidamente incluso en
            grandes volúmenes de datos.
            """
        )


def render_patron_reversion(
    patron: dict,
    df: pd.DataFrame,
    ticker: str
):
    """
    Renderiza el patrón de reversión a la media.

    Detecta cuando el precio se aleja significativamente
    de su media móvil y luego regresa.
    """

    st.subheader("🔁Reversión a la Media")

    st.markdown(
        """
        Este patrón detecta cuando el precio:

        - Se desvía de su valor promedio
        - Y posteriormente regresa a la media

        Es útil para identificar:

        - Correcciones del mercado
        - Zonas de sobrecompra/sobreventa
        - Oscilaciones estructurales
        """
    )

    st.metric(
        "Eventos Detectados",
        patron.get("eventos_detectados", 0)
    )

    with st.container(border=True):

        # Visualización base
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["fecha"],
                y=df["precio"],
                mode="lines",
                name=ticker
            )
        )

        # bandas de reversión si existen
        for evento in patron.get("eventos", []):
            fig.add_vrect(
                x0=evento["inicio"],
                x1=evento["fin"],
                opacity=0.25,
                fillcolor="purple"
            )

        fig.update_layout(
            template="plotly_dark",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    with st.container(border=True):

        st.subheader("⚙️ Complejidad Computacional")

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Temporal",
                "O(n)"
            )

        with c2:
            st.metric(
                "Espacial",
                "O(k)"
            )

        st.info(
            """
            El cálculo de reversión a la media recorre la serie temporal
            una sola vez para estimar desviaciones respecto a la media,
            lo que mantiene eficiencia lineal incluso en grandes volúmenes de datos.
            """
        )


def render_patron_volatilidad(
    patron: dict,
    df: pd.DataFrame,
    ticker: str
):
    """
    Renderiza panel de volatilidad.
    """

    st.subheader(
        "⚠️ Volatilidad Alta Consecutiva"
    )

    st.markdown(
        """
        Este algoritmo detecta periodos donde el activo presenta
        movimientos bruscos consecutivos.

        El objetivo es identificar:

        - Riesgo.
        - Inestabilidad.
        - Eventos extremos.
        - Mercados agresivos.
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Eventos Detectados",
            patron["patrones_detectados"]
        )

    with c2:

        st.metric(
            "Frecuencia",
            patron["frecuencia"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # VOLATILIDAD DIARIA
    volatilidad = []

    for i in range(1, len(df)):

        anterior = df.iloc[i - 1]["precio"]
        actual = df.iloc[i]["precio"]

        if anterior == 0:
            volatilidad.append(0)
            continue

        cambio = (
            abs(actual - anterior)
            / anterior
        ) * 100

        volatilidad.append(cambio)

    df_vol = pd.DataFrame({
        "fecha": df["fecha"][1:],
        "volatilidad": volatilidad
    })

    with st.container(border=True):

        st.subheader(
            "📊 Variación Porcentual Diaria"
        )

        fig = px.bar(
            df_vol,
            x="fecha",
            y="volatilidad",
            height=450
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Fecha",
            yaxis_title="Volatilidad (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):

        st.subheader(
            "🧠 Interpretación Financiera"
        )

        if patron["frecuencia"] == "Alta":

            st.error(
                """
                El activo presenta comportamiento altamente volátil.

                Esto puede representar:

                - Mayor riesgo.
                - Cambios bruscos.
                - Mayor incertidumbre.
                """
            )

        elif patron["frecuencia"] == "Moderada":

            st.warning(
                """
                El activo presenta periodos ocasionales
                de inestabilidad.
                """
            )

        else:

            st.success(
                """
                El activo mantiene un comportamiento
                relativamente estable.
                """
            )


def _inject_page_css():
    """
    Inyecta estilos visuales personalizados.
    """

    st.markdown(
        """
        <style>

        .hero-subtitle {
            font-size: 1.15rem;
            color: #A0A0A0;
            line-height: 1.8;
            margin-bottom: .6rem;
        }

        .hero-card-text {
            font-size: 1rem;
            color: #B8B8B8;
            line-height: 1.8;
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.02);
            padding: 18px;
            border-radius: 16px;
        }

        div[data-testid="stContainer"] {
            border-radius: 18px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
