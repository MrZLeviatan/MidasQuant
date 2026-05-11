"""
Servicios de comparación de series temporales.

Responsabilidades:
- Obtener series temporales limpias.
- Filtrar por rango temporal del portafolio.
- Preparar datos para visualización y algoritmos.
"""

# Sesión de BD
from app.database.connection import SessionLocal

# ORM
from app.database.models import (
    Activo,
    SerieTemporalLimpia,
    ConfiguracionAnalisis
)

# Excepciones
from app.exceptions import (
    RecursoNoEncontradoError,
    InsuficientesDatosComunesError,
    DominioError
)


def obtener_series_comparacion(
    portafolio_id: int,
    ticker_1: str,
    ticker_2: str
):
    """
    Obtiene dos series temporales limpias y alineadas temporalmente.

    Reglas:
    - Las series se filtran por el rango temporal
        del portafolio seleccionado.

    Complejidad: O(n log n):
        1. Crear los sets y la intersección (&) es O(n).
        2. La función 'sorted()' sobre las fechas comunes aplica Timsort,
            lo que introduce el factor logarítmico dominante en el proceso.
    """

    # Crear sesión BD
    db = SessionLocal()

    try:

        # Parsear de String a int (Error raro con el Streamlit)
        portafolio_id = int(portafolio_id)

        # Se obtiene la configuración del portafolio para conocer el rango temporal
        configuracion = db.query(
            ConfiguracionAnalisis
        ).filter(
            ConfiguracionAnalisis.portafolio_id == portafolio_id
        ).first()

        # Validar configuración
        if not configuracion:
            raise RecursoNoEncontradoError(
                message="El portafolio no posee configuración de análisis.",
                code="CONFIGURACIÓN_NO_ENCONTRADA",
                detail=f"Portafolio ID: {portafolio_id}"
            )

        # Rango temporal del portafolio
        fecha_inicio = configuracion.fecha_inicio
        fecha_fin = configuracion.fecha_fin

        # BUSCAR ACTIVO 1
        activo_1 = db.query(Activo).filter(
            Activo.ticker == ticker_1
        ).first()

        if not activo_1:
            raise RecursoNoEncontradoError(
                message="El activo no fue encontrado.",
                code="ACTIVO_NO_ENCONTRADO",
                detail=f"Ticker: {ticker_1}"
            )

        # BUSCAR ACTIVO 2
        activo_2 = db.query(Activo).filter(
            Activo.ticker == ticker_2
        ).first()

        if not activo_2:
            raise RecursoNoEncontradoError(
                message="El activo no fue encontrado.",
                code="ACTIVO_NO_ENCONTRADO",
                detail=f"Ticker: {ticker_2}"
            )

        # Obtener serie temporal limpia del activo 1
        serie_1 = db.query(SerieTemporalLimpia).filter(
            SerieTemporalLimpia.activo_id == activo_1.id_activo
        ).filter(
            SerieTemporalLimpia.fecha >= fecha_inicio
        ).filter(
            SerieTemporalLimpia.fecha <= fecha_fin
        ).order_by(
            SerieTemporalLimpia.fecha.asc()
        ).all()

        # Obtener serie temporal limpia del activo 2
        serie_2 = db.query(SerieTemporalLimpia).filter(
            SerieTemporalLimpia.activo_id == activo_2.id_activo
        ).filter(
            SerieTemporalLimpia.fecha >= fecha_inicio
        ).filter(
            SerieTemporalLimpia.fecha <= fecha_fin
        ).order_by(
            SerieTemporalLimpia.fecha.asc()
        ).all()

        # MAPEO A DICCIONARIOS PARA BÚSQUEDA O(1)
        if not serie_1:
            raise RecursoNoEncontradoError(
                message="El activo no fue encontrado.",
                code="ACTIVO_NO_ENCONTRADO",
                detail=f"Ticker: {ticker_1}"
            )

        if not serie_2:
            raise RecursoNoEncontradoError(
                message="El activo no fue encontrado.",
                code="ACTIVO_NO_ENCONTRADO",
                detail=f"Ticker: {ticker_2}"
            )

        # Convertimos las listas en mapas {fecha: precio} para cruzar datos
        datos_1 = {
            item.fecha: item.close
            for item in serie_1
        }

        datos_2 = {
            item.fecha: item.close
            for item in serie_2
        }

        # Solo compara días donde ambos activos tengan cotización (evita ruidos).
        fechas_comunes = sorted(
            set(datos_1.keys()) & set(datos_2.keys())
        )

        # Mínimo 2 puntos para poder trazar una línea/tendencia.
        if len(fechas_comunes) < 2:
            raise InsuficientesDatosComunesError(puntos_encontrados=len(fechas_comunes))

        """
        Normalización financiera base 100

        - Se toma el primer precio común como base (100) y se calcula el valor relativo
            para cada fecha posterior.
        - Esto permite comparar la evolución porcentual de ambos activos
            independientemente de sus precios absolutos.
        """
        precio_base_1 = datos_1[fechas_comunes[0]]
        precio_base_2 = datos_2[fechas_comunes[0]]

        # CONSTRUCCIÓN DEL DATASET FINAL
        resultado = []

        for fecha in fechas_comunes:

            precio_1 = datos_1[fecha]
            precio_2 = datos_2[fecha]

            # Evitar divisiones inválidas
            if precio_base_1 == 0 or precio_base_2 == 0:
                continue

            # Normalización financiera base 100
            normalizado_1 = (
                precio_1 / precio_base_1
            ) * 100

            normalizado_2 = (
                precio_2 / precio_base_2
            ) * 100

            # Precisión financiera de 4 decimales.
            resultado.append({
                "fecha": fecha,
                ticker_1: round(normalizado_1, 4),
                ticker_2: round(normalizado_2, 4)
            })

        # Verificación final de integridad del dataset generado.
        if not resultado:
            raise DominioError(
                code="SERIE_COMPARATIVA_VACIA",
                message=(
                    "No fue posible construir "
                    "la serie temporal comparativa."
                )
            )

        return resultado

    finally:
        db.close()
