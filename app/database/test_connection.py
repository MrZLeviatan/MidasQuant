"""
Script de prueba para verificar conexión a la base de datos.
Objetivos:
- Forzar la creación del archivo SQLite
- Validar que el engine funciona correctamente
"""

# Importamos el engine (esto ya configura la conexión)
from app.database.connection import engine

# Importamos herramienta para ejecutar SQL directo
from sqlalchemy import text


def test_db_connection():
    """
    Ejecuta una consulta simple para validar la conexión.
    """

    # Se abre una conexión con la base de datos
    with engine.connect() as connection:

        # Ejecutamos una consulta mínima válida
        result = connection.execute(text("SELECT 1"))

        # Obtenemos el resultado
        for row in result:
            print("Resultado de prueba:", row[0])


if __name__ == "__main__":
    test_db_connection()