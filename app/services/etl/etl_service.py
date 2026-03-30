"""
Servicio de aplicación para ejecución del proceso ETL

Responsabilidad:
- Orquestar la extracción de metadatos (Identidad del activo).
- Gestionar la persistencia atómica de la información descriptiva.
- Extracción de series temporales OHLCV (Gestión de Gaps).
"""

import time
import random

# Importación del generador de sesiones para interactuar con la persistencia.
from app.database.connection import SessionLocal

# Importación del servicio encargado de la consulta optimizada de portafolios.
from app.services.portafolios.portafolio_service import (
    obtener_portafolio_con_relaciones
)

# Importación de la lógica de extracción de Series Temporales
from app.etl.extract.market_data_extractor import ExtractorFinanciero

# Importación de la lógica de extracción de metadatos
from app.etl.extract.asset_metadata_extractor import AssetMetadataExtractor

# Importación de la lógica para la Alineación de Calendarios bursátiles
from app.etl.transform.time_series_alignment import alinear_series_temporales

# Importación de la lógica para la Auditoria de las Series Temporales
from app.etl.transform.quality_audit import auditar_calidad_series

# Importación de la lógica de imputación y transformación de las Series Temporales
from app.etl.transform.data_imputation import ImputadorSeriesTemporales


# Importación de excepciones personalizadas.
from ...exceptions import (
    AppError,
    ExtraccionFallidaError,
    RecursoNoEncontradoError
)

# Importación de los modelos de entidades
from app.database.models import SerieTemporalRaw


