import streamlit as st


def render():
    """
    Página de inicio del sistema de análisis financiero algorítmico.
    """

    _inject_css()

    st.markdown(
        """
        # 📊 Sistema de Análisis Algorítmico Financiero

        <div class="hero-subtitle">
            Plataforma diseñada para el análisis cuantitativo de activos financieros
            mediante algoritmos de series temporales, correlación estadística,
            detección de patrones y construcción de métricas de riesgo.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # =========================
    # BLOQUE 1 - PROPÓSITO
    # =========================
    with st.container(border=True):

        st.subheader("🎯 Propósito del Sistema")

        st.markdown(
            """
            Este sistema tiene como objetivo transformar datos financieros en
            información estructurada mediante técnicas algorítmicas.

            Se enfoca en:

            - Análisis de comportamiento histórico de activos
            - Detección de patrones de mercado (trend / volatilidad / reversión)
            - Evaluación cuantitativa de riesgo
            - Comparación estadística entre activos financieros
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # BLOQUE 2 - MÓDULOS
    # =========================
    with st.container(border=True):

        st.subheader("🧠 Módulos Analíticos")

        st.markdown(
            """
            El sistema está compuesto por módulos independientes:

            - 📂 **Gestión de Portafolios**
              - Registro y organización de activos financieros
              - Preparación de datos mediante ETL

            - 📈 **Análisis de Patrones**
              - Sliding Window para detección de tendencias
              - Volatilidad local
              - Reversión a la media

            - 🔬 **Similitud entre Activos**
              - Correlación estadística
              - Distancia entre series temporales

            - 📊 **Dashboard Bursátil**
              - Visualización de correlaciones
              - Candlestick con medias móviles
              - Exportación de reportes técnicos
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # BLOQUE 3 - MODELO ANALÍTICO
    # =========================
    with st.container(border=True):

        st.subheader("⚙️ Enfoque Algorítmico")

        st.markdown(
            """
            El sistema está basado en procesamiento de series temporales:

            - Normalización de datos financieros
            - Cálculo de retornos porcentuales
            - Análisis de ventanas móviles (Sliding Window)
            - Métricas de dispersión y riesgo (desviación estándar)
            - Construcción de scores cuantitativos

            Todo análisis es determinístico y reproducible.
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # BLOQUE 4 - FLUJO DEL SISTEMA
    # =========================
    with st.container(border=True):

        st.subheader("🔄 Flujo del Sistema")

        st.markdown(
            """
            1. Registro de portafolios y activos
            2. Ejecución del proceso ETL
            3. Construcción de series temporales limpias
            4. Aplicación de algoritmos de análisis
            5. Generación de métricas y scores
            6. Visualización en dashboards interactivos
            7. Exportación de reportes técnicos en PDF
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # BLOQUE 5 - ALERTA TÉCNICA
    # =========================
    with st.container(border=True):

        st.subheader("📌 Consideraciones Técnicas")

        st.info(
            """
            El sistema no utiliza predicciones estocásticas ni modelos de IA generativa.

            Todos los resultados se basan en:

            - Cálculos matemáticos explícitos
            - Estadística aplicada
            - Algoritmos determinísticos sobre series temporales
            """
        )


def _inject_css():
    """
    Estilos visuales consistentes con el resto del sistema.
    """

    st.markdown(
        """
        <style>

        .hero-subtitle {
            font-size: 1.15rem;
            color: #A0A0A0;
            line-height: 1.7;
        }

        div[data-testid="stContainer"] {
            border-radius: 16px;
            padding: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
