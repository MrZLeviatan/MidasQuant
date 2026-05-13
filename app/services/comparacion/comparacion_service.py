"""
Servicios de comparación de series temporales.

Responsabilidades:
- Obtener series temporales limpias.
- Preparar datos para visualización y algoritmos.
- Orquestar el análisis comparativo entre activos con diferentes algoritmos.
"""

# Sesión de bd
from app.database.connection import SessionLocal

# ORM
from app.database.models import (
    Activo,
    SerieTemporalLimpia,
    ConfiguracionAnalisis
)

# Uso de excepciones personalizadas
from app.exceptions import (
    RecursoNoEncontradoError,
    InsuficientesDatosComunesError,
    ObjetoVacio
)

# Algoritmos
from app.algorithms.similitud.distancia_euclidiana import (
    calcular_distancia_euclidiana
)

from app.algorithms.similitud.correlacion_pearson import (
    calcular_correlacion_pearson
)

from app.algorithms.similitud.dtw import (
    calcular_dtw
)

from app.algorithms.similitud.similitud_coseno import (
    calcular_similitud_coseno
)


def obtener_series_comparacion(
    portafolio_id: int,
    ticker_1: str,
    ticker_2: str
):
    """
    Obtiene dos series limpias y alineadas temporalmente.

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

        # Validar configuración (Validar fecha inicio/fin)
        if not configuracion:
            raise RecursoNoEncontradoError(
                message="El portafolio no posee configuración de análisis.",
                code="CONFIGURACIÓN_NO_ENCONTRADA",
                detail=f"Portafolio ID: {portafolio_id}"
            )

        # Rango temporal del portafolio
        fecha_inicio = configuracion.fecha_inicio
        fecha_fin = configuracion.fecha_fin

        # Buscar el Activo 1 por su ticker
        activo_1 = db.query(Activo).filter(
            Activo.ticker == ticker_1
        ).first()

        # Validar que el activo 1 exista
        if not activo_1:
            raise RecursoNoEncontradoError(
                message="El activo no fue encontrado.",
                code="ACTIVO_NO_ENCONTRADO",
                detail=f"Ticker: {ticker_1}"
            )

        # Buscar el Activo 2 por su ticker
        activo_2 = db.query(Activo).filter(
            Activo.ticker == ticker_2
        ).first()

        # Validar que el activo 2 exista
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

        # Verificar que ambas series tengan datos
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
            if item.close is not None
        }

        datos_2 = {
            item.fecha: item.close
            for item in serie_2
            if item.close is not None
        }

        # Solo compara días donde ambos activos tengan cotización (evita ruidos).
        fechas_comunes = sorted(
            set(datos_1.keys()) & set(datos_2.keys())
        )

        # Validación de al menos 2 puntos para calcular variaciones o tendencias.
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

        # Validación de protección para los datos base
        if precio_base_1 is None or precio_base_2 is None:
            raise ObjetoVacio(
                objeto_nombre="precio_base_normalizacion"
            )

        # Construcción de la serie comparativa con precisión financiera de 4 decimales.
        resultado = []

        # Construcción del dataset normalizado
        for fecha in fechas_comunes:

            precio_1 = datos_1[fecha]
            precio_2 = datos_2[fecha]

            # Evitar divisiones inválidas
            if precio_base_1 == 0 or precio_base_2 == 0:
                continue

            """
            Normalización: (Precio Actual / Precio en T0) * 100
            Esto iguala la linea de salida de ambos activos a 100,
                permitiendo comparar su evolución relativa.
            """
            normalizado_1 = (
                precio_1 / precio_base_1
            ) * 100

            normalizado_2 = (
                precio_2 / precio_base_2
            ) * 100

            # Redondea a 4 decimales para balancear precisión y ligereza de datos.
            resultado.append({
                "fecha": fecha,
                ticker_1: round(normalizado_1, 4),
                ticker_2: round(normalizado_2, 4)
            })

        # Verificación final de integridad del dataset generado.
        if not resultado:
            raise ObjetoVacio(
                objeto_nombre="serie_comparativa"
            )

        # ALGORITMOS DE SIMILITUD

        # Aplicación de la distancia euclidiana
        distancia_euclidiana = calcular_distanciaec(
            resultado, ticker_1, ticker_2
        )

        correlacion_pearson = calcular_metricas_pearson(
            resultado, ticker_1, ticker_2
        )

        dtw = calcular_metricas_dtw(
            resultado, ticker_1, ticker_2
        )

        similitud_coseno = calcular_metricas_coseno(
            resultado, ticker_1, ticker_2
        )

        # Retorno Final de mapeo de distintos resultados
        return {
            "series": resultado,
            "metricas": {
                "distancia_euclidiana": distancia_euclidiana,
                "correlacion_pearson": correlacion_pearson,
                "dtw": dtw,
                "similitud_coseno": similitud_coseno
            }
        }

    # Cierre de sesión de la BD.
    finally:
        db.close()


def calcular_distanciaec(
        datos_series: list[dict],
        ticker_1: str,
        ticker_2: str,
) -> dict:
    """
    Calcular la métrica de la distancia euclidiana.

    Complejidad: O(n)
    """

    # Se convierten en vectores numéricos las series temporales
    vector_1 = [
        item[ticker_1]
        for item in datos_series
    ]

    vector_2 = [
        item[ticker_2]
        for item in datos_series
    ]

    # Aplicamos la distancia euclidiana
    distancia_euclidiana = calcular_distancia_euclidiana(
        vector_1,
        vector_2
    )

    return distancia_euclidiana


def calcular_metricas_pearson(
        datos_series: list[dict],
        ticker_1: str,
        ticker_2: str,
) -> dict:
    """
    Calcular la métrica de correlación de Pearson.

    Complejidad: O(n)
    """

    serie_1 = []
    serie_2 = []

    for fila in datos_series:

        serie_1.append(fila[ticker_1])
        serie_2.append(fila[ticker_2])

    correlacion = calcular_correlacion_pearson(
        serie_1,
        serie_2
    )

    return correlacion


def calcular_metricas_dtw(
    datos_series: list[dict],
    ticker_1: str,
    ticker_2: str
) -> dict:
    """
    Calcula las métricas DTW.

    Complejidad: O(n²)
    """

    serie_1 = []
    serie_2 = []

    for fila in datos_series:

        serie_1.append(
            fila[ticker_1]
        )

        serie_2.append(
            fila[ticker_2]
        )

    return calcular_dtw(
        serie_1,
        serie_2
    )


def calcular_metricas_coseno(
    datos_series: list[dict],
    ticker_1: str,
    ticker_2: str,
) -> dict:
    """
    Calcula similitud por coseno.

    Complejidad: O(n)
    """

    serie_1 = []
    serie_2 = []

    for fila in datos_series:

        valor_1 = fila.get(ticker_1)
        valor_2 = fila.get(ticker_2)

        if valor_1 is None or valor_2 is None:
            continue

        serie_1.append(valor_1)
        serie_2.append(valor_2)

    return calcular_similitud_coseno(
        serie_1,
        serie_2
    )
