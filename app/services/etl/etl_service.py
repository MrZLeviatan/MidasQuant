"""
Servicio de aplicación para ejecución del proceso ETL - Fase de Identificación.

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

# Importación de excepciones personalizadas.
from ...exceptions import (
    RecursoNoEncontrado,
    ExtraccionFallidaError
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

    def ejecutar_extraccion(self, portafolio_id: int):
        """
        Orquestador principal enfocado en la fase de Metadata.

        Regla de negocio:
        - Si el éxito de identificación es >= 80%, el portafolio se marca como ETL.
        - Garantiza el cierre de conexión a base de datos y rollback en caso de fallo.

        Complejidad: O(n), heredada de ejecutar_fase_metadata
        """
        # Abre la conexión con la DB
        db = SessionLocal()

        # Herramienta robusta para información descriptiva (metadatos)
        portafolio_id = int(portafolio_id)

        try:
            # Recupera el objeto portafolio con sus activos vinculados.
            portafolio = obtener_portafolio_con_relaciones(db, portafolio_id)

            if not portafolio:
                raise RecursoNoEncontrado("Portafolio", portafolio_id)

            # Ejecuta la lógica de identificación de activos.
            total_activos, exitosos = self.ejecutar_fase_metadata(db, portafolio)

            # Cálculo de la métrica de éxito.
            tasa_exito = (exitosos / total_activos) if total_activos > 0 else 0

            # Lógica de validación por umbral de negocio.
            if tasa_exito >= 0.8:

                fecha_inicio, fecha_fin = self._obtener_fechas(portafolio)
                self.ejecutar_fase_series_temporales(
                    db, portafolio, fecha_inicio, fecha_fin
                )

                portafolio.isETL = True
                db.add(portafolio)
            else:
                portafolio.isETL = False
                db.add(portafolio)

            # Confirmación final de la transacción en la base de datos.
            db.commit()

        except Exception as e:
            # En caso de error, se deshacen todos los cambios no confirmados.
            db.rollback()
            raise e

        finally:
            # Garantiza que la conexión se devuelva al pool de conexiones.
            db.close()

    def ejecutar_fase_metadata(self, db, portafolio):
        """
        Lógica de Enriquecimiento:
        - Itera activos sin información completa.
        - Agota los motores de búsqueda (cascada).
        - Realiza persistencia atómica por activo.

        Complejidad: O(n * k), donde n es el número de activos
            y k es el número de motores de búsqueda.
        """
        # Calcular numero de correcciones.
        total = len(portafolio.activos)
        exitosos = 0

        # Iteración sobre cada activo del Portafolio encontrado.
        for pa in portafolio.activos:
            activo = pa.activo
            ticker = activo.ticker

            # No re-procesar activos que ya tengan nombre y mercado (optimización).
            ya_identificado = (
                activo.nombre
                and activo.nombre != ticker
                and activo.mercado
            )
            # Si el Activo ya recibió proceso ETL, continue
            if ya_identificado:
                exitosos += 1
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
                    exitosos += 1
                else:
                    raise ExtraccionFallidaError(ticker)

            except ExtraccionFallidaError as e:
                # Se captura la excepción.
                print(f"  ❌ {e}")

            except Exception as e:
                # Si un activo falla catastróficamente, el bucle sigue con los demás
                print(f"Error procesando {ticker}: {e}")

            # Pausa aleatoria para mimetizar comportamiento humano y evitar baneos
            time.sleep(random.uniform(1.5, 3.0))

        # Retorna el umbral de Activos encontrados
        return total, exitosos

    # Lógica de Extracción de Series Temporales (Precios OHLCV):
    def ejecutar_fase_series_temporales(self, db, portafolio, fecha_inicio, fecha_fin):
        """
        - Identifica rangos de fechas faltantes en la DB para cada activo.
        - Descarga únicamente los segmentos necesarios (pasado o futuro).
        - Realiza inserción masiva (bulk) para optimizar el rendimiento de la DB.

        Complejidad: O(n) por cada iteración en las listas.
        """
        # Itera sobre la relación muchos-a-muchos entre portafolio y activos
        for pa in portafolio.activos:
            activo = pa.activo
            ticker = activo.ticker

            # Obtener fechas ya existentes en DB para este activo específico
            # f[0] extrae el primer elemento de la tupla devuelta por el query
            fechas_existentes = set(
                f[0] for f in db.query(SerieTemporalRaw.fecha)
                .filter(SerieTemporalRaw.activo_id == activo.id_activo)
                .all()
            )

            # Pausa aleatoria para intentar engañar a los sistemas anti-bot
            time.sleep(random.uniform(2, 4))

            # Llama al orquestador de motores
            datos = self.market_extractor.extraer(
                ticker,
                fecha_inicio,
                fecha_fin
            )

            # Si el extractor falló en todas las fuentes, salta al siguiente activo
            if not datos:
                continue

            # Solo conserva registros cuya fecha no esté en el set de la DB
            datos_filtrados = [
                reg for reg in datos
                if reg["fecha"] not in fechas_existentes
            ]

            # Si después de filtrar no hay nada nuevo que guardar, continúa
            if not datos_filtrados:
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

    def _obtener_fechas(self, portafolio):
        """
        Helper para obtener el rango temporal de la configuración.

        Complejidad: O(1) - Acceso a atributos de relación.
        """
        if not portafolio.configuracion:
            raise RecursoNoEncontrado(
                "Configuración de Portafolio", portafolio.id_portafolio
            )

        config = portafolio.configuracion
        return config.fecha_inicio, config.fecha_fin
