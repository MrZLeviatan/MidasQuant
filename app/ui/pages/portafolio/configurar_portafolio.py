"""
Página de configuración de portafolio (HU04).

Responsabilidades:
- Renderizar el formulario de entrada de datos
- Capturar la interacción del usuario
- Invocar la lógica de negocio (service)
- Manejar errores del dominio
- Mostrar resultados en UI
"""

from datetime import date
import streamlit as st

# Componentes reutilizables de UI
from app.ui.components.feedback.alerts import (
    mostrar_error,
    mostrar_exito,
)

# Componentes reutilizables de formularios
from app.ui.components.forms.form_portafolio import form_portafolio

# Excepciones del dominio
from app.exceptions import AppError

# Lógica de negocio
from app.services.portafolios.portafolio_service import (
    crear_portafolio_completo,
)


def render():
    """
    Punto de entrada principal de la página.

    Esta función:
    - Muestra el formulario
    - Procesa la acción del usuario
    - Llama al backend para crear el portafolio
    - Maneja errores y muestra feedback
    """

    # Aplica estilos CSS personalizados
    _inject_custom_css()

    # Bandera de control para saber si se ah registrado el portafolio
    if "registrado" not in st.session_state:
        st.session_state["registrado"] = False

    # Si ya se ha registrado un portafolio, limpiamos el formulario
    if st.session_state["registrado"]:
        limpiar_formulario()

    # Garantiza que el Session State tenga las claves necesarias
    _asegurar_estado_inicial()

    # Encabezado principal y descripción
    st.markdown(
        """

        ## Gestión de Portafolio

        <div class="hero-subtitle">
            Registre portafolios financieros para análisis cuantitativos y
            comparación de activos.
        </div>
        """, unsafe_allow_html=True
    )

    # Separador visual
    st.divider()

    # Diseño de dos columnas: formulario a la izquierda, información a la derecha
    col_left, col_right = st.columns([2.2, 1])

    # Formulario principal para configurar el portafolio
    with col_left:

        # Contenedor con borde para el formulario
        with st.container(border=True):

            # Título y descripción del formulario
            st.subheader("⚙️ Registro del Portafolio")

            # Descripción breve del formulario
            st.markdown(
                """
                <div class="hero-subsubtitle">
                    Ingrese los datos necesarios para construir el portafolio
                    financiero.
                </div>
                """, unsafe_allow_html=True
            )

            # Separador visual
            st.markdown("<br>", unsafe_allow_html=True)

            # Formulario reutilizable
            nombre, tickers, fecha_inicio, fecha_fin = form_portafolio()

            # Separador Visual
            st.markdown("<br>", unsafe_allow_html=True)

            # BOTONES
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

            # Botón Registro del Portafolio
            with btn_col1:
                btn_registrar = st.button(
                    "Registrar Portafolio",
                    use_container_width=True,
                )

            # Botón LImpiar Formulario
            with btn_col2:
                st.button(
                    "Limpiar Formulario",
                    use_container_width=True,
                    on_click=limpiar_formulario,
                    type="primary"
                )

    # Panel Lateral de Información
    with col_right:

        # Contenedor de información para recomendaciones
        with st.container(border=True):
            st.subheader("ℹ️ Información")
            st.markdown(
                """
                ### Recomendaciones

                - Utilice activos válidos del mercado.
                - Separe los tickers por comas.
                - Evite rangos de fechas pequeños (Mínimo 5 años de diferencia).
                - Verifique que los activos tengan histórico disponible.
                """
            )

        # Separador visual
        st.markdown("<br>", unsafe_allow_html=True)

        # Contenedor de ejemplos para los tickets
        with st.container(border=True):
            st.subheader("📈 Ejemplo")
            st.code(
                "AAPL, MSFT, ECOPETROL, CL=F",
                language="text"
            )
            st.caption(
                "Formato esperado para los activos/tickers financieros."
            )

    # Procesamiento (Control de Eventos)
    if btn_registrar:

        # Validación básica de formulario
        if not st.session_state.nombre.strip():
            mostrar_error(
                "El nombre del portafolio es obligatorio."
            )
            return

        try:
            # Muestra una animación de carga mientras se ejecuta el proceso
            with st.spinner(
                "Validando activos y construyendo portafolio..."
            ):

                # Llama a la capa de servicio (Lógica de Negocio)
                crear_portafolio_completo(
                    nombre_portafolio=nombre,
                    tickers_input=tickers,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin
                )

            # Muestra mensaje de información
            mostrar_exito(
                f"Portafolio '{nombre}' creado correctamente."
            )

            # Cambia el estado para limpiar el formulario.
            st.session_state["registrado"] = True

            # Re carga de pagina
            st.rerun()

        # Manejo de excepciones
        except AppError as e:

            mostrar_error(e.to_dict())

        except Exception as e:

            mostrar_error(
                f"Error crítico del sistema: {str(e)}"
            )


def _asegurar_estado_inicial():
    """
    Inicializa el Session State de la vista.
    """

    keys_defaults = {
        "nombre": "",
        "tickers": "",
        "fecha_inicio": date(2015, 1, 5),
        "fecha_fin": date(2026, 3, 20)
    }

    for key, val in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def limpiar_formulario():
    """
    Limpia los campos del formulario y resetea el estado.
    """

    st.session_state["nombre"] = ""
    st.session_state["tickers"] = ""
    st.session_state["fecha_inicio"] = date(2015, 1, 5)
    st.session_state["fecha_fin"] = date(2026, 3, 20)
    st.session_state["registrado"] = False

    # Limpia selectores adicionales si existieron en el flujo
    if "selector_portafolio" in st.session_state:
        st.session_state["selector_portafolio"] = (
            "Cargar configuración existente..."
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
