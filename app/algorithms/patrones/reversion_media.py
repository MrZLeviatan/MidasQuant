"""
Algoritmo de detección de reversión a la media.

Responsabilidades:
- Detectar desviaciones significativas del promedio móvil.
- Identificar retorno del precio a la media.
- Usar sliding window para análisis local.
"""

from collections import deque


def detectar_reversion_media(
    serie_temporal: list[dict],
    ventana: int = 5,
    umbral_salida: float = 0.03,
    umbral_retorno: float = 0.015
) -> dict:
    """
    Detecta patrones de reversión a la media.

    Lógica:
    - Si el precio se aleja de la media móvil > umbral_salida
    - y luego regresa dentro de umbral_retorno
    => se detecta un patrón válido
    """

    if len(serie_temporal) < ventana:
        return {
            "frecuencia": 0,
            "patrones": []
        }

    precios = [p["close"] for p in serie_temporal]
    fechas = [p["fecha"] for p in serie_temporal]

    patrones = []
    ventana_previa = deque(maxlen=ventana)

    estado_salida = None  # (indice, precio_base, media)

    for i in range(len(precios)):

        ventana_previa.append(precios[i])

        if len(ventana_previa) < ventana:
            continue

        media = sum(ventana_previa) / ventana

        precio = precios[i]

        desviacion = abs(precio - media) / media

        # Fase 1: salida de la media
        if estado_salida is None and desviacion > umbral_salida:

            estado_salida = {
                "indice": i,
                "precio_base": precio,
                "media": media,
                "fecha_inicio": fechas[i]
            }

        # Fase 2: retorno a la media
        elif estado_salida is not None:

            if desviacion < umbral_retorno:

                patrones.append({
                    "fecha_inicio": estado_salida["fecha_inicio"],
                    "fecha_fin": fechas[i],
                    "duracion": i - estado_salida["indice"],
                    "tipo": "reversion_media"
                })

                estado_salida = None

    return {
        "frecuencia": len(patrones),
        "patrones": patrones
    }
