"""
Página para visualizar portafolios registrados.
"""

import streamlit as st

# Importación de la capa de servicios (Lógica de negocio y consultas a BD).
from app.services.portafolios.portafolio_service import (
    obtener_resumen_portafolios,
    obtener_activos_de_portafolio
)

# Importación de lógica del proceso ETL
from app.services.etl.etl_service import ETLService

# Importación de componentes de UI (Capa de presentación).
from app.ui.components.tables.tabla_portafolios import mostrar_tabla_portafolios
from app.ui.components.tables.tabla_activos import mostrar_tabla_activos
from app.ui.components.feedback.alerts import mostrar_error


# Función para renderizar la estructura completa de la página.
def render():
    """
    Renderiza la página de listado de portafolios.
    """
    # Define el título principal de la sección en la aplicación.
    st.header("Listado de Portafolios y proceso ETL")

    try:
        # Recupera la lista de portafolios desde la BD
        data = obtener_resumen_portafolios()

        # Renderiza la tabla y captura la selección del usuario
        id_portafolio, nombre_portafolio = mostrar_tabla_portafolios(data)

        # Si el usuario ha seleccionado un portafolio válido:
        if id_portafolio:
            # Recupera los activos (Acciones/ETFs) vinculados a ese ID específico.
            activos = obtener_activos_de_portafolio(id_portafolio)
            # Renderiza la tabla de detalle con los activos y el título dinámico.
            mostrar_tabla_activos(activos, nombre_portafolio)

            # --- CONTROL DEL PROCESO ETL ---
            # Si el portafolio tiene activos, habilitamos la opción de procesamiento.
            if activos:
                # Crea un botón de acción para disparar la lógica de ETL.
                if st.button("Empezar proceso ETL"):
                    try:
                        etl = ETLService()
                        etl.ejecutar_extraccion(id_portafolio)

                        st.success("Extracción Completa")
                        st.rerun()

                    except Exception as e:
                        mostrar_error(str(e))

    except Exception as e:
        # Captura cualquier fallo en la cadena
        mostrar_error(f"Error al cargar portafolios: {str(e)}")
