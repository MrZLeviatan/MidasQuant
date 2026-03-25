"""
Servicio de aplicación para ejecución del proceso ETL - Fase de Identificación.

Responsabilidad:
- Orquestar la extracción de metadatos (Identidad del activo).
- Gestionar la persistencia atómica de la información descriptiva.
"""

import time
import random

# Importación del generador de sesiones para interactuar con la persistencia.
from app.database.connection import SessionLocal

# Importación del servicio encargado de la consulta optimizada de portafolios.
from app.services.portafolios.portafolio_service import (
    obtener_portafolio_con_relaciones
)

# Importación de la lógica de extracción de metadatos (Guantelete de 3 motores).
from app.etl.extract.asset_metadata_extractor import AssetMetadataExtractor

# Importación de excepciones personalizadas.
from ...exceptions import (
    RecursoNoEncontrado
)


class ETLService:
    """
    Coordina el ciclo de vida de la identificación de activos para un portafolio.
    """

    def __init__(self):
        # Herramienta robusta para información descriptiva (metadatos)
        self.metadata_extractor = AssetMetadataExtractor()

    def ejecutar_extraccion(self, portafolio_id: int):
        """
        Orquestador principal enfocado en la fase de Metadata.
        """
        db = SessionLocal()
        portafolio_id = int(portafolio_id)

        try:
            # 1. Recupera el objeto portafolio con sus activos vinculados.
            portafolio = obtener_portafolio_con_relaciones(db, portafolio_id)

            if not portafolio:
                raise RecursoNoEncontrado("Portafolio", portafolio_id)

            total_activos, exitosos = self.ejecutar_fase_metadata(db, portafolio)

            tasa_exito = (exitosos / total_activos) if total_activos > 0 else 0

            if tasa_exito >= 0.8:
                portafolio.isETL = True
                db.add(portafolio)
                print("✅ Umbral del 80% alcanzado. Portafolio marcado como listo")
            else:
                portafolio.isETL = False
                db.add(portafolio)
                print("⚠️ Umbral del 80% NO alcanzado.")

            portafolio.isETL = True
            db.add(portafolio)

            # 3. Confirmación final de la transacción.
            db.commit()
            print(f"Proceso de metadata finalizado para el portafolio {portafolio_id}")

        except Exception as e:
            db.rollback()
            print(f"❌ Error crítico en el proceso ETL: {e}")
            raise e

        finally:
            db.close()

    def ejecutar_fase_metadata(self, db, portafolio):
        """
        Lógica de Enriquecimiento:
        - Itera activos sin información completa.
        - Agota los motores de búsqueda (cascada).
        - Realiza persistencia atómica por activo.
        """
        print("\n=== INICIANDO FASE 1: ACTUALIZACIÓN DE METADATA ===")

        total = len(portafolio.activos)
        exitosos = 0

        for pa in portafolio.activos:
            activo = pa.activo
            ticker = activo.ticker

            ya_identificado = (
                activo.nombre
                and activo.nombre != ticker
                and activo.mercado
            )

            if ya_identificado:
                print(f"✔️ Activo {ticker} ya identificado previamente.")
                exitosos += 1
                continue

            print(f"🔍 Buscando identidad para: {ticker}...")

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
                    print(f"  ✨ Encontrado: {activo.nombre} ({activo.tipo_activo})")
                else:
                    print(f"No se pudo recuperar información para {ticker}")

            except Exception as e:
                # Si un activo falla catastróficamente, el bucle sigue con los demás
                print(f"  🚨 Error procesando {ticker}: {e}")

            # Pausa aleatoria para mimetizar comportamiento humano y evitar baneos de IP
            time.sleep(random.uniform(1.5, 3.0))

        print("=== FASE 1 COMPLETADA ===\n")
        return total, exitosos

    def _obtener_fechas(self, portafolio):
        """
        Helper para obtener fechas (se mantiene por compatibilidad, aunque no se use en
        esta fase).
        """
        if not portafolio.configuracion:
            raise RecursoNoEncontrado(
                "Configuración de Portafolio", portafolio.id_portafolio
            )

        config = portafolio.configuracion
        return config.fecha_inicio, config.fecha_fin
