"""
Configuración del entorno de pruebas.

Aquí creamos una base de datos temporal (en memoria)
para que los tests no afecten la base de datos real.
"""
# Importar pytest para crear fixtures
import pytest

# Importar SQLAlchemy para manejar la base de datos temporal
from sqlalchemy import create_engine

# Importar sessionmaker para crear sesiones de base de datos
from sqlalchemy.orm import sessionmaker

# Importar Base (todas las tablas)
from app.database.models import Base


# 1. CREAR BASE DE DATOS TEMPORAL

# Esto crea una BD en memoria RAM (NO archivo, NO persistente)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Crear el motor de base de datos con la URL de SQLite en memoria
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# 2. CREAR LAS TABLAS
Base.metadata.create_all(bind=engine)


# 3. CREAR SESIÓN DE PRUEBA
TestingSessionLocal = sessionmaker(bind=engine)


# 4. CREAR FIXTURE (MUY IMPORTANTE)
@pytest.fixture
def db_session():
    """
    Crea una sesión limpia para cada test.

    - Se abre antes del test
    - Se cierra después del test
    """
    session = TestingSessionLocal()
    try:
        # Aquí se usa en el test
        yield session
    finally:
        session.close()
