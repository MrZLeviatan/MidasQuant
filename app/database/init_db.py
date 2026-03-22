"""
Inicializa la base de datos.

Objetivos: Crear todas las tablas definidas en models.py
"""

# La conexión entre la aplicación y la base de datos
from database.connection import engine

# Importar la clase Base para crear las tablas a partir de los modelos definidos
from database.models import Base


def init_database():
    """
    Inicializa la base de datos creando las tablas definidas en los modelos.
    - Si las tablas ya existen, no las recrea.
    - Si no existen, las crea automáticamente.
    """

    # Crea las tablas en la base de datos usando el engine de conexión
    Base.metadata.create_all(bind=engine)


# Se ejecuta al unísono con el script principal
if __name__ == "__main__":
    init_database()
    print("Base de datos inicializada correctamente.")
