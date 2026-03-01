"""
Punto de entrada de la aplicación web basada en Streamlit.

Responsabilidades:
- Configurar la aplicación web.
- Definir el diseño principal.
- Renderizar los componentes iniciales de la interfaz de usuario.
"""

# framework Streamlit, asigna el alias 'st' para llamadas más compactas.
import streamlit as st


# Configura parámetros globales de la aplicación antes de Renderizar.
# - page_title: Define el título de la pestaña del navegador.
# - layout="wide": Permite usar todo el ancho disponible para visualizaciones.
st.set_page_config(
    page_title="Análisis Algorítmico Financiero",
    layout="wide"
)

# Renderizar el encabezado principal de la aplicación.
# Funciona como identificador contextual del sistema.
st.title("Proyecto - Análisis de Algoritmos Financieros")


# Muestra un texto descriptivo debajo del título.
# Proporciona contexto funcional al usuario.
st.write("Sistema de análisis de series de tiempo financieras")
