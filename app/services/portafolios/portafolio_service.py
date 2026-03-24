"""
Responsabilidades:
- Procesar entrada del usuario (tickers y fechas)
- Validar reglas de negocio (mínimo activos, horizonte temporal)
- Gestionar la persistencia en base de datos
- Preparar la configuración base para el proceso ETL
"""

# Sesión de base de datos
from ...database.connection import SessionLocal
from sqlalchemy.exc import IntegrityError
# Utilizado para joined en relación de métodos
from sqlalchemy.orm import joinedload


# Excepciones específicas del dominio
from ...exceptions import MinimoActivosError
from ...exceptions import NombreDuplicadoError

# Llamada a los modelos ORM
from ...database.models import (
    Activo,
    Portafolio,
    PortafolioActivo,
    ConfiguracionAnalisis,
)

# Llamada a utilidades de validación y normalización
from ...utils.text_utils import normalizar_tickers, validar_ticker_formato
from ...utils.date_utils import validar_rango_fechas, validar_horizonte_minimo

# Librerías estándar
from datetime import date, datetime


# Función principal del servicio para crear un portafolio completo
def crear_portafolio_completo(
    nombre_portafolio: str,
    tickers_input: str,
    fecha_inicio: date,
    fecha_fin: date,
    db=None
):
    """
    Crea un portafolio completo con sus activos y configuración de análisis.

    Complejidad: O(n) por la iteración sobre las listas en ciclos.
    """

    # 1. NORMALIZACIÓN DE TICKERS: Convierte el string en lista limpia
    tickers = normalizar_tickers(tickers_input)

    # 2. VALIDACIONES DE NEGOCIO
    # Validar que haya al menos 20 activos
    if len(tickers) < 20:
        raise MinimoActivosError(minimo=20, actual=len(tickers))

    # Validar formato de cada ticker
    for ticker in tickers:
        validar_ticker_formato(ticker)

    # Validar fechas (orden correcto)
    validar_rango_fechas(fecha_inicio, fecha_fin)

    # Validar horizonte mínimo de 5 años
    validar_horizonte_minimo(fecha_inicio, fecha_fin, min_anios=5)

    # Crear sesión de base de datos transaccional
    # Si no se proporciona una sesión, se crea una nueva
    if db is None:
        db = SessionLocal()

    # 3. OBTENER O CREAR ACTIVOS
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
                    ticker=ticker,
                    nombre=None,
                    tipo_activo=None,
                    mercado=None
                )
                # Agregar el nuevo activo a la sesión pero no hacer commit aún
                db.add(activo)
                db.flush()  # Permite obtener el ID sin hacer commit

            # Agregar a la lista de activos para el portafolio
            activos_db.append(activo)

        # 4. CREAR PORTAFOLIO
        portafolio = Portafolio(
            nombre=nombre_portafolio,
            fecha_creacion=datetime.now()
        )
        # Agregar el portafolio a la sesión pero no hacer commit aún
        db.add(portafolio)
        db.flush()  # Obtener ID del portafolio sin hacer commit

        # 5. CREAR RELACIONES ACTIVO-PORTAFOLIO
        # Para cada activo, crear una relación con el portafolio
        for activo in activos_db:
            relacion = PortafolioActivo(
                portafolio_id=portafolio.id_portafolio,
                activo_id=activo.id_activo
            )
            # Agregar la relación a la sesión pero no hacer commit aún
            db.add(relacion)

        # 6. CREAR CONFIGURACIÓN DE ANÁLISIS
        # Esta configuración se usará luego para el proceso ETL, análisis y benchmarking
        configuracion = ConfiguracionAnalisis(
            portafolio_id=portafolio.id_portafolio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        # Agregar la configuración a la sesión pero no hacer commit aún
        db.add(configuracion)

        # 7. CONFIRMAR TRANSACCIÓN
        # Si todo ha ido bien hasta aquí, se confirma la transacción con un commit a BD
        db.commit()

        # 8. RESPUESTA DEL SERVICIO
        # Preparar la respuesta con la información del portafolio creado
        return {
            "portafolio_id": portafolio.id_portafolio,
            "nombre": portafolio.nombre,
            "activos": [a.ticker for a in activos_db],
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    # Manejo de errores específicos de integridad (como nombre de portafolio duplicado)
    except IntegrityError:
        db.rollback()
        raise NombreDuplicadoError(nombre_portafolio=portafolio.nombre)

    # Si ocurre cualquier error durante el proceso, se captura la excepción
    except Exception as e:
        # Si ocurre un error, revertir cambios
        db.rollback()
        raise e

    # Siempre cerrar la sesión de base de datos al finalizar el proceso
    finally:
        # Cerrar la sesión siempre
        db.close()


# Función para obtener todos los portafolios con su configuración (Usado en comboBox).
def obtener_todos_los_portafolios():
    """
    Obtiene lista de portafolios con su configuración para el combobox.

    Complejidad: O(n) por la iteración sobre los portafolios y sus activos.
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
            conf = db.query(ConfiguracionAnalisis).filter_by(
                portafolio_id=p.id_portafolio
            ).first()

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
        return lista_portafolios
    finally:
        db.close()


# Función para obtener un resumen de todos los portafolios (Usado en Tablas).
def obtener_resumen_portafolios():
    """
    Obtiene información resumida de portafolios para visualización en tabla.

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
        # - .all(): Ejecuta la consulta y trae todos los registros a memoria.
        """
        portafolios = db.query(Portafolio).options(
            joinedload(Portafolio.configuraciones)
        ).all()

        resultado = []

        # Itera sobre cada objeto de portafolio recuperado.
        for p in portafolios:
            # Intenta obtener la primera configuración asociada
            # Se usa una expresión ternaria para evitar errores si la lista está vacía.
            conf = p.configuraciones[0] if p.configuraciones else None

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


# Función para obtener los activos de un Portafolio mediante su Id.
def obtener_activos_de_portafolio(portafolio_id: int):
    """
    Obtiene los activos asociados a un portafolio.

    Regla de negocio:
    - Si el ETL no se ha ejecutado → solo mostrar ticker
    - Si ETL ya se ejecutó → mostrar todos los campos

    Complejidad: O(n) por los Joinedload y el bucle de activos.
    """
    # Abre una nueva sesión de conexión con la BD,
    db = SessionLocal()

    # Parsear de String a int (Pasa con el Streamlit)
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

        if not portafolio:
            return []

        # Construcción del resultado usando la relación definida en el modelo.
        # Navegamos: Portafolio -> PortafolioActivo (pa) -> Activo (pa.activo)
        resultado = []
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

        return resultado
    # Liberación de la conexión al pool.
    finally:
        db.close()
