# app/ui/pages/sorting/benchmark_sorting.py

import streamlit as st
import plotly.express as px  # Usamos Plotly para gráficas interactivas profesionales
import pandas as pd         # Para manejar los datos más fácilmente

from app.database.connection import SessionLocal
from app.services.sorting.sorting_service import SortingService


def render():
    """
    Renderiza una interfaz de benchmark
    """
    st.title("📊 Laboratorio de Rendimiento: Algoritmos")
    st.markdown("---")

    db = SessionLocal()
    service = SortingService(db)

    # Botones con iconos y mejor estilo en columnas
    col_btn1, col_btn2 = st.columns(2)
    ejecutar_real = col_btn1.button("Ejecutar Benchmark Real", use_container_width=True)
    ejecutar_controlado = col_btn2.button(
        "Prueba Controlada (800 datos)", use_container_width=True
    )

    resultados = None

    if ejecutar_real:
        with st.spinner("Analizando toda la serie temporal..."):
            resultados = service.ejecutar_benchmark()
    elif ejecutar_controlado:
        with st.spinner("Ejecutando prueba rápida..."):
            data = service.obtener_datos_limitados(800)
            resultados = service.ejecutar_benchmark(data=data)

    if resultados is None:
        st.info("Haz clic en un botón superior para iniciar el análisis comparativo.")
        return

    # Procesamiento de datos con Pandas (Más profesional y rápido)
    df = pd.DataFrame([
        {"Algoritmo": k, "Tiempo (s)": v["tiempo"], "Tamaño": v["tamano"]}
        for k, v in resultados.items() if v["tiempo"] is not None
    ])

    if df.empty:
        st.error("No se obtuvieron resultados válidos durante la ejecución.")
        return

    # Ordenar por tiempo para la gráfica
    df = df.sort_values(by="Tiempo (s)", ascending=True)

    # --- SECCIÓN 1: MÉTRICAS DESTACADAS ---
    st.subheader("🏆 Resultados Destacados")
    m_col1, m_col2, m_col3 = st.columns(3)

    ganador = df.iloc[0]
    lento = df.iloc[-1]

    m_col1.metric(
        label="Más Rápido",
        value=ganador["Algoritmo"],
        delta=f"{ganador['Tiempo (s)']:.4f}s",
        delta_color="normal"
    )

    # Métrica 2: El más lento (Corregido el error de argumentos)
    m_col2.metric(
        label="Más Lento",
        value=lento["Algoritmo"],
        delta=f"{lento['Tiempo (s)']:.4f}s",
        delta_color="inverse"
    )

    m_col3.metric(
        label="📊 Registros",
        value=f"{ganador['Tamaño']:,}"
    )

    # --- SECCIÓN 2: GRÁFICA INTERACTIVA ---
    st.markdown("### 📈 Comparativa Visual de Tiempos")

    # Creamos una gráfica de barras horizontales con gradiente de color
    fig = px.bar(
        df,
        x="Tiempo (s)",
        y="Algoritmo",
        orientation='h',
        text_auto='.4s',
        color="Tiempo (s)",
        color_continuous_scale=px.colors.sequential.Viridis,
        template="plotly_dark"
    )

    fig.update_layout(yaxis={'categoryorder': 'total descending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    # --- SECCIÓN 3: TABLA DETALLADA ---
    with st.expander("📄 Ver Tabla de Datos Crudos"):
        st.dataframe(df, use_container_width=True)

    # --- SECCIÓN 4: ANÁLISIS DE VOLUMEN ---
    st.divider()
    st.subheader("📈 Top 15 Días: Mayor Volumen de Mercado")

    top_15_data = service.obtener_top_15_volumen()
    if top_15_data:
        # Convertimos a DataFrame para estilo profesional
        df_top = pd.DataFrame([
            {
                "Fecha": x.fecha,
                "ID Activo": x.activo_id,
                "Volumen": f"{x.volumen:,.2f}",
                "Cierre ($)": f"{x.close:,.2f}"
            } for x in top_15_data
        ])
        st.table(df_top)
    else:
        st.warning("No se encontraron registros de volumen.")
