"""
Servicio de aplicación para ejecución del proceso ETL.

Responsabilidad:
- Orquestar la extracción de datos financieros
- Coordinar acceso a BD
- Invocar el extractor
- Persistir datos RAW
"""

from app.database.connection import SessionLocal

from app.database.models import (
    Portafolio,
    PortafolioActivo,
    SerieTemporalRaw
)

from sqlalchemy.orm import joinedload

from app.etl.extract.market_data_extractor import ExtractorFinanciero


class ETLService:
    """
    Servicio de aplicación para ejecutar el proceso ETL completo.
    """

    def __init__(self):
        self.extractor = ExtractorFinanciero()

    def ejecutar_etl(self, portafolio_id: int):
        """
        Ejecuta el proceso ETL para un portafolio.

        Flujo:
        1. Obtener portafolio
        2. Obtener activos
        3. Obtener configuración (fechas)
        4. Iterar activos → extraer datos
        5. Persistir datos RAW
        6. Marcar ETL como ejecutado
        """
        db = SessionLocal()

        try:
            # =========================
            # 1. Obtener portafolio
            # =========================
            portafolio = db.query(Portafolio).options(
                joinedload(Portafolio.activos).joinedload(PortafolioActivo.activo),
                joinedload(Portafolio.configuraciones)
            ).filter(
                Portafolio.id_portafolio == portafolio_id
            ).first()

            if not portafolio:
                raise ValueError("Portafolio no encontrado")

            # =========================
            # 2. Validar configuración
            # =========================
            if not portafolio.configuraciones:
                raise ValueError("El portafolio no tiene configuración de análisis")

            config = portafolio.configuraciones[0]

            fecha_inicio = config.fecha_inicio
            fecha_fin = config.fecha_fin

            # =========================
            # 3. Iterar activos
            # =========================
            for pa in portafolio.activos:
                activo = pa.activo
                ticker = activo.ticker

                # =========================
                # 4. Extraer datos
                # =========================
                datos = self.extractor.extraer(
                    ticker,
                    fecha_inicio,
                    fecha_fin
                )

                # =========================
                # 5. Persistir datos RAW
                # =========================
                registros = []

                for fila in datos:
                    registros.append(
                        SerieTemporalRaw(
                            activo_id=activo.id_activo,
                            fecha=fila["fecha"],
                            open=fila["open"],
                            high=fila["high"],
                            low=fila["low"],
                            close=fila["close"],
                            volumen=fila["volumen"]
                        )
                    )

                # Inserción batch (mejor rendimiento)
                db.bulk_save_objects(registros)
                db.commit()

            # =========================
            # 6. Marcar ETL ejecutado
            # =========================
            portafolio.isETL = True
            db.commit()

            return True

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()
