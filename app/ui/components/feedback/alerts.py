"""
Componente para manejo de mensajes en UI.

Responsabilidad:
- Centralizar mensajes visuales
- Homogeneizar UX
"""

import streamlit as st
# Se importa el time para manejos de temporización de mensajes
import time


def mostrar_error(mensaje_o_error: str | dict, segundos: int = 8):
    """
    Muestra un error en la UI.
    Si recibe un dict (de AppError), formatea el mensaje y los detalles técnicos.
    """
    # Creamos un contenedor vacío para poder borrarlo después
    placeholder = st.empty()

    if isinstance(mensaje_o_error, dict):
        # Extraemos la info de nuestro formato estándar
        msg = mensaje_o_error.get("message", "Error desconocido")
        code = mensaje_o_error.get("code", "ERROR")
        detail = mensaje_o_error.get("detail", "")

        # Agrupamos los elementos visuales dentro del placeholder
        with placeholder.container():
            st.error(f"**{code}:** {msg}")
            # Si hay detalles técnicos (ej. un stacktrace), se ocultan en un expander
            if detail:
                with st.expander("Ver detalles técnicos"):
                    st.json(detail)
    else:
        # Si es solo un texto, usamos el formato estándar de error de Streamlit
        placeholder.error(mensaje_o_error)
    # Pausa la ejecución para que el usuario pueda leer
    time.sleep(segundos)
    # Elimina el contenido del contenedor, limpiando la UI
    placeholder.empty()


def mostrar_exito(mensaje: str, segundos: int = 4):
    """
    Muestra un mensaje de éxito en la interfaz.
    """
    placeholder = st.empty()
    placeholder.success(mensaje)
    time.sleep(segundos)
    # Limpia el mensaje después de los segundos
    placeholder.empty()
