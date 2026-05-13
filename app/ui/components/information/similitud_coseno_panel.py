"""
Panel visual del algoritmo de Similitud por Coseno.
"""

import streamlit as st
import pandas as pd

import plotly.express as px


def render_cosine_similarity_panel(
    metricas: dict,
    df_series: pd.DataFrame,
    activo_1: str,
    activo_2: str
):
    """
    Renderiza panel completo de similitud por coseno.
    """

    valor = metricas["similitud_coseno"]["valor"]

    st.markdown("""
    ## 🧭 Similitud por Coseno

    Este algoritmo analiza si ambos activos financieros
    se mueven en la misma dirección general.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Explicación sencilla
    with st.container(border=True):

        st.subheader(
            "🧠 ¿Qué hace este algoritmo?"
        )

        st.markdown(
            f"""
            La similitud por coseno compara la orientación
            entre dos series temporales.

            No analiza distancia exacta.

            Analiza si ambos activos:

            - suben juntos,
            - bajan juntos,
            - o mantienen una dirección similar.

            ### Interpretación simple

            - Valor cercano a 1 → comportamiento muy parecido.
            - Valor cercano a 0 → comportamiento sin relación.
            - Valor cercano a -1 → comportamiento opuesto.

            Activos analizados:

            - **{activo_1}**
            - **{activo_2}**
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas
    st.subheader(
        "📊 Resultado del Análisis"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Similitud Coseno",
            round(valor, 4)
        )

    with c2:

        if valor >= 0.9:

            nivel = "Muy Alta"

        elif valor >= 0.7:

            nivel = "Alta"

        elif valor >= 0.5:

            nivel = "Moderada"

        else:

            nivel = "Baja"

        st.metric(
            "Nivel Relacional",
            nivel
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Interpretación
    with st.container(border=True):

        st.subheader(
            "🧾 Interpretación del Resultado"
        )

        if valor >= 0.9:

            st.success(
                """
                Ambos activos muestran una dirección
                histórica extremadamente similar.
                """
            )

        elif valor >= 0.7:

            st.info(
                """
                Los activos presentan comportamientos
                relativamente alineados.
                """
            )

        elif valor >= 0.5:

            st.warning(
                """
                Existe cierta relación direccional,
                aunque no es completamente consistente.
                """
            )

        else:

            st.error(
                """
                Los activos muestran comportamientos
                bastante diferentes.
                """
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico radial
    with st.container(border=True):

        st.subheader(
            "📈 Visualización Angular"
        )

        st.caption(
            """
            Mientras más cercano esté el valor a 1,
            menor será el ángulo entre ambas series.
            """
        )

        df_gauge = pd.DataFrame({
            "categoria": ["Similitud"],
            "valor": [valor]
        })

        fig = px.bar(
            df_gauge,
            x="categoria",
            y="valor",
            height=400
        )

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            yaxis_range=[-1, 1]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Explicación matemática
    with st.container(border=True):

        st.subheader(
            "📘 Explicación Matemática"
        )

        st.latex(
            r"\text{Similitud}_C = \frac{\sum_{i=1}^{n} x_i y_i}"
            r"{\sqrt{\sum_{i=1}^{n} x_i^2} \sqrt{\sum_{i=1}^{n} y_i^2}}"
        )

        st.markdown(
            """
            Donde:

            - (X x Y) es el producto punto.
            - (X²) es la magnitud del vector X.
            - (Y²) es la magnitud del vector Y.

            El resultado representa qué tan alineados
            están ambos vectores.
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
            El algoritmo únicamente recorre
            las series una vez, por lo que
            es altamente eficiente.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparación
    with st.container(border=True):

        st.subheader(
            "🔬 Diferencia con Otros Algoritmos"
        )

        st.markdown(
            """
            | Algoritmo | Qué analiza |
            |---|---|
            | Euclidiana | Distancia absoluta |
            | Pearson | Correlación lineal |
            | DTW | Desfase temporal |
            | Coseno | Dirección de movimiento |
            """
        )

        st.warning(
            """
            La similitud por coseno puede indicar
            alta relación incluso cuando las magnitudes
            reales de los activos son distintas.
            """
        )
