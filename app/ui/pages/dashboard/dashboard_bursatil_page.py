import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from app.services.dashboard.dashboard_service import (
    construir_matriz_correlacion,
    construir_candlestick,
    calcular_medias_moviles,
    generar_reporte_pdf
)


from app.services.patrones.patrones_service import (
    analizar_patrones_portafolio
)


def render():

    st.markdown(
        """
        ## Dashboard Bursátil


        <div class="hero-subtitle">
            Sistema de análisis cuantitativo que integra correlaciones,
            comportamiento de precios y señales técnicas basadas en medias móviles.
        </div>
        """, unsafe_allow_html=True

    )
    resultados = analizar_patrones_portafolio(1)

    # Separados visual
    st.divider()

    with st.container(border=True):

        # MATRIZ DE CORRELACIÓN
        st.markdown(
            """

            ## 📊 Matriz de Correlación entre Activos

            <div class="hero-subtitle">
                Esta matriz mide la relación estadística entre los retornos de
                los activos.

            - Valores cercanos a **1** → correlación positiva fuerte
            - Valores cercanos a **-1** → correlación negativa fuerte
            - Valores cercanos a **0** → independencia estadística
            </div>
            """, unsafe_allow_html=True
        )

        # Se construye la matriz de correlación
        corr = construir_matriz_correlacion(resultados)

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )

        fig_corr.update_layout(
            title="Mapa de calor de correlación entre activos",
            height=500
        )

        st.plotly_chart(fig_corr, use_container_width=True)

        st.info("""
        Interpretación:
        Este gráfico permite identificar diversificación real del portafolio.
        Activos altamente correlacionados aportan menor reducción de riesgo.
        """)

    # Separados visual
    st.divider()

    with st.container(border=True):

        # SELECCIÓN DE ACTIVO
        tickers = [r["ticker"] for r in resultados]

        selected = st.selectbox(
            "Seleccionar activo para análisis técnico",
            tickers
        )

    # Separador Visual
    st.markdown("<br>", unsafe_allow_html=True)

    activo = next(r for r in resultados if r["ticker"] == selected)

    precios = activo["precios"]
    fechas = activo["fechas"]

    with st.container(border=True):

        # CANDLESTICK + MEDIAS MÓVILES
        st.markdown(
            f"""

            ## 📈 Análisis Técnico - {selected}

            <div class="hero-subtitle">
            El gráfico de velas muestra la evolución del precio en forma OHLC.
            Permite identificar:

            - Tendencias del mercado
            - Volatilidad intradía (simulada)
            - Cambios estructurales en el precio
            </div>
        """, unsafe_allow_html=True
        )

        df_candle = construir_candlestick(precios, fechas)
        df_candle = calcular_medias_moviles(df_candle)

        fig = go.Figure()

        # Velas
        fig.add_trace(go.Candlestick(
            x=df_candle["fecha"],
            open=df_candle["open"],
            high=df_candle["high"],
            low=df_candle["low"],
            close=df_candle["close"],
            name="Precio OHLC"
        ))

        # SMA 10
        fig.add_trace(go.Scatter(
            x=df_candle["fecha"],
            y=df_candle["sma_10"],
            mode="lines",
            name="SMA 10 (corto plazo)",
            line=dict(width=2)
        ))

        # SMA 20
        fig.add_trace(go.Scatter(
            x=df_candle["fecha"],
            y=df_candle["sma_20"],
            mode="lines",
            name="SMA 20 (mediano plazo)",
            line=dict(width=2)
        ))

        fig.update_layout(
            template="plotly_dark",
            height=650,
            xaxis_title="Fecha",
            yaxis_title="Precio",
            legend_title="Indicadores"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info("""
        Interpretación técnica:
        - Cuando SMA 10 cruza por encima de SMA 20 → señal alcista
        - Cuando SMA 10 cruza por debajo de SMA 20 → señal bajista
        - La distancia entre medias indica fuerza de tendencia
        """)

    # EXPORTACIÓN PDF
    with st.container(border=True):

        st.subheader("📄 Reporte Técnico")

        st.markdown("""
        Genera un reporte consolidado con:

        - Matriz de correlación
        - Análisis técnico del activo
        - Medias móviles
        - Resumen estadístico
        """)

        if st.button("Generar y descargar reporte PDF"):

            with st.spinner("Generando reporte técnico..."):

                pdf_buffer = generar_reporte_pdf(
                    resultados=resultados,
                    activo=activo,
                    corr_matrix=corr,
                    df_candle=df_candle
                )

                st.success("Reporte generado correctamente")

                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_buffer,
                    file_name=f"reporte_{activo['ticker']}.pdf",
                    mime="application/pdf"
                )


def _inject_custom_css():
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
            height: 45px;
            font-weight: 600;
        }

        div[data-testid="stContainer"] {
            border-radius: 16px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
