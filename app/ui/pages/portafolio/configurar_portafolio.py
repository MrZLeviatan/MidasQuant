"""
Página de configuración de portafolio (HU01).

Responsabilidades:
- Renderizar el formulario de entrada de datos
- Capturar la interacción del usuario
- Invocar la lógica de negocio (service)
- Manejar errores del dominio
- Mostrar resultados en UI
"""

import streamlit as st
from datetime import date

# Componentes reutilizables de UI
from app.ui.components.forms.form_portafolio import form_portafolio
from app.ui.components.alerts import mostrar_error, mostrar_exito

# Lógica de negocio
from app.services.portafolio_service import crear_portafolio_completo

# Excepciones del dominio
from app.exceptions import (
    MinimoActivosError,
    RangoFechasError,
    HorizonteInvalidoError,
    TickerInvalidoError
)


# Punto de entrada de la página
def render():
    """
    Punto de entrada de la página.

    Esta función:
    1. Muestra el formulario
    2. Procesa la acción del usuario
    3. Llama al backend
    4. Maneja resultados o errores
    """

    # ENCABEZADO DE LA PÁGINA
    st.header("Registro de nueva configuración de Portafolio")

    # Limpieza (Debe ir antes del formulario)
    if "registrado" not in st.session_state:
        st.session_state["registrado"] = False

    # Si acabamos de registrar, reseteamos los valores ANTES de mostrar el form
    if st.session_state["registrado"]:
        limpiar_formulario()

    # ASEGURAR EXISTENCIA (Si es la primera vez que carga la app)
    if "nombre" not in st.session_state:
        st.session_state["nombre"] = ""
    if "tickers" not in st.session_state:
        st.session_state["tickers"] = ""
    if "fecha_inicio" not in st.session_state:
        st.session_state["fecha_inicio"] = date(2015, 1, 5)
    if "fecha_fin" not in st.session_state:
        st.session_state["fecha_fin"] = date(2026, 3, 20)
    if "registrado" not in st.session_state:
        st.session_state["registrado"] = False

    """
    Se utiliza un componente reutilizable para capturar los datos.
    Esto evita duplicación de código y mejora mantenibilidad.
    """
    nombre, tickers, fecha_inicio, fecha_fin = form_portafolio()

    """
    El botón controla cuándo se ejecuta la lógica.
    Evita ejecuciones automáticas en cada cambio de input.
    """
    if st.button("Registrar Portafolio"):

        # VALIDACIÓN DE FORMULARIO
        errores = []

        # Validar que el nombre no esté vacío
        if not st.session_state.nombre.strip():
            errores.append("El nombre del portafolio es obligatorio.")

        # Si hay errores, se muestran y se detiene la ejecución
        if errores:
            for e in errores:
                mostrar_error(e)
            # Detiene la ejecución si hay errores
            return

        # Llamada al backend con try/except para manejar errores del dominio
        try:

            # LLAMADA AL BACKEND
            crear_portafolio_completo(
                nombre_portafolio=nombre,
                tickers_input=tickers,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            mostrar_exito("Portafolio creado correctamente")

            # Marcar que ya se registró
            st.session_state["registrado"] = True
            # Rerun para limpiar el formulario
            st.rerun()

        # MANEJO DE ERRORES DEL DOMINIO
        except (MinimoActivosError, RangoFechasError,
                HorizonteInvalidoError, TickerInvalidoError) as e:
            mostrar_error(str(e))

        except Exception as e:
            # Captura cualquier otro error inesperado
            mostrar_error(f"Error inesperado: {str(e)}")


# Limpieza automática del formulario
def limpiar_formulario():
    st.session_state["nombre"] = ""
    st.session_state["tickers"] = ""
    st.session_state["fecha_inicio"] = date(2020, 1, 5)
    st.session_state["fecha_fin"] = date(2026, 3, 20)
    st.session_state["registrado"] = False
