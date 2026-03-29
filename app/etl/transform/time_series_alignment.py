"""
Módulo de transformación para alineación de series temporales (HU07)

Responsabilidad:
- Construir una línea temporal común (master timeline)
- Alinear múltiples activos sobre esa línea
- Marcar datos faltantes como None

No realiza persistencia.
No aplica limpieza (forward fill, interpolación, etc).
"""

# Se importa el modelo de las SeriesTemporalRaw
from app.database.models import SerieTemporalRaw


def alinear_series_temporales(db, activos, fecha_inicio, fecha_fin):
    """
    Alinea las series temporales de múltiples activos.

    Complejidad: O(n^2) por las iteraciones anidadas.
    """

    # Obtener ID de los Activos
    activos_ids = [a.id_activo for a in activos]

    if not activos_ids:
        return {}

    """
    Obtener las fechas únicas (timeline aislado).
    - Consulta a la DB para traer solo la columna 'fecha' de todos los
        registros del portafolio.
    - '.distinct()' elimina duplicados a nivel de SQL para que no traiga
        miles de veces la misma fecha.
    """
    fechas = db.query(SerieTemporalRaw.fecha).filter(
        SerieTemporalRaw.activo_id.in_(activos_ids),
        SerieTemporalRaw.fecha >= fecha_inicio,
        SerieTemporalRaw.fecha <= fecha_fin
    ).distinct().all()

    """
    - Como SQLAlchemy devuelve una lista de tuplas [(fecha1,), (fecha2,)], usamos una
        "comprensión de conjunto" {f[0] for f in fechas} para extraer el valor y
        asegurar unicidad.
    - Luego 'sorted()' ordena cronológicamente (de más antigua a más reciente).

    Convertimos [(fecha,), (fecha,)...] → set → lista ordenada
    MASTER TIMELINE!!!
    """
    fechas_unicas = sorted({f[0] for f in fechas})

    # Diccionario vacío donde guardaremos los resultados finales agrupados por Ticker.
    resultado = {}

    #  Iterar sobre cada activo
    for activo in activos:

        """
        Traer datos del activo
        - Trae los precios de cierre y sus fechas para EL ACTIVO ACTUAL.
        - Filtra por 'id_activo' para no traer datos de otros activos.
        - Se trae el objeto completo (SerieTemporalRaw)
        """
        datos = db.query(
            SerieTemporalRaw
        ).filter(
            SerieTemporalRaw.activo_id == activo.id_activo,
            SerieTemporalRaw.fecha >= fecha_inicio,
            SerieTemporalRaw.fecha <= fecha_fin
        ).all()

        """
        Convertir a diccionario para acceso O(1)
        - Transforma la lista de la DB en un mapa (Hash Map).
        - Esto es clave para el rendimiento: permite preguntar
            "¿Qué precio hubo en esta fecha?" y obtener la respuesta
            instantáneamente sin buscar en toda la lista.'
        - Mapeo de fechas -> Objeto Completo
        """
        mapa_datos = {obj.fecha: obj for obj in datos}

        # Lista temporal para guardar la serie de tiempo completa y "rellenada"
        serie_alineada = []

        # Recorre la "Línea de Tiempo Maestra" que creamos
        for fecha in fechas_unicas:
            """
            Buscar la fecha actual en los datos que el activo realmente tiene.
            -.get(fecha,None) intenta obtener el precio; si no existe en esa fecha,
                devuelve None.
            """
            obj_raw = mapa_datos.get(fecha)

            # Agrega un diccionario con la fecha y el valora la lista del activo.
            serie_alineada.append({
                "fecha": fecha,
                "valor": obj_raw.close if obj_raw else None,
                "obj_sql": obj_raw
            })
        # Guarda la lista en el diccionario principal usando el Ticker como clave.
        resultado[activo.ticker] = serie_alineada

    # Retorna el diccionario con todos los activos ya sincronizados temporalmente.
    return resultado
