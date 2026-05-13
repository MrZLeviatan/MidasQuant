"""
Panel visual del algoritmo de Distancia Euclidiana.
"""

import streamlit as st
import pandas as pd

# Visualización avanzada
import plotly.express as px


def render_euclidean_similarity_panel(
    metricas: dict,
    df_series: pd.DataFrame,
    activo_1: str,
    activo_2: str
):
    """
    Renderiza el dashboard explicativo completo
    del algoritmo de Distancia Euclidiana.
    """

    _inject_euclidean_css()

    valor = metricas["distancia_euclidiana"]

    # Cabecera del dashboard
    st.markdown("""
        ## 📐 Distancia Euclidiana

        <div class="algo-subtitle">
            Este algoritmo mide qué tan similares o diferentes
            son dos activos financieros comparando el comportamiento
            de sus precios a lo largo del tiempo.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Explicación del Algoritmo
    with st.container(border=True):

        st.subheader(
            "🧠 ¿Qué hace este algoritmo?"
        )

        st.markdown(
            f"""
            Imagine que cada activo financiero representa
            una curva en el tiempo.

            El algoritmo de Distancia Euclidiana:

            1. Compara ambas curvas punto por punto.
            2. Calcula la diferencia entre sus valores.
            3. Acumula todas las diferencias.
            4. Genera una distancia matemática final.

            ### Interpretación sencilla

            - Distancia pequeña → Los activos se comportan parecido.
            - Distancia grande → Los activos se comportan diferente.

            En este análisis se comparan las series de tiempo de los activos:

            - **{activo_1}**
            - **{activo_2}**
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas Principales
    st.subheader(
        "📊 Resultado del Análisis"
    )

    col1, col2, col3 = st.columns(3)

    # Distancia
    with col1:

        st.metric(
            "Distancia",
            round(valor, 2)
        )

    # Nivel de similitud
    with col2:

        if valor < 50:

            nivel = "Alta"

        elif valor < 150:

            nivel = "Moderada"

        else:

            nivel = "Baja"

        st.metric(
            "Similitud",
            nivel
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Interpretación mas amigable
    with st.container(border=True):

        st.subheader(
            "🧾 Interpretación del Resultado"
        )

        if valor < 50:

            st.success(
                f"""
                Los activos {activo_1} y {activo_2}
                presentan un comportamiento históricamente
                muy similar.

                Sus movimientos en el tiempo tienden
                a mantenerse cercanos.
                """
            )

        elif valor < 150:

            st.warning(
                """
                Los activos presentan similitud parcial.

                Existen periodos donde ambos activos
                se comportan de forma parecida y otros
                donde divergen.
                """
            )

        else:

            st.error(
                """
                Los activos presentan comportamientos
                considerablemente diferentes.

                Sus movimientos históricos no muestran
                una relación cercana.
                """
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualización gráfica de las métricas
    with st.container(border=True):

        st.subheader(
            "📈 Diferencia entre Activos"
        )

        st.caption(
            """
            La gráfica muestra cuánto se separan los activos
            en cada instante del tiempo.
            """
        )

        diferencias = []

        for _, row in df_series.iterrows():

            diferencia = abs(
                row[activo_1] - row[activo_2]
            )

            diferencias.append({
                "fecha": row["fecha"],
                "Diferencia": diferencia
            })

        df_diff = pd.DataFrame(diferencias)

        fig = px.area(

            df_diff,

            x="fecha",

            y="Diferencia",

            height=400
        )

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            xaxis_title="Fecha",

            yaxis_title="Diferencia",

            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # El paso a paso para el algoritmo
    with st.container(border=True):

        st.subheader(
            "🪜 Paso a Paso del Algoritmo"
        )

        st.markdown(
            """
            ### Paso 1 — Comparar valores

            El algoritmo toma el valor de ambos activos
            en el mismo instante temporal.

            ### Paso 2 — Calcular diferencia

            Se calcula qué tan separados están
            ambos valores.

            ### Paso 3 — Elevar al cuadrado

            Esto evita que diferencias negativas
            cancelen diferencias positivas.

            ### Paso 4 — Sumar diferencias

            Todas las diferencias se acumulan.

            ### Paso 5 — Aplicar raíz cuadrada

            Finalmente se obtiene la distancia total.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Análisis Matemático
    with st.container(border=True):

        st.subheader(
            "📘 Fórmula Matemática"
        )

        st.latex(
            r"d(x,y)=\sqrt{\sum_{i=1}^{n}(x_i-y_i)^2}"
        )

        st.markdown(
            """
            Donde:

            - \(x\) representa valores del primer activo.
            - \(y\) representa valores del segundo activo.
            - \(n\) representa el número de observaciones.
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
            El algoritmo es extremadamente rápido
            porque únicamente necesita recorrer
            la serie temporal una vez.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparación con los otros algoritmos
    with st.container(border=True):

        st.subheader(
            "🔬 Comparación con Otros Algoritmos"
        )

        st.markdown(
            """
            | Algoritmo | ¿Qué analiza? | Ventaja |
            |---|---|---|
            | Distancia Euclidiana | Distancia directa | Muy rápida |
            | Pearson | Correlación estadística | Detecta relación lineal |
            | DTW | Desfase temporal | Flexible |
            | Similitud por Coseno | Ángulo entre series | Detecta dirección similar |
            """
        )

        st.warning(
            """
            La Distancia Euclidiana puede verse afectada
            cuando dos activos tienen comportamientos similares
            pero desplazados temporalmente.
            """
        )


def _inject_euclidean_css():
    """
    Estilos visuales del panel.
    """

    st.markdown("""
    <style>

    .algo-hero {

        background: linear-gradient(
            135deg,
            #0F172A,
            #132B52
        );

        padding: 2rem;

        border-radius: 22px;

        margin-bottom: 1rem;

        border: 1px solid rgba(255,255,255,0.06);
    }

    .algo-title {

        font-size: 2.7rem;

        font-weight: 800;

        color: white;

        margin-bottom: .6rem;
    }

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
