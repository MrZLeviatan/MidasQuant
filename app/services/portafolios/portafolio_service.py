"""
Responsabilidades:
- Procesar entrada del usuario (tickers y fechas)
- Validar reglas de negocio (mínimo activos, horizonte temporal)
- Gestionar la persistencia en base de datos
- Preparar la configuración base para el proceso ETL
"""

# Tipos de datos para anotaciones
from typing import Dict, Any, Optional

# Sesión de base de datos
from ...database.connection import SessionLocal
from sqlalchemy.exc import IntegrityError
# Utilizado para joined en relación de métodos
from sqlalchemy.orm import joinedload, Session


# Excepciones específicas del dominio
from ...exceptions import (
    AppError,
    BDError,
    MinimoActivosError,
    NombreDuplicadoError,
    RecursoNoEncontradoError,
    PortafolioSinETLError
)

# Llamada a los modelos ORM
from ...database.models import (
    Activo,
    Portafolio,
    PortafolioActivo,
    ConfiguracionAnalisis,
)

# Llamada a utilidades de validación y normalización
from ...utils.text_utils import normalizar_tickers, validar_ticker_formato
from ...utils.date_utils import (
    validar_rango_fechas, validar_horizonte_minimo, validar_fecha_futura
)
# Librerías estándar
from datetime import date


