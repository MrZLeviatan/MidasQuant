import streamlit as st
import time

# Importaciones de servicios y UI
from app.services.portafolios.portafolio_service import (
    obtener_resumen_portafolios,
    obtener_activos_de_portafolio
)

# Importación de la lógica del Backend
from app.services.etl.etl_service import ETLService

# Importación de componentes para la UI
from app.ui.components.tables.tabla_portafolios import mostrar_tabla_portafolios
from app.ui.components.tables.tabla_activos import mostrar_tabla_activos
from app.ui.components.feedback.alerts import mostrar_error


def render():
    """
    Renderiza la pantalla.
    """
    st.header("Listado de Portafolios y Proceso ETL")

    # Inicialización de Session State (Banderazos)
    if "etl_corriendo" not in st.session_state:
        st.session_state.etl_corriendo = False
    if "mensajes_exito" not in st.session_state:
        st.session_state.mensajes_exito = []
    if "mensajes_error" not in st.session_state:
        st.session_state.mensajes_error = []
    if "resumen_final" not in st.session_state:
        st.session_state.resumen_final = None

    try:
        # Se obtienes los datos de los Portafolios para las tablas
        data = obtener_resumen_portafolios()
        # La tabla devuelve el ID y nombre seleccionado por el usuario.
        id_portafolio, nombre_portafolio = mostrar_tabla_portafolios(data)

        # Si el usuario selecciona un Portafolio
        if id_portafolio:
            # Obtiene los Activos financieros vinculados a ese ID.
            activos = obtener_activos_de_portafolio(id_portafolio)
            # Muestra la tabla de Activos
            mostrar_tabla_activos(activos, nombre_portafolio)

            # BOTÓN ETL

            # Si el portafolio tiene Activos habilita el proceso.
            if activos:
                # 1. Definimos la etiqueta y el estado de bloqueo según el session_state
                es_procesando = st.session_state.etl_corriendo
                btn_label = (
                    "Procesando..."
                    if es_procesando
                    else "Empezar proceso ETL"
                )
                # Deshabilitamos el botón si ya hay un proceso en marcha.
                if st.button(btn_label, disabled=es_procesando):
                    # Primero se cambia el estado a True para que la UI bloque
                    st.session_state.etl_corriendo = True
                    # Al volver a entrar, el botón aparece bloqueado
                    st.rerun()

                # Lógica de disparo fuera del bloque del botón para evitar error rerun
                if (
                    st.session_state.etl_corriendo
                    and not st.session_state.resumen_final
                ):
                    disparar_etl(id_portafolio)

        # Area de mensaje dinámico
        renderizar_mensajes()

        # Mensaje final con contador (10 sg)
        if st.session_state.resumen_final:
            renderizar_resumen_final()

    except Exception as e:
        mostrar_error(f"Error crítico: {str(e)}")


def disparar_etl(id_portafolio):
    """
    Lógica UI para la visualización del proceso ETL.
    """
    st.session_state.etl_corriendo = True
    st.session_state.mensajes_exito = []
    st.session_state.mensajes_error = []
    st.session_state.resumen_final = None

    # Marca el tiempo inicial
    start_time = time.time()
    # Instancia de la lógica del Backend
    etl = ETLService()

    # Estos placeholders se mantienen vivos durante toda la ejecución
    progress_bar = st.progress(0)
    status_text = st.empty()
    # Usamos un área de log fija para los mensajes que van rotando
    log_area = st.empty()

    # Bucle del proceso ETL
    for evento in etl.ejecutar_etl(id_portafolio):
        tipo = evento.get("tipo")
        msg = evento.get("mensaje")

        # Actualizamos la UI visual directamente
        status_text.text(f"Procesando: {evento.get('mensaje')}")
        progress_bar.progress(evento.get("progress", 0.0))

        if tipo in ["info", "success", "success_item"]:
            st.session_state.mensajes_exito.append(msg)
            # Mantenemos solo los últimos 2 mensajes para no saturar la vista.
            if len(st.session_state.mensajes_exito) > 2:
                st.session_state.mensajes_exito.pop(0)

            # Mostramos los últimos mensajes en el log_area
            with log_area.container():
                for m in st.session_state.mensajes_exito:
                    st.write(f"✔️ {m}")

        elif tipo == "error":
            # Guardamos el error con un ID único basado en el tiempo.
            st.session_state.mensajes_error.append({
                "id": time.time(),
                "msg": msg,
                "detalle": evento.get("detalle")
            })
            # Los errores los lanzamos como toasts para avisar rápido
            st.toast(f"❌ {msg}")

    # Finalización
    end_time = time.time()
    st.session_state.resumen_final = {
        "tiempo": round(end_time - start_time, 2),
        "errores": len(st.session_state.mensajes_error)
    }

    # Solo ahora, al terminar todo, liberamos el botón y refrescamos
    st.session_state.etl_corriendo = False
    st.rerun()


def renderizar_mensajes():
    """
    Renderiza mensajes de éxito (rotativos) y errores (persistentes con botón)
    """
    # Éxitos (Máximo 2)
    for m in st.session_state.mensajes_exito:
        st.toast(m),

    # Errores (Con botón para cerrar)
    for i, err in enumerate(st.session_state.mensajes_error):
        col_err, col_btn = st.columns([0.85, 0.15])
        with col_err:
            st.error(f"**Error:** {err['msg']}")
            # Si hay detalle técnico, lo metemos en un expander
            if err.get("detalle"):
                with st.expander("Ver detalle técnico"):
                    st.json(err["detalle"])

        with col_btn:
            # Botón para limpiar el error específico
            if st.button("✖", key=f"btn_err_{err['id']}"):
                st.session_state.mensajes_error.pop(i)
                st.rerun()


def renderizar_resumen_final():
    """
    Muestra el resumen final con un contador de 10 segundos
    """
    res = st.session_state.resumen_final
    # Placeholder para el mensaje que desaparecerá
    placeholder = st.empty()

    # Bucle de 10 segundos para el contador regresivo.
    for i in range(10, 0, -1):
        with placeholder.container():
            st.success("¡Carga finalizada!")
            st.write(f"⏱ Tiempo: {res['tiempo']}s | ❌ Errores: {res['errores']}")
            st.info(f"Esta notificación desaparecerá en {i} segundos...")
        time.sleep(1)

    # Al terminar el contador, limpiamos y recargamos la página
    st.session_state.resumen_final = None
    st.rerun()
