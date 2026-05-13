"""
Servicios de análisis de patrones financieros.

Responsabilidades:
- Obtener series temporales limpias.
- Ejecutar algoritmos de detección de patrones.
- Consolidar resultados para visualización.
"""

# Sesión BD
from app.database.connection import SessionLocal


# ORM
from app.database.models import (
    Portafolio,
    PortafolioActivo,
    SerieTemporalLimpia,
    ConfiguracionAnalisis
)

# Excepciones
from app.exceptions import (
    RecursoNoEncontradoError,
    ObjetoVacio
)

# Algoritmos
from app.algorithms.patrones.dias_consecutivos_alza import (
    detectar_dias_consecutivos_alza
)

from app.algorithms.patrones.volatilidad_local import (
    detectar_volatilidad_alta
)

from app.algorithms.patrones.reversion_media import (
    detectar_reversion_media
)

from app.algorithms.patrones.desviacion_estandar import (
    calcular_desviacion_estandar
)


def analizar_patrones_portafolio(
    portafolio_id: int
) -> list[dict]:
    """
    Ejecuta análisis de patrones alcistas
    para todos los activos de un portafolio.
    """

    # Crear sesión
    db = SessionLocal()

    try:

        # Validación ID
        portafolio_id = int(portafolio_id)

        # Buscar portafolio
        portafolio = db.query(
            Portafolio
        ).filter(
            Portafolio.id_portafolio == portafolio_id
        ).first()

        # Validación de portafolio no encontrado
        if not portafolio:

            raise RecursoNoEncontradoError(
                message="Portafolio no encontrado.",
                code="PORTAFOLIO_NO_ENCONTRADO",
                detail=f"ID: {portafolio_id}"
            )

        # Obtener configuración temporal
        configuracion = db.query(
            ConfiguracionAnalisis
        ).filter(
            ConfiguracionAnalisis.portafolio_id == portafolio_id
        ).first()

        if not configuracion:

            raise RecursoNoEncontradoError(
                message="Configuración no encontrada.",
                code="CONFIGURACION_NO_ENCONTRADA",
                detail=f"Portafolio ID: {portafolio_id}"
            )

        fecha_inicio = configuracion.fecha_inicio
        fecha_fin = configuracion.fecha_fin

        # Obtener activos del portafolio
        activos = db.query(
            PortafolioActivo
        ).filter(
            PortafolioActivo.portafolio_id == portafolio_id
        ).all()

        if not activos:

            raise ObjetoVacio(
                objeto_nombre="activos_portafolio"
            )

        resultados = []

        # Analizar cada activo del portafolio
        for relacion in activos:

            activo = relacion.activo

            # Obtener serie limpia
            serie = db.query(
                SerieTemporalLimpia
            ).filter(
                SerieTemporalLimpia.activo_id == activo.id_activo
            ).filter(
                SerieTemporalLimpia.fecha >= fecha_inicio
            ).filter(
                SerieTemporalLimpia.fecha <= fecha_fin
            ).order_by(
                SerieTemporalLimpia.fecha.asc()
            ).all()

            # Ignorar activos sin datos
            if not serie:
                continue

            # Transformar serie para algoritmo
            precios = []
            fechas = []

            serie_algoritmo = []

            # Transformación a diccionario con los resultados
            for item in serie:

                # Validar close
                if item.close is None:
                    continue

                # Creación de la biblia
                precios.append(item.close)
                fechas.append(item.fecha)

                serie_algoritmo.append({
                    "fecha": item.fecha,
                    "close": item.close
                })

            # Validación mínima
            if len(precios) < 5:
                continue

            # Ejecutar patrón Dias ALza
            resultado_patrones = (
                detectar_dias_consecutivos_alza(
                    serie_algoritmo
                )
            )

            # Ejecutar patrón de revision
            resultado_reversion = detectar_reversion_media(
                serie_algoritmo
            )

            # Ejecutar la volatilidad
            resultado_volatilidad = detectar_volatilidad_alta(
                precios, 2.0 , 3
            )

            # EJecutar la desviación estandar
            desviacion_estandar = calcular_desviacion_estandar(precios)

            # Implementación de clasificación de riesgo
            volatilidad_promedio = sum(
                abs(precios[i] - precios[i - 1]) / precios[i - 1]
                for i in range(1, len(precios))
            ) / max(len(precios) - 1, 1) * 100

            patrones_vol = resultado_volatilidad.get("patrones_detectados", 0)

            risk_score = calcular_risk_score(
                desviacion_estandar,
                volatilidad_promedio,
                patrones_vol
            )

            riesgo = clasificar_por_score(risk_score)

            # Consolidar resultado en una misma biblia
            resultados.append({

                "ticker": activo.ticker,
                "nombre": activo.nombre,
                "tipo_activo": activo.tipo_activo,
                "mercado": activo.mercado,
                "precios": precios,
                "fechas": fechas,
                "desviacion_estandar": desviacion_estandar,
                "riesgo": riesgo,
                "analisis_patrones": resultado_patrones,
                "analisis_volatilidad": resultado_volatilidad,
                "analisis_reversion": resultado_reversion,
                "risk_score": risk_score,
                "riesgo": riesgo
            })

        # Validación final
        if not resultados:

            raise ObjetoVacio(
                objeto_nombre="resultados_patrones"
            )

        return resultados

    finally:

        db.close()


def calcular_risk_score(desviacion, volatilidad, patrones_volatilidad):
    """
    Calcula score de riesgo (0 - 100).

    Modelo:
        score = combinación ponderada de:
        - desviación estándar
        - volatilidad
        - eventos de volatilidad
    """

    score = (
        (desviacion * 10) + (volatilidad * 0.8) + (patrones_volatilidad * 2)
    )

    return round(min(score, 100), 2)


def clasificar_por_score(score):
    if score < 33:
        return "Conservador"
    elif score < 66:
        return "Moderado"
    else:
        return "Agresivo"
