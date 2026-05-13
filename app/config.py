"""
Objetivos:
    - Definir la configuración de conexión a la base de datos.
    - Permitir la configuración según el entorno (desarrollo vs producción)
    - Mantener la portabilidad entre SQLite y PostgreSQL
        sin cambios en el código de la aplicación.
"""


import os
# Permite acceder a variables de entorno del sistema operativo.

from dotenv import load_dotenv
# Lectura del .ENV

load_dotenv()
# Lee el .env en local, en Render usa las vars reales automáticamente


# Obtiene la variable de entorno DATABASE_URL si existe.
# Si no está definida, usa SQLite como base de datos por defecto (desarrollo).

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data/dev.db"
)
