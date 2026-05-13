import pandas as pd


from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io

import matplotlib.pyplot as plt
import seaborn as sns


def construir_matriz_correlacion(resultados: list[dict]) -> pd.DataFrame:
    """
    Construye matriz de correlación alineando por fechas.

    Complejidad: O(n) - itera una vez
    """

    series = []

    # Itera sobre el diccionario
    for activo in resultados:

        ticker = activo["ticker"]
        precios = activo["precios"]
        fechas = activo["fechas"]

        df = pd.DataFrame({
            "fecha": fechas,
            ticker: precios
        })

        df = df.set_index("fecha")

        # retorno porcentual (mejor base estadística)
        df = df.pct_change()

        series.append(df)

    # alineación por fecha (outer join automático)
    df_merged = pd.concat(series, axis=1)

    # limpieza
    df_merged = df_merged.dropna()

    return df_merged.corr()


def construir_candlestick(precios: list, fechas: list) -> pd.DataFrame:
    """
    Genera OHLC sintético desde precios.
    """

    df = []

    # Tamaño de la ventana para simular un periodo
    window = 5

    # Desplazamiento por la serie de precios para agrupar bloques de datos.
    for i in range(window, len(precios)):

        chunk = precios[i - window:i]

        df.append({
            "fecha": fechas[i],
            "open": chunk[0],
            "high": max(chunk),
            "low": min(chunk),
            "close": precios[i]
        })

    return pd.DataFrame(df)


def calcular_medias_moviles(df: pd.DataFrame):
    """
    Calcula SMA 10 y SMA 20.
    Aplicar indicadores de tendencia
    """

    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["sma_20"] = df["close"].rolling(window=20).mean()

    return df


def generar_reporte_pdf(resultados, activo, corr_matrix, df_candle):
    """
    Genera reporte técnico financiero en PDF.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Portada
    title = Paragraph("📊 REPORTE TÉCNICO DE ANÁLISIS FINANCIERO", styles["Title"])
    subtitle = Paragraph(f"Activo analizado: {activo['ticker']}", styles["Heading2"])

    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # Resumen Ejecutivo
    resumen = Paragraph(
        "Este reporte consolida análisis de correlación, tendencias "
        "y comportamiento técnico basado en medias móviles y velas japonesas.",
        styles["BodyText"]
    )

    elements.append(resumen)
    elements.append(Spacer(1, 15))

    # MATRIZ DE CORRELACIÓN (imagen)
    corr_img_path = "/tmp/corr.png"
    guardar_heatmap_correlacion(corr_matrix, corr_img_path)

    elements.append(Paragraph("Matriz de Correlación", styles["Heading3"]))
    elements.append(Image(corr_img_path, width=400, height=300))
    elements.append(Spacer(1, 20))

    # CANDLESTICK (imagen plotly exportada)
    candle_path = "/tmp/candle.png"
    guardar_candlestick(df_candle, candle_path)

    elements.append(Paragraph("Análisis Técnico (Candlestick)", styles["Heading3"]))
    elements.append(Image(candle_path, width=450, height=300))
    elements.append(Spacer(1, 20))

    # MÉTRICAS
    data = [
        ["Ticker", activo["ticker"]],
        ["Tipo", activo.get("tipo_activo", "")],
        ["Mercado", activo.get("mercado", "")],
        ["Riesgo", activo.get("riesgo", "N/A")],
        ["Score", activo.get("risk_score", 0)],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)

    # BUILD
    doc.build(elements)

    buffer.seek(0)
    return buffer


def guardar_heatmap_correlacion(corr_matrix, path):
    plt.figure(figsize=(8, 6))

    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0
    )

    plt.title("Matriz de Correlación")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def guardar_candlestick(df_candle, path):
    """
    Genera candlestick simplificado en matplotlib.
    """

    plt.figure(figsize=(10, 4))

    plt.plot(df_candle["fecha"], df_candle["close"], label="Close", linewidth=1.5)

    plt.plot(df_candle["fecha"], df_candle["sma_10"], label="SMA 10")
    plt.plot(df_candle["fecha"], df_candle["sma_20"], label="SMA 20")

    plt.title("Análisis Técnico - Candlestick (Simplificado)")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")

    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
