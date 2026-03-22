"""
Definición de modelos ORM del sistema.

Objetivos:
- Representar entidades del dominio.
- Definir relaciones entre tablas.
- Permitir generación automática del esquema en la base de datos.
"""

# Importación de tipos de columnas
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime

# Para timestamps (Guardar fecha y hora exactamente)
from datetime import datetime

# Para definir relaciones entre tablas
from sqlalchemy.orm import declarative_base, relationship


"""
Base es la clase padre de todos los modelos.

Cuando se hace: class Activo(Base): se dice que Activo es una tabla en la base de datos.

Internamente:
- Registra metadata
- Permite a SQLAlchemy saber qué tablas existen
"""
Base = declarative_base()


# Tabla: Activos
class Activo(Base):
    """
    Representa un activo financiero (acción o ETF).
    """
    __tablename__ = "activo"

    # Identificador único interno (más eficiente para búsquedas)
    id_activo = Column(Integer, primary_key=True, index=True)

    # Código del activo (ticker), único, no nulo e indexado para búsquedas rápidas
    ticker = Column(String, unique=True, nullable=False, index=True)

    # Nombre descriptivo
    nombre = Column(String, nullable=True)

    # Tipo de activo (STOCK, ETF)
    tipo_activo = Column(String, nullable=True)

    # Relación con precios
    precios = relationship("SerieTemporal", back_populates="activo")

    """
    No se tiene relación directa con portafolio_activo porque no se va acceder desde el
    activo hacia los portafolios, solo al revés (desde el portafolio hacia los activos)
    """


# Tabla: portfolios
class Portafolio(Base):
    """
    Representa un portafolio de activos configurado por el usuario.
    """
    __tablename__ = "portafolio"

    id_portafolio = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)

    # Fecha de creación automática
    fecha_creacion = Column(DateTime, default=datetime)

    """
    relationship: permite definir relaciones entre tablas sin escribir SQL.
    back_populates: indica que esta relación es bidireccional
    """
    # Relación con activos (N:M)
    activos = relationship("PortafolioActivo", back_populates="portafolio")

    # Relación con configuraciones
    configuraciones = relationship("ConfiguracionAnalisis", back_populates="portafolio")


# Tabla intermedia entre Portafolio y Activos (N:M)
class PortafolioActivo(Base):
    """
    Relación muchos a muchos entre portafolios y activos.
    """
    __tablename__ = "portafolio_activo"

    id_portafolio_activo = Column(Integer, primary_key=True, index=True)

    # FK hacia Portafolio
    portafolio_id = Column(Integer, ForeignKey("portafolio.id_portafolio"))

    # FK hacia Activo
    activo_id = Column(Integer, ForeignKey("activo.id_activo"))

    """
    - Cada registro de esta tabla está asociado a un portafolio
    - El back_populates indica que desde el portafolio se puede acceder a los activos
    asociados
    """
    portafolio = relationship("Portafolio", back_populates="activos")

    # Cada registro de esta tabla está asociado a un activo
    activo = relationship("Activo")


# Tabla: Configuración de análisis de Portafolio
class ConfiguracionAnalisis(Base):
    """
    Configuración del análisis (rango de fechas).
    """
    __tablename__ = "configuracion_analisis"

    id_configuracion = Column(Integer, primary_key=True, index=True)

    portafolio_id = Column(Integer, ForeignKey("portafolio.id_portafolio"))

    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)

    portafolio = relationship("Portafolio", back_populates="configuraciones")


# Tabla: Serie temporal de precios de un activo
class SerieTemporal(Base):
    """
    Serie temporal de precios de un activo.
    """
    __tablename__ = "serie_temporal"

    id_serie = Column(Integer, primary_key=True, index=True)

    activo_id = Column(Integer, ForeignKey("activo.id_activo"), index=True)

    fecha = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volumen = Column(Float)

    activo = relationship("Activo", back_populates="precios")
