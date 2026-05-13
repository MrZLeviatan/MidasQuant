"""
Componente para visualizar los activos de un portafolio.
"""

# Librería principal para la construcción de la interfaz web.
import streamlit as st
# Herramienta utilizada para manipulación de datos de la UI.
import pandas as pd


# Función que muestra la tabla de activos en base al Portafolio seleccionado
def mostrar_tabla_activos(data: list[dict], nombre_portafolio: str):
    """
    Renderiza la tabla de activos del portafolio seleccionado.
    """
    # Genera un título dinámico que confirma al usuario qué portafolio está consultando.
    st.subheader("📈 Activos del Portafolio: " + nombre_portafolio)

    # Validación básica, si la lista está vacía se detiene la ejecución.
    if not data:
        # Muestra notificación informativa.
        st.info("Este portafolio no tiene activos asociados")
        return

    # Convierte la colección de activos en una matriz de datos (DataFrame).
    df = pd.DataFrame(data)

    # Llenar valores nulos con un placeholder para que la tabla se vea limpia
    df = df.fillna("Buscando...")

    # Limpieza de UI: Sustituye los nombres de las llaves técnicas por etiquetas.
    df = df.rename(columns={
        "ticker": "Ticker",
        "nombre": "Nombre",
        "tipo_activo": "Tipo",
        "mercado": "Mercado"
    })

    # Seleccionamos solo las columnas que queremos mostrar en el orden correcto
    columnas_visibles = ["Ticker", "Nombre", "Tipo", "Mercado"]

    # Renderiza final: Muestra los datos en una tabla interactiva de solo lectura.
    st.dataframe(
        df[columnas_visibles],
        width="stretch",
        height=200
    )
