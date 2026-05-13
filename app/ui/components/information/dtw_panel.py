"""
Panel visual del algoritmo DTW.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_dtw_panel(
    metricas: dict,
    df_series: pd.DataFrame,
    activo_1: str,
    activo_2: str
):
    """
    Renderiza panel DTW.
    """

    distancia = metricas["dtw"]["distancia"]

    st.markdown("""
    ## 🔄 Dynamic Time Warping (DTW)

    DTW permite comparar series temporales
    aunque sus movimientos ocurran en momentos diferentes.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Qué hace
    with st.container(border=True):

        st.subheader(
            "🧠 ¿Qué hace este algoritmo?"
        )

        st.markdown(f"""
        DTW busca alinear los movimientos históricos
        de los activos financieros (es decir, incluso cuando
        sus movimientos ocurren en momentos diferentes).

        En este análisis se estudian los activos:

        - **{activo_1}**
        - **{activo_2}**

        incluso cuando ocurren con retrasos temporales.

        ### Qué problema intenta resolver DTW?

        Los mercados financieros no siempre reaccionan
        exactamente al mismo tiempo.

        Por ejemplo:

        - Un activo puede subir hoy.
        - Otro activo puede reaccionar 3 días después.
        - Ambos tienen un comportamiento parecido,
            pero desplazado temporalmente.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas
    st.subheader("📊 Resultado del Análisis")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Distancia DTW",
            round(distancia, 2)
        )

    with col2:

        if distancia < 100:

            nivel = "Alta"

        elif distancia < 300:

            nivel = "Moderada"

        else:

            nivel = "Baja"

        st.metric(
            "Similitud",
            nivel
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Interpretación
    with st.container(border=True):

        st.subheader(
            "🧾 Interpretación"
        )

        st.markdown(f"""
        La distancia DTW obtenida fue:

        ## {round(distancia, 2)}

        ### ¿Qué significa esto?

        - Valores pequeños indican que los activos
        poseen trayectorias históricas similares.

        - Valores grandes indican que las trayectorias
        históricas difieren considerablemente.

        ---

        ## 📌 Importante

        A diferencia de otros algoritmos:

        - DTW sí permite desfases temporales.
        - Puede detectar similitud aunque
        los movimientos ocurran en fechas distintas.
        - Es mucho más flexible que la
        Distancia Euclidiana tradicional.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfica
    with st.container(border=True):

        st.subheader(
            "📈 Series Temporales"
        )

        fig = px.line(

            df_series,

            x="fecha",

            y=[
                activo_1,
                activo_2
            ],

            height=500
        )

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)"
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
            r"""
            DTW(i,j)=d(x_i,y_j)+min
            \begin{cases}
            DTW(i-1,j) \\
            DTW(i,j-1) \\
            DTW(i-1,j-1)
            \end{cases}
            """
        )

        st.markdown("""
        DTW construye una matriz de costos mínimos
        para alinear ambas series.
        """)

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
                "O(n²)"
            )

        with c2:

            st.metric(
                "Complejidad Espacial",
                "O(n²)"
            )

        st.warning("""
        DTW es más costoso computacionalmente
        porque analiza múltiples alineaciones posibles.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparación
    with st.container(border=True):

        st.subheader(
            "🔬 Diferencia con Otros Algoritmos"
        )

        st.markdown("""
        | Algoritmo | Ventaja |
        |---|---|
        | Euclidiana | Muy rápida |
        | Pearson | Detecta correlación |
        | DTW | Detecta desfases temporales |
        """)

        st.info("""
        DTW es especialmente útil en mercados donde
        los activos reaccionan con retrasos.
        """)
