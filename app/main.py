"""
Punto de entrada de la aplicación web basada en Streamlit.

Responsabilidades:
- Configurar la aplicación web.
- Definir el diseño principal.
- Renderizar los componentes iniciales de la interfaz de usuario.
"""

# framework Streamlit, asigna el alias 'st' para llamadas más compactas.
import streamlit as st

# Importar la función para inicializar la base de datos
from app.database.init_db import init_database

from app.ui.pages.portafolio.configurar_portafolio import render as r_config_portafolio
from app.ui.pages.portafolio.listar_portafolios import render as r_listar_portafolios
from app.ui.pages.sorting.benchmark_sorting import render as r_sorting_benchmarking


# Esta función se ejecuta una sola vez y su resultado se almacena en caché para
# reutilizarlo en futuras ejecuciones sin volver a inicializar la base de datos.
@st.cache_resource
def init_db_once():
    init_database()


# Ejecuta la función de Inicialización de la base de datos y guarda en cache.
init_db_once()


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


# NAVEGACIÓN PRINCIPAL ENTRE PÁGINAS

# Diccionario de páginas: clave = nombre visible, valor = función render
paginas = {
    "Inicio": lambda: st.write("Bienvenido al sistema de análisis financiero"),
    "Registro de Portafolio": r_config_portafolio,
    "Ver Portafolios y ETL": r_listar_portafolios,
    "Benchmarking Ordenamiento": r_sorting_benchmarking
    # Futuras páginas se pueden agregar aquí
}

# Selección de página mediante barra lateral
pagina_seleccionada = st.sidebar.radio("Navegación", list(paginas.keys()))

# Renderizar condicional según selección
paginas[pagina_seleccionada]()
