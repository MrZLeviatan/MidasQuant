"""
Algoritmo de detección de días consecutivos al alza.

Responsabilidades:
- Detectar secuencias consecutivas de crecimiento.
- Implementar sliding window.
- Calcular métricas del patrón.
"""


def detectar_dias_consecutivos_alza(
    serie_temporal: list[dict],
    minimo_dias: int = 3
) -> dict:
    """
    Detecta patrones consecutivos de subida.

    Un patrón alcista ocurre cuando:

        precio_actual > precio_anterior

    durante N días consecutivos.

    Complejidad Temporal: O(n) - Solo se recorre una vez la serie
        O(n)

    Complejidad Espacial: O(k) - Cantidad de patrones encontrados
    """

    # Validación básica
    if not serie_temporal:

        return {
            "frecuencia_patrones": 0,
            "racha_maxima": 0,
            "promedio_racha": 0,
            "patrones": []
        }

    patrones = []

    # Sliding Window
    inicio_racha = None
    longitud_racha = 1

    # Recorremos la serie
    for i in range(1, len(serie_temporal)):

        actual = serie_temporal[i]
        anterior = serie_temporal[i - 1]

        precio_actual = actual.get("close")
        precio_anterior = anterior.get("close")

        # Validación datos nulos
        if (
            precio_actual is None
            or precio_anterior is None
        ):

            # Reiniciar ventana
            inicio_racha = None
            longitud_racha = 1

            continue

        # Día alcista
        if precio_actual > precio_anterior:

            # Inicio de nueva racha
            if inicio_racha is None:

                inicio_racha = anterior["fecha"]

            longitud_racha += 1

        # Se rompe la racha
        else:

            # Validar tamaño mínimo
            if longitud_racha >= minimo_dias:

                patrones.append({
                    "fecha_inicio": inicio_racha,
                    "fecha_fin": anterior["fecha"],
                    "dias_consecutivos": longitud_racha
                })

            # Reiniciar ventana
            inicio_racha = None
            longitud_racha = 1

    # Caso borde:
    # Si termina alcista
    if longitud_racha >= minimo_dias:

        patrones.append({
            "fecha_inicio": inicio_racha,
            "fecha_fin": serie_temporal[-1]["fecha"],
            "dias_consecutivos": longitud_racha
        })

    frecuencia_patrones = len(patrones)

    # Sin patrones
    if frecuencia_patrones == 0:

        return {
            "frecuencia_patrones": 0,
            "racha_maxima": 0,
            "promedio_racha": 0,
            "patrones": []
        }

    # Métricas
    racha_maxima = max(
        patron["dias_consecutivos"]
        for patron in patrones
    )

    promedio_racha = sum(
        patron["dias_consecutivos"]
        for patron in patrones
    ) / frecuencia_patrones

    return {
        "frecuencia_patrones": frecuencia_patrones,
        "racha_maxima": racha_maxima,
        "promedio_racha": round(promedio_racha, 2),
        "patrones": patrones
    }
