"""
Panel visual del algoritmo
de Correlación de Pearson.
"""

import streamlit as st
import pandas as pd

import plotly.express as px


def render_pearson_similarity_panel(
    metricas: dict,
    df_series: pd.DataFrame,
    activo_1: str,
    activo_2: str
):
    """
    Renderiza dashboard visual completo
    del algoritmo de Pearson.
    """

    _inject_pearson_css()

    correlacion = metricas["correlacion_pearson"]

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown("""
        ## 📊 Correlación de Pearson

        <div class="algo-subtitle">
            Este algoritmo mide qué tan relacionados
            están dos activos financieros.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Explicación del algoritmo
    with st.container(border=True):

        st.subheader(
            "🧠 ¿Qué hace este algoritmo?"
        )

        st.markdown(
            f"""
            La Correlación de Pearson analiza
            si dos activos financieros tienden
            a moverse juntos.

            ### Interpretación sencilla

            - Pearson ≈ 1 → ambos suben y bajan juntos.
            - Pearson ≈ 0 → no existe relación clara.
            - Pearson ≈ -1 → se mueven en direcciones opuestas.

            EN este análisis se comparan las series de tiempo de los activos:

            - **{activo_1}**
            - **{activo_2}**
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas Principales
    st.subheader(
        "📊 Resultado del Análisis"
    )

    c1, c2, c3 = st.columns(3)

    # Correlación entra ambos
    with c1:

        st.metric(
            "Correlación",
            round(correlacion, 4)
        )

    # CLasificación de correlación
    with c2:

        if correlacion >= 0.7:

            nivel = "Muy Alta"

        elif correlacion >= 0.4:

            nivel = "Moderada"

        elif correlacion >= 0:

            nivel = "Débil"

        else:

            nivel = "Negativa"

        st.metric(
            "Relación",
            nivel
        )

    # Si van de la mano
    with c3:

        direccion = (
            "Positiva"
            if correlacion >= 0
            else "Negativa"
        )

        st.metric(
            "Dirección",
            direccion
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Interpretación mas amigable
    with st.container(border=True):

        st.subheader(
            "🧾 Interpretación"
        )

        if correlacion >= 0.7:

            st.success(
                """
                Los activos muestran una relación
                muy fuerte.

                Históricamente tienden a moverse
                en la misma dirección.
                """
            )

        elif correlacion >= 0.4:

            st.warning(
                """
                Los activos presentan relación parcial.

                Existen periodos donde se mueven
                de forma similar.
                """
            )

        elif correlacion >= 0:

            st.info(
                """
                La relación entre activos es débil.
                """
            )

        else:

            st.error(
                """
                Los activos presentan relación inversa.

                Cuando uno sube,
                el otro tiende a bajar.
                """
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualización gráfica de las métricas
    with st.container(border=True):

        st.subheader(
            "📈 Dispersión Estadística"
        )

        st.caption(
            """
            Cada punto representa una relación
            entre ambos activos.
            """
        )

        fig = px.scatter(

            df_series,

            x=activo_1,

            y=activo_2,

            height=500
        )

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            xaxis_title=activo_1,

            yaxis_title=activo_2
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # PASO A PASO
    with st.container(border=True):

        st.subheader(
            "🪜 Paso a Paso del Algoritmo"
        )

        st.markdown(
            """
            ### Paso 1 — Calcular promedios

            El algoritmo obtiene el promedio
            de cada serie temporal.

            ### Paso 2 — Comparar desviaciones

            Analiza cuánto se alejan los valores
            respecto a sus promedios.

            ### Paso 3 — Detectar relación

            Evalúa si ambas series aumentan
            o disminuyen juntas.

            ### Paso 4 — Normalizar resultado

            El resultado final queda entre -1 y 1.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Análisis Matemático
    with st.container(border=True):

        st.subheader(
            "📘 Fórmula Matemática"
        )

        st.latex(
            r"r = \frac{\sum (x_i-\bar{x})(y_i-\bar{y})}"
            r"{\sqrt{\sum(x_i-\bar{x})^2}\sqrt{\sum(y_i-\bar{y})^2}}"
        )

        st.markdown(
            """
            Donde:

            - (x) y (y) son las series.
            - (\u0304 x) y (\u0304y) son promedios.
            - (r) representa la correlación final.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Complejidad
    with st.container(border=True):

        st.subheader(
            "⚙️ Complejidad Computacional"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Complejidad Temporal",
                "O(n)"
            )

        with c2:

            st.metric(
                "Complejidad Espacial",
                "O(1)"
            )

        st.info(
            """
            Pearson es eficiente y adecuado
            para grandes volúmenes de datos financieros.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Diferencias
    with st.container(border=True):

        st.subheader(
            "🔬 Diferencia con Otros Algoritmos"
        )

        st.markdown(
            """
            | Algoritmo | Qué analiza |
            |---|---|
            | Pearson | Relación estadística |
            | Euclidiana | Distancia directa |
            | DTW | Desfase temporal |
            | Coseno | Dirección vectorial |
            """
        )

        st.warning(
            """
            Pearson detecta relación estadística,
            no similitud exacta de magnitudes.
            """
        )


def _inject_pearson_css():

    st.markdown("""
    <style>

    .algo-subtitle {

        color: #CBD5E1;

        font-size: 1.08rem;

        line-height: 1.8;
    }

    div[data-testid="stMetric"] {

        background: rgba(255,255,255,0.02);

        padding: 16px;

        border-radius: 16px;
    }

    div[data-testid="stContainer"] {

        border-radius: 18px;
    }

    </style>
    """, unsafe_allow_html=True)
