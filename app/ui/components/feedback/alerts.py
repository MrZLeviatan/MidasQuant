"""
Componente para manejo de mensajes en UI.

Responsabilidad:
- Centralizar mensajes visuales
- Homogeneizar UX
"""

# Importaciones necesarias para el componente
import streamlit as st
import time


# Funciones para mostrar mensajes de error o éxito en la interfaz
def mostrar_error(mensaje: str, segundos: int = 6):
    """
    Muestra un mensaje de error en la interfaz.
    """
    placeholder = st.empty()  # Crear un placeholder para el mensaje
    placeholder.error(mensaje)  # Mostrar el mensaje de error
    time.sleep(segundos)  # Esperar el tiempo especificado
    placeholder.empty()  # Limpiar el mensaje después de mostrarlo


# Función para mostrar mensajes de éxito
def mostrar_exito(mensaje: str, segundos: int = 4):
    """
    Muestra un mensaje de éxito en la interfaz.
    """
    placeholder = st.empty()
    placeholder.success(mensaje)
    time.sleep(segundos)
    placeholder.empty()  # Limpia el mensaje después de los segundos