def crear_portafolio_completo(
    nombre_portafolio: str,
    tickers_input: str,
    fecha_inicio: date,
    fecha_fin: date,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Crea un portafolio completo con sus activos y configuración de análisis.

    Reglas de negocio:
    - El portafolio debe tener al menos 20 activos.
    - El horizonte temporal debe ser de al menos 5 años.
    - El formato de los tickers debe ser válido (solo letras, números y guiones).
    - El nombre del portafolio debe ser único.
    - Al crear el portafolio, se crean los activos (si no existen) y las relaciones
        correspondientes (la configuración).

    Retorna: Un diccionario con la información del portafolio creado.

    Complejidad: O(n) por la iteración sobre las listas en ciclos.
    """

    # 1. Normalización de Tickers: Convierte el string en lista limpia
    tickers = normalizar_tickers(tickers_input)

    # 2. Validaciones de negocio

    # Validar que haya al menos 20 activos
    if len(tickers) < 20:
        raise MinimoActivosError(minimo=20, actual=len(tickers))

    # Validar formato de cada ticker
    for ticker in tickers:
        validar_ticker_formato(ticker)

    # Valida que la fecha_fin no sobrepase la fecha actual.
    validar_fecha_futura(fecha_fin)

    # Validar fechas (orden correcto)
    validar_rango_fechas(fecha_inicio, fecha_fin)

    # Validar horizonte mínimo de 5 años
    validar_horizonte_minimo(fecha_inicio, fecha_fin, min_anios=5)

    """
    3. Gestión de base de datos
    - Crea una sesión de bd transaccional
    - Si no se proporciona una sesión, se crea una nueva (para Tests)
    - Se crea una bandera para poder saber si toca cerrar la bd.
    """
    local_session = False
    if db is None:
        db = SessionLocal()
        local_session = True

    # 4. Obtener o Crear Activos
    try:
        # Lista para almacenar los objetos Activo que se usarán en el portafolio
        activos_db = []

        # Para cada ticker, buscar o crear el activo correspondiente
        for ticker in tickers:

            # Buscar si el activo ya existe en la base de datos
            activo = db.query(Activo).filter(Activo.ticker == ticker).first()

            # Si no existe, se crea uno nuevo con información mínima
            # (Se completa la información luego en ETL)
            if not activo:
                activo = Activo(
                    ticker=ticker
                )
                # Agregar el nuevo activo a la sesión pero no hacer commit aún
                db.add(activo)
                # Permite obtener el ID sin hacer commit
                db.flush()

            # Agregar a la lista de activos para el portafolio
            activos_db.append(activo)

        # 4. Crear Portafolio
        portafolio = Portafolio(
            nombre=nombre_portafolio,
        )
        # Agregar el portafolio a la sesión pero no hacer commit aún
        db.add(portafolio)
        # Obtener ID del portafolio sin hacer commit
        db.flush()

        # 5. Crear Relación Activo-Portafolio

        # Para cada activo, crear una relación con el portafolio
        for activo in activos_db:
            relacion = PortafolioActivo(
                portafolio_id=portafolio.id_portafolio,
                activo_id=activo.id_activo
            )
            # Agregar la relación a la sesión pero no hacer commit aún
            db.add(relacion)

        # 6. Crear configuración de análisis para el portafolio
        # Esta configuración se usará luego para el proceso ETL, análisis y benchmarking
        configuracion = ConfiguracionAnalisis(
            portafolio_id=portafolio.id_portafolio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        # Agregar la configuración a la sesión pero no hacer commit aún
        db.add(configuracion)

        # 7. Confirmar la transacción
        # Si todo ha ido bien hasta aquí, se confirma la transacción con un commit a BD
        db.commit()

        # 8. Respuesta del Servicio
        # Preparar la respuesta con la información del portafolio creado
        return {
            "portafolio_id": portafolio.id_portafolio,
            "nombre": portafolio.nombre,
            "activos": [a.ticker for a in activos_db],
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    # Manejo de errores específicos de integridad
    except IntegrityError:
        db.rollback()
        # Se llama a la excepción personalizada
        raise NombreDuplicadoError(nombre_portafolio=portafolio.nombre)

    except AppError:
        # Si ya es una de nuestras excepciones, la dejamos pasar tal cual
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        # Cualquier error no controlado lo envolvemos en un BDError genérico
        raise BDError(
            message="Error inesperado al persistir el portafolio",
            detail=str(e)
        )

    # Siempre cerrar la sesión de base de datos al finalizar el proceso
    finally:
        if local_session:
            # Cerrar la sesión siempre
            db.close()


def obtener_portafolio_con_relaciones(db, portafolio_id: int):
    """
    Obtiene el portafolio mediante su ID con las relaciones de:
    - activos
    - configuraciones

    Complejidad: O(1) Gracias a joinedload se resuelve la búsqueda en una sola
    """
    # Inicia la construcción de la consulta sobre la entidad 'Portafolio'
    portafolio_relaciones = db.query(Portafolio).options(
        # Realiza un SQL Join para traer los activos vinculados al portafolio
        # a través de la tabla intermedia (PortafolioActivos) y el objeto Activo final
        joinedload(Portafolio.activos).joinedload(PortafolioActivo.activo),
        # Trae también la configuración (fechas, etc.) en el mismo SELECT.
        joinedload(Portafolio.configuracion)
        # Busca coincidencias exactas con la llave primaria 'id_portafolio'.
    ).filter(
        Portafolio.id_portafolio == portafolio_id
        # Retorna el primer objeto encontrado o 'None' si no existe el registro.
    ).first()

    # Si no se encuentra el portafolio, se lanza una excepción
    if not portafolio_relaciones:
        raise RecursoNoEncontradoError(
            recurso="Portafolio",
            identificador=portafolio_id
        )

    # Retorna el Portafolio con sus Relaciones (Activos y Configuración)
    return portafolio_relaciones


def obtener_todos_los_portafolios():
    """
    # Función para obtener todos los portafolios con su configuración
        (Usado en comboBox).

    Complejidad: O(n^2) por la iteración sobre los portafolios y luego sobre
        los tickers de los Activos asociados al portafolio.
    """
    # Crear sesión de base de datos
    db = SessionLocal()

    try:
        # Traemos el portafolio y su configuración asociada (join)
        resultados = db.query(Portafolio).all()

        # Preparar la lista de portafolios con su configuración para el combobox
        lista_portafolios = []

        # Iterar sobre los portafolios obtenidos y preparar la información
        for p in resultados:

            # Buscamos su configuración de análisis
            conf = p.configuracion

            # Buscamos sus tickers
            tickers_obj = db.query(Activo).join(PortafolioActivo).filter(
                PortafolioActivo.portafolio_id == p.id_portafolio
            ).all()

            # Agregar la información del portafolio a la lista de respuesta
            lista_portafolios.append({
                "id": p.id_portafolio,
                "nombre": p.nombre,
                "fecha_creacion": p.fecha_creacion,
                "tickers": ", ".join([a.ticker for a in tickers_obj]),
                "fecha_inicio": conf.fecha_inicio if conf else date(2015, 1, 5),
                "fecha_fin": conf.fecha_fin if conf else date(2026, 3, 20)
            })
        # Retornar la lista completa de portafolios con su configuración y tickers
        return lista_portafolios
    finally:
        db.close()


def obtener_resumen_portafolios():
    """
    Obtiene información resumida de portafolios para visualización en Tabla.

    Complejidad: O(n) por los Joinedload y el bucle de procesamiento.
    """
    # Abre una nueva sesión de conexión con la BD,
    db = SessionLocal()

    try:
        """
        Realiza una consulta principal:

        - db.query(Portafolio): Busca en la tabla de portafolios
        - .options(joinedload(...)): Realiza un "JOIN" en SQL para traer la
            configuración de análisis en la misma consulta, evitando consultar
            la BD dentro del bucle.
        - .all(): Ejecuta la consulta y trae todos los registros a memoria.
        """
        portafolios = db.query(Portafolio).options(
            joinedload(Portafolio.configuracion)
        ).all()

        resultado = []

        # Itera sobre cada objeto de portafolio recuperado.
        for p in portafolios:
            # Intenta obtener la primera configuración asociada
            conf = p.configuracion

            # Mapea el objeto de base de datos a un diccionario simple
            resultado.append({
                "id": p.id_portafolio,
                "nombre": p.nombre,
                "fecha_creacion": p.fecha_creacion,
                "fecha_inicio": conf.fecha_inicio if conf else None,
                "fecha_fin": conf.fecha_fin if conf else None,
                "etl": "Sí" if p.isETL else "No"
            })

        # Retorna la lista de diccionario lista para ser usada.
        return resultado
    # Finalmente, cierra sesión pase lo que pase para liberar recursos
    finally:
        db.close()


def obtener_activos_de_portafolio(portafolio_id: int):
    """
    Obtiene los activos asociados a un portafolio mediante su ID.

    Regla de negocio:
    - Si el ETL no se ha ejecutado: Solo mostrar ticker
    - Si ETL ya se ejecutó: Mostrar todos los campos

    Complejidad: O(n) por los Joinedload y el bucle de activos.
    """
    # Abre una nueva sesión de conexión con la BD,
    db = SessionLocal()

    # Parsear de String a int (Error raro con el Streamlit)
    portafolio_id = int(portafolio_id)

    try:
        """
        Consulta única optimizada:
        - Buscamos el portafolio por ID.
        - .options(joinedload(...)): Realiza un SQL JOIN para traer la tabla intermedia
            y los activos finales de una vez, evitando el problema de N+1 consultas.
        """
        portafolio = db.query(Portafolio).options(
            joinedload(Portafolio.activos).joinedload(PortafolioActivo.activo)
        ).filter(Portafolio.id_portafolio == portafolio_id).first()

        # Si no se encuentra el portafolio, se lanza una excepción
        if not portafolio:
            raise RecursoNoEncontradoError(
                recurso="Portafolio",
                identificador=portafolio_id
            )

        # Construcción del resultado usando la relación definida en el modelo.
        resultado = []

        # Definimos una bandera para saber si el portafolio ya pasó por ETL o no
        is_etl_ready = portafolio.isETL

        # Iteramos sobre cada activo del portafolio
        for pa in portafolio.activos:
            activo = pa.activo
            """
            Regla de negocio:
            - Si IsETL es False, solo se expone el ticker seleccionado por el Usuario.
            """
            resultado.append({
                "ticker": activo.ticker,
                "nombre": activo.nombre if is_etl_ready else "",
                "tipo_activo": activo.tipo_activo if is_etl_ready else "",
                "mercado": activo.mercado if is_etl_ready else ""
            })

        # Retorna la lista de Activos asociados al Portafolio
        return resultado

    # Liberación de la conexión al pool.
    finally:
        db.close()


def obtener_portafolios_con_etl():
    """
    Obtiene únicamente los portafolios que ya ejecutaron ETL.

    Regla de negocio:
    - Solo pueden compararse portafolios con información enriquecida
        proveniente del proceso ETL.

    Complejidad: O(n) por recorrido lineal de resultados.
    """

    # Crear sesión de BD
    db = SessionLocal()

    try:
        # Filtra únicamente portafolios con ETL ejecutado.
        portafolios = db.query(Portafolio).options(
            # joinedload evita consultas adicionales para configuración.
            joinedload(Portafolio.configuracion)
        ).filter(
            Portafolio.isETL.is_(True)
        ).all()

        resultado = []

        # Transformación ORM -> Diccionario
        for p in portafolios:

            # Obtener la configuración asociada al portafolio (fechas, etc.)
            conf = p.configuracion

            # Agregar la información relevante del portafolio a la lista de resultados.
            resultado.append({
                "id": p.id_portafolio,
                "nombre": p.nombre,
                "fecha_inicio": conf.fecha_inicio if conf else None,
                "fecha_fin": conf.fecha_fin if conf else None,
                "fecha_creacion": p.fecha_creacion
            })

        # Retorna la lista de portafolios con ETL
        return resultado
    # Finalmente, cierra la sesión de base de datos para liberar recursos.
    finally:
        db.close()


def obtener_activos_comparacion(portafolio_id: int):
    """
    Obtiene los activos de un portafolio.

    Reglas de negocio:
    - El portafolio debe existir.
    - El portafolio debe haber ejecutado ETL.
    - Los activos retornan información enriquecida.

    Complejidad: O(n) por iteración de activos.
    """

    # Crear sesión
    db = SessionLocal()

    try:
        # Parsear de String a int (Error raro con el Streamlit)
        portafolio_id = int(portafolio_id)

        """
        Consulta única optimizada:
        - Buscamos el portafolio por ID.
        - .options(joinedload(...)): Realiza un SQL JOIN para traer la tabla intermedia
            y los activos finales de una vez, evitando el problema de N+1 consultas.
        """
        portafolio = db.query(Portafolio).options(
            joinedload(Portafolio.activos).joinedload(
                PortafolioActivo.activo
            )
        ).filter(
            Portafolio.id_portafolio == portafolio_id
        ).first()

        # Si no se encuentra el portafolio, se lanza una excepción
        if not portafolio:
            raise RecursoNoEncontradoError(
                recurso="Portafolio",
                identificador=portafolio_id
            )

        # Validar que el portafolio del Activo si paro por ETL
        if not portafolio.isETL:
            raise PortafolioSinETLError(portafolio_id=portafolio_id)

        # Construcción del resultado usando la relación definida en el modelo.
        resultado = []

        # Iteramos sobre cada activo del portafolio
        for pa in portafolio.activos:

            activo = pa.activo

            resultado.append({
                "id_activo": activo.id_activo,
                "ticker": activo.ticker,
                "nombre": activo.nombre,
                "tipo_activo": activo.tipo_activo,
                "mercado": activo.mercado
            })

        # Retorna la lista de Activos asociados al Portafolio
        return resultado

    # Liberación de la conexión al pool.
    finally:
        db.close()
