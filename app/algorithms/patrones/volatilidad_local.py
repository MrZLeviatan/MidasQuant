"""
Algoritmo de detección de volatilidad alta consecutiva.

Responsabilidades:
- Detectar ventanas consecutivas con cambios porcentuales altos.
- Implementar sliding window.
- Medir frecuencia del patrón.
"""


def detectar_volatilidad_alta(
    precios: list[float],
    umbral_porcentual: float = 2.0,
    ventana: int = 3
) -> dict:
    """
    Analiza una serie de precios para encontrar rachas de cambios bruscos
        (positivos o negativos) que superen un umbral definido.

    Complejidad Temporal: O(n) - Solo se recorre una vez la serie
        O(n)

    Complejidad Espacial: O(k) - Cantidad de patrones encontrados
    """

    # Validación mínima si no hay suficientes datos para formar una racha
    if len(precios) < ventana + 1:

        return {
            "patrones_detectados": 0,
            "indices": [],
            "frecuencia": "Baja"
        }

    # Lista de días volátiles
    volatilidades = []

    # Calcular variación porcentual diaria
    for i in range(1, len(precios)):

        precio_anterior = precios[i - 1]
        precio_actual = precios[i]

        # Evitar división inválida
        if precio_anterior == 0:
            volatilidades.append(False)
            continue

        # Cálculo de retorno simple convertido a porcentaje
        cambio = (
            (precio_actual - precio_anterior)
            / precio_anterior
        ) * 100

        # Día volátil (si rompe el umbral)
        volatilidades.append(
            abs(cambio) >= umbral_porcentual
        )

    patrones = []

    # Sliding Window!!
    # Recorre el mapa buscando secuencias ininterrumpidas
    for i in range(
        len(volatilidades) - ventana + 1
    ):
        # Extrae un subsegmento de la lista según el tamaño de racha requerido
        ventana_actual = volatilidades[
            i:i + ventana
        ]

        # Todos los días deben ser volátiles para validar la racha
        if all(ventana_actual):
            # Guarda el índice inicial del periodo inestable
            patrones.append(i)

    cantidad = len(patrones)

    # Clasificación sencilla
    if cantidad >= 10:
        frecuencia = "Alta"

    elif cantidad >= 5:
        frecuencia = "Moderada"

    else:
        frecuencia = "Baja"

    return {
        "patrones_detectados": cantidad,
        "indices": patrones,
        "frecuencia": frecuencia
    }
