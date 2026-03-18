"""
Objetivos:
    - Crear el motor SQLAlchemy para gestionar la conexión a la base de datos.
    - Proporcionar una fábrica de sesiones para interactuar con la bd.
    - Mantener la portabilidad entre SQLite y PostgreSQL sin cambios en
        el código de la aplicación.
"""
import os

# Función central para crear el motor de conexión.
from sqlalchemy import create_engine

# Permite crear sesiones de base de datos.
from sqlalchemy.orm import sessionmaker

# Importa configuración centralizada.
from app.config import DATABASE_URL

# Asegurar que el directorio de SQLite existe
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)

    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


# El engine es la interfaz principal con la base de datos.
# Gestiona conexiones y ejecución de SQL.
engine = create_engine(
    DATABASE_URL,
    echo=False  # Deshabilitar el registro de SQL en la consola
)


# SessionLocal es una fábrica de sesiones.
# Cada sesión representa una transacción independiente.
SessionLocal = sessionmaker(bind=engine)