class ETLService:
    """
    Coordina el ciclo de vida de la identificación de activos para un portafolio.
    """

    def __init__(self):
        """
        Inicializa el extractor de metadatos.

        Complejidad: O(1)
        """
        # Herramienta robusta para información descriptiva (metadatos)
        self.metadata_extractor = AssetMetadataExtractor()

        # Herramienta robusta para información de Series Temporales
        self.market_extractor = ExtractorFinanciero()

    def ejecutar_etl(self, portafolio_id: int):
        """
        Orquestador Principal del proceso ETL para un portafolio específico.

        Regla de negocio:
        - Si el éxito de identificación es >= 80%, el portafolio se marca como ETL.
        - Garantiza el cierre de conexión a base de datos y rollback en caso de fallo.

        Complejidad: O(n^4) por la iteración en las series temporales y su búsqueda.
            Se promete que se optimizara :c
        """
        # Abre la conexión con la DB
        db = SessionLocal()

        # Fase 1: Recuperación de Portafolio y sus relaciones

        # Parsear de String a int (Error raro con el Streamlit)
        portafolio_id = int(portafolio_id)

        try:

            # Proceso de la barra de progreso para la UI.
            yield {"tipo": "info", "mensaje": "Iniciando proceso ETL...", "progress": 0}

            # Recupera el objeto portafolio con sus activos vinculados.
            portafolio = obtener_portafolio_con_relaciones(db, portafolio_id)

            # Validación de existencia del portafolio antes de continuar con el proceso.
            if not portafolio:
                raise RecursoNoEncontradoError(
                    message="El portafolio solicitado no existe.",
                    code="PORTFOLIO_NOT_FOUND",
                    detail={"id_buscado": portafolio_id}
                )

            # Total de activos para calcular la métrica de éxito al final del proceso.
            total_activos = len(portafolio.activos)

            # Validación de que el portafolio tenga activos asignados
            if total_activos == 0:
                raise RecursoNoEncontradoError(
                    message="El portafolio no tiene activos asignados.",
                    code="EMPTY_PORTFOLIO"
                )

            # Fase 2: Metadatos de los Activos (Identidad)
            exitosos = 0

            # Ejecuta la lógica de identificación de activos.
            for evento in self.ejecutar_fase_metadata(db, portafolio):
                yield evento
                if evento.get("tipo") == "success_item":
                    exitosos += 1

            # Cálculo de la métrica de éxito.
            tasa = exitosos / total_activos if total_activos > 0 else 0

            # Lógica de validación por umbral de negocio.
            if tasa < 0.8:
                yield {
                    "tipo": "error",
                    "mensaje": f"Calidad de metadatos insuficiente ({tasa:.0%}).",
                    "code": "METADATA_THRESHOLD_NOT_MET",
                    "detail": f"Exitosos: {exitosos}, Total: {total_activos}",
                    "progress": 0.3
                }
                return

            # Mensaje de éxito para la fase de metadata
            yield {
                "tipo": "success",
                "mensaje": f"Metadata completado ({exitosos}/{total_activos})",
                "progress": 0.3
            }

            # Fase 3: Series Temporales (Precios OHLCV)

            # Obtenemos las fechas formateadas
            fecha_inicio, fecha_fin = self._obtener_fechas(portafolio)

            # Se ejecuta la extracción de la Series Temporales
            for evento in self.ejecutar_fase_series_temporales(
                db, portafolio, fecha_inicio, fecha_fin
            ):
                yield evento

            # Mensajes de información para la barra de progreso
            yield {"tipo": "success", "mensaje": "Series completadas", "progress": 0.7}

            # Fse 4: Transformación y Calidad

            yield {"tipo": "info", "mensaje": "Alineando series...", "progress": 0.75}

            # Transformación de alineación de calendarios
            dataset = alinear_series_temporales(
                db, [pa.activo for pa in portafolio.activos],
                fecha_inicio,
                fecha_fin
            )

            yield {"tipo": "success", "mensaje": "Alineación completa", "progress": 0.8}

            # Auditar el dataset
            dataset_auditado = auditar_calidad_series(dataset)

            yield {"tipo": "success", "mensaje": "Auditoría completa", "progress": 0.9}

            # Imputación (Putación)
            imputador = ImputadorSeriesTemporales(db)
            imputador.procesar(
                dataset_auditado, [pa.activo for pa in portafolio.activos]
            )

            yield {
                "tipo": "success", "mensaje": "Imputación completa", "progress": 0.95
            }

            # Fase 5: Load, finalización y persistencia del estado ETL

            portafolio.isETL = True
            db.add(portafolio)

            # Confirmación final de la transacción en la base de datos.
            db.commit()

            yield {
                "tipo": "success",
                "mensaje": "ETL finalizado correctamente",
                "progress": 1.0
            }

        except AppError as e:
            db.rollback()
            error_dict = e.to_dict()
            yield {
                "tipo": "error",
                "mensaje": error_dict["message"],
                "code": error_dict["code"],
                "detalle": error_dict["detail"],
                "progress": 0.5
            }

        except Exception as e:
            db.rollback()
            yield {
                "tipo": "error",
                "mensaje": "Error crítico inesperado en el orquestador",
                "code": "SYSTEM_FATAL_ERROR",
                "detalle": str(e),
                "progress": 0.5
            }

        finally:
            # Garantiza que la conexión se devuelva al pool de conexiones.
            db.close()

    def ejecutar_fase_metadata(self, db, portafolio):
        """
        Lógica de Enriquecimiento del metaData de los Activos

        - Itera activos sin información completa.
        - Agota los motores de búsqueda (cascada).
        - Realiza persistencia atómica por activo.

        Complejidad: O(n^2), por la iteración sobre el metodo de
            'buscar_en_cascada' que a su vez itera sobre múltiples fuentes.
        """
        # Calcular numero de correcciones.
        total = len(portafolio.activos)

        # Iteración sobre cada activo del Portafolio encontrado.
        for i, pa in enumerate(portafolio.activos):
            activo = pa.activo
            ticker = activo.ticker

            # Cálculo del progreso para la barra de progreso (30% dedicado a esta fase).
            progreso = (i / total) * 0.3

            # Mensaje de progreso para la UI, indicando el ticker que está procesando.
            yield {
                "tipo": "info",
                "mensaje": f"Metadata: {ticker}",
                "progress": progreso
            }

            # No re-procesar activos que ya tengan nombre y mercado (optimización).
            if activo.nombre and activo.nombre != ticker and activo.mercado:
                yield {
                    "tipo": "success_item",
                    "mensaje": f"{ticker} ya completo, saltando",
                    "progress": progreso
                }
                continue

            try:
                # Intento de búsqueda en cascada
                info = self.metadata_extractor.buscar_en_cascada(ticker)

                if info:
                    # Actualización de los campos descriptivos
                    activo.nombre = info["nombre"]
                    activo.tipo_activo = info["tipo_activo"]
                    activo.mercado = info["mercado"]

                    # Persistencia inmediata en la sesión para asegurar el avance
                    db.add(activo)
                    db.flush()

                    yield {
                        "tipo": "success_item",
                        "mensaje": f"{ticker} OK",
                        "progress": progreso
                    }

            except ExtraccionFallidaError as e:
                # Caso específico: Orquestador falló con múltiples fuentes
                yield {
                    "tipo": "error",
                    "mensaje": f"{ticker}: {str(e)}",
                    "code": e.code,
                    "detalle": e.detalle_completo(),
                    "progress": progreso
                }

            except AppError as e:
                # Si ya es una de nuestras excepciones, la dejamos pasar tal cual
                error_data = e.to.dict()
                yield {
                    "tipo": "error",
                    "mensaje": f"{ticker}: {error_data['message']}",
                    "code": error_data['code'],
                    "detalle": error_data['detail'],
                    "progress": progreso
                }

            # Error no controlado
            except Exception as e:
                yield {
                    "tipo": "error",
                    "mensaje": f"{ticker}: Error crítico inesperado",
                    "code": "UNKNOWN_SYSTEM_ERROR",
                    "detalle": str(e),
                    "progress": progreso
                }

        # Pausa aleatoria para mimetizar comportamiento humano y evitar baneos
        time.sleep(random.uniform(1.5, 3.0))

    def ejecutar_fase_series_temporales(self, db, portafolio, fecha_inicio, fecha_fin):
        """
        Lógica de Extracción de Series Temporales (Precios OHLCV):

        - Identifica rangos de fechas faltantes en la DB para cada activo.
        - Descarga únicamente los segmentos necesarios (pasado o futuro).
        - Realiza inserción masiva (bulk) para optimizar el rendimiento de la DB.

        Complejidad: O(n^3) por cada iteración del método de extraer,
            que a su vez contiene una complejidad O(n^2).
        """
        # Calcular el total de activos para la métrica de progreso.
        total = len(portafolio.activos)

        # Itera sobre la relación muchos-a-muchos entre portafolio y activos
        for i, pa in enumerate(portafolio.activos):
            activo = pa.activo
            ticker = activo.ticker

            # Rango de progreso: del 30% al 70%
            progreso = 0.3 + (i / total) * 0.4

            # Mensaje de progreso para la UI, indicando el ticker que está procesando.
            yield {
                "tipo": "info",
                "mensaje": f"Series: {ticker}",
                "progress": progreso
            }

            try:

                # Obtener fechas ya existentes en DB para este activo específico
                # f[0] extrae el primer elemento de la tupla devuelta por el query
                fechas_existentes = set(
                    f[0] for f in db.query(SerieTemporalRaw.fecha)
                    .filter(SerieTemporalRaw.activo_id == activo.id_activo)
                    .all()
                )

                # Pausa aleatoria para intentar engañar a los sistemas anti-bot
                time.sleep(random.uniform(1.5, 3.0))

                # Llama al orquestador para obtener los datos de series temporales
                datos = self.market_extractor.extraer(
                    ticker,
                    fecha_inicio,
                    fecha_fin
                )

                # Solo conserva registros cuya fecha no esté en el set de la DB
                datos_filtrados = [
                    reg for reg in datos
                    if reg["fecha"] not in fechas_existentes
                ]

                # Si no hay datos nuevos, envía un mensaje de "Al día" y continúa
                if not datos_filtrados:
                    yield {
                        "tipo": "success_item",
                        "mensaje": f"{ticker}: Al día",
                        "progress": progreso
                    }
                    continue

                # Convierte los diccionarios planos en objetos del modelo
                registros = [
                    SerieTemporalRaw(
                        activo_id=activo.id_activo,
                        fecha=reg["fecha"],
                        open=reg["open"],
                        high=reg["high"],
                        low=reg["low"],
                        close=reg["close"],
                        volumen=reg["volumen"]
                    )
                    for reg in datos_filtrados
                ]

                # Inserción masiva: prepara los objetos para la base de datos
                db.bulk_save_objects(registros)
                # Envía los cambios a la DB pero NO cierra la transacción todavía
                db.flush()

                yield {
                    "tipo": "success_item",
                    "mensaje": f"{ticker}: +{len(registros)} registros",
                    "progress": progreso
                }

            # Error detallado de los motores de búsqueda
            except ExtraccionFallidaError as e:
                yield {
                    "tipo": "error",
                    "mensaje": e.message,
                    "code": e.code,
                    "detalle": e.detalle_completo(),
                    "progress": progreso
                }

            except AppError as e:
                # Si ya es una de nuestras excepciones, la dejamos pasar tal cual
                err = e.to_dict()
                yield {
                    "tipo": "error",
                    "mensaje": f"{ticker}: {err['message']}",
                    "code": err['code'],
                    "detail": err['detail'],
                    "progress": progreso
                }

            except Exception as e:
                # Errores de Python o infraestructura no controlada
                yield {
                    "tipo": "error",
                    "mensaje": f"{ticker}: Error interno en procesamiento",
                    "code": "INTERNAL_PROCESS_ERROR",
                    "detail": str(e),
                    "progress": progreso
                }
            # Breve pausa entre activos para estabilidad de la conexión
            time.sleep(random.uniform(1, 2))

    def _obtener_fechas(self, portafolio):
        """
        Helper para obtener el rango temporal de la configuración.

        Complejidad: O(1) - Acceso a atributos de relación.
        """
        if not portafolio.configuracion:
            raise RecursoNoEncontradoError(
                message="""
                    No se puede iniciar el ETL:
                    El portafolio no tiene una configuración de fechas.
                """,
                code="PORTAFOLIO_CONFIGURACION_FALTANTE",
                detail={
                    "portafolio_id": portafolio.id_portafolio,
                    "action": """
                        Verifique que el portafolio tenga
                        fechas de inicio y fin definidas.
                    """
                }
            )
        # Acceso directo a la configuración relacionada del portafolio
        config = portafolio.configuracion

        # Validar que las fechas no sean nulas dentro de la configuración
        if not config.fecha_inicio or not config.fecha_fin:
            raise RecursoNoEncontradoError(
                message="Rango de fechas incompleto en la configuración.",
                code="INVALID_DATE_RANGE",
                detail=f"Inicio: {config.fecha_inicio}, Fin: {config.fecha_fin}"
            )

        # Retorna las fechas de inicio y fin para su uso
        return config.fecha_inicio, config.fecha_fin
