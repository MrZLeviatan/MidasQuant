"""
Módulo de Auditoría de Calidad de Datos (HU08)

Responsabilidad:
- Analizar series temporales alineadas para detectar y clasificar problemas de calidad.
- Generar métricas porcentuales de calidad y un diagnóstico final para cada activo.
- Finalmente generar un "informe" porcentual y un diagnóstico sobre si los datos
de cada activo son lo suficientemente confiable para ser usado en el modelo.

Enfoque:
- No altera datos originales
- No elimina registros
- Solo clasifica y mide calidad
"""

# Importación para cálculos
import math


def auditar_calidad_series(dataset_alineado):
    """
    Ejecuta limpieza y validación sobre series temporales alineadas.

    Enfoque:
    - No modifica valores originales
    - No elimina datos
    - Solo detecta, clasifica y mide calidad

    Complejidad: O(n^2) por las iteraciones anidadas.
    """

    # Diccionario maestro donde guardaremos la serie etiquetada por cada activo.
    resultado = {}

    # Inicia el bucle para procesar cada activo (ticker) y su lista de precios (serie).
    for ticker, serie in dataset_alineado.items():

        # Fase 1: Clasificación básica
        serie_limpia = _clasificar_serie(serie)

        # Fase 2: Cálculo de log returns para detectar cambios bruscos
        log_returns = _calcular_log_returns(serie_limpia)

        # Fase 3: Cálculo de Z-scores para detectar anomalías estadísticas
        z_scores = _calcular_zscore(log_returns)

        # Fase 4: Detección de anomalías
        _detectar_anomalias(serie_limpia, z_scores)

        # Fase 3: Cálculo de métricas de calidad
        calidad = _calcular_metricas(serie_limpia)

        # Fase 4: Diagnóstico final
        diagnostico = _generar_diagnostico(calidad)

        """
        Resultado final por activo. Agrupa la serie etiquetada, las estadísticas
            y el diagnóstico bajo el nombre del activo.
        """
        resultado[ticker] = {
            "serie": serie_limpia,
            "calidad": calidad,
            "diagnostico": diagnostico
        }
    # Devuelve el objeto completo con la auditoría de todos los activos procesados.
    return resultado


def _clasificar_serie(serie):
    """
    Fase 1: Clasificación básica de cada punto de la serie.

    Detecta:
    - Valores nulos
    - Valores inválidos (<= 0)

    Complejidad: O(n) por iterar una vez sobre la serie.
    """
    serie_limpia = []

    # Itera sobre cada punto de la serie original para clasificarlo.
    for punto in serie:
        # Extrae el valor de cierre para facilitar su manipulación.
        valor = punto["valor"]
        obj = punto.get("obj_sql")

        # Construimos el raw_dict SOLO si existe el dato en la DB
        raw_dict = None
        if obj:
            raw_dict = {
                "id_serie": obj.id_serie,
                "open": obj.open,
                "high": obj.high,
                "low": obj.low,
                "volumen": obj.volumen
            }

        # Crea un nuevo diccionario para el punto, manteniendo la fecha y el valor.
        punto_clean = {
            "fecha": punto["fecha"],
            "valor": valor,
            # Enviamos los datos del Raw en la RAM
            "raw": raw_dict,
            # Flags de calidad
            "es_nulo": valor is None,
            "es_invalido": valor is not None and valor <= 0,
            "es_anomalo": False,
            # Preparado para futuras técnicas
            "tipo_anomalia": None
        }

        serie_limpia.append(punto_clean)

    return serie_limpia


def _calcular_log_returns(serie):
    """
    Calcula cuánto cambia el precio de un activo día tras día usando
        una escala logarítmica.

    Se usa logaritmos (y no solo porcentajes) para medir cambios
        relativos de forma simétrica. Es una regla más justa.

    Complejidad: O(n) por iterar una vez sobre la serie.
    """

    # Inicializa una lista vacía para almacenar los rendimientos calculados.
    log_returns = []

    # Itera desde el segundo elemento (índice 1) hasta el final de la serie.
    # Se empieza en 1 porque cada cálculo requiere el valor actual y el anterior.
    for i in range(1, len(serie)):
        # Extrae el precio de cierre del punto en el tiempo actual.
        a = serie[i]["valor"]
        # Extrae el precio de cierre del punto en el tiempo inmediatamente anterior.
        p = serie[i - 1]["valor"]

        if a and p and a > 0 and p > 0:
            # Calculamos la "distancia" o cambio entre precios usando logaritmos.
            # Esto nos dice cuánto ganamos o perdimos en ese paso.
            log_returns.append(math.log(a / p))
        else:
            # Si falta un precio, ponemos 'None' para no dejar el hueco vacío.
            log_returns.append(None)

    return log_returns


def _calcular_zscore(valores):
    """
    Calcula el Z-score de una lista de valores con el fin de detectar anomalías.

    - Desviación estándar: Es una medida que te dice qué tan "rebeldes" son los datos;
        si es un número bajo, los precios están cerca del promedio, pero si es alto,
        los precios están saltando por todos lados (volatilidad).
    - El Z-Score: Es una etiqueta que le pones a un precio para saber qué tan lejos
        se escapó del promedio; si el Z-Score es 0, el precio es normal, pero si
        es 3 o -3, es un movimiento exagerado o raro.

    Complejidad: O(n) por las iteraciones en los cálculos
    """

    # Filtra los valores no nulos para calcular media y desviación estándar.
    vals = [v for v in valores if v is not None]

    # Si no hay suficientes datos para calcular estadísticas, devuelve None.
    if len(vals) < 2:
        return [None] * len(valores)

    # Promedio (Media): Suma todos los valores válidos y divide por cuántos hay.
    mean = sum(vals) / len(vals)

    """
    Desviación estándar: Mide cuánto se dispersan los valores respecto a la media.
    - x - mean: Para cada número X, se resta el promedio 'mean'
        esto nos dice cuánto se aleja cada número del promedio.
    - (...) ** 2: Se eleva esa diferencia al cuadrado
        para eliminar signos negativos.
    - sum(...) / len(vals): Se suman todas esas diferencias al cuadrado y se
        divide por la cantidad de valores para obtener el promedio de esas diferencias.
    - ** 0.5: Finalmente, se saca la raíz cuadrada para volver a la escala original.
    """
    std = (sum((x - mean) ** 2 for x in vals) / len(vals)) ** 0.5

    # Si todos los valores son iguales, la desviación es cero (no hay dispersión)
    if std == 0:
        return [0] * len(valores)

    # Transforma cada valor en su Z-score
    return [(v - mean) / std if v is not None else None for v in valores]


def _detectar_anomalias(serie_limpia, z_scores):
    """
    Fase 4:  Detección de anomalías usando reglas simples

    Técnica:
    - Cambio porcentual diario

    Regla:  1
    - Variación > 30% => sospechoso

    Complejidad: O(n) por iterar una vez sobre la serie.
    """
    # Itera desde el segundo punto (índice 1) para comparar con el anterior.
    for i in range(1, len(serie_limpia)):

        # Obtiene el valor actual y el previo para comparar.
        actual = serie_limpia[i]["valor"]
        previo = serie_limpia[i - 1]["valor"]

        # Solo compara si ambos valores existen
        # y el previo no es cero para evitar división por cero.
        if actual is not None and previo is not None and previo != 0:

            """
            Se calcula el cambio porcentual en valor absoluto para normalizar
                la magnitud de la variación.
            Es decir, se calcula que tanto cambió el precio sin importar si subió o
                bajó, y se compara con el umbral del 30%.
            """
            variacion = abs((actual - previo) / previo)
            if variacion > 0.3:
                serie_limpia[i]["es_anomalo"] = True
                serie_limpia[i]["tipo_anomalia"] = "SALTO_BRUSCO"

            """
            Calculo de Z-score para detectar anomalías estadísticas
            - Si el Z-score es mayor a 3 o menor a -3, se considera un
                outlier estadístico.
            - Se empieza desde i- 1 porque el primer log return corresponde
                al cambio entre el primer y segundo punto.
            """
            z = z_scores[i - 1]
            if z is not None and abs(z) > 3:
                serie_limpia[i]["es_anomalo"] = True
                serie_limpia[i]["tipo_anomalia"] = "OUTLIER_ESTADISTICO"

            # Flat Line
            if actual is not None and actual == previo:
                serie_limpia[i]["es_anomalo"] = True
                serie_limpia[i]["tipo_anomalia"] = "SIN_CAMBIO"


def _calcular_metricas(serie_limpia):
    """
    Fase 3: Métricas de calidad.
    Calcula indicadores de calidad de la serie.

    Métricas:
    - Porcentaje de nulos
    - Porcentaje de inválidos
    - Porcentaje de anomalías

    Complejidad: O(n) por iterar una vez sobre la serie para contar cada tipo de error.
    """

    # Cuenta el total de registros para calcular porcentajes.
    total = len(serie_limpia)

    # Si no hay registros, se devuelven métricas con 0% para evitar división por cero.
    if total == 0:
        return {
            "total_registros": 0,
            "pct_nulos": 0,
            "pct_invalidos": 0,
            "pct_anomalias": 0
        }

    # Cuenta cuántos registros tienen cada tipo de error para calcular porcentajes.
    nulos = sum(1 for x in serie_limpia if x["es_nulo"])
    invalidos = sum(1 for x in serie_limpia if x["es_invalido"])
    anomalias = sum(1 for x in serie_limpia if x["es_anomalo"])

    # Calcula y devuelve las métricas porcentuales de calidad.
    return {
        "total_registros": total,
        "pct_nulos": nulos / total,
        "pct_invalidos": invalidos / total,
        "pct_anomalias": anomalias / total
    }


def _generar_diagnostico(calidad):
    """
    Fase 4: Diagnóstico final de calidad.

    Reglas:
    - Muchos nulos => DEFICIENTE
    - Muchas anomalías => RIESGOSO
    - Caso contrario => ACEPTABLE

    Complejidad: O(1) porque solo se evalúan condiciones.
    """

    # Clasifica la serie según la gravedad de sus fallos usando las métricas calculadas.
    if calidad["pct_nulos"] > 0.2:
        estado = "DEFICIENTE"
    elif calidad["pct_anomalias"] > 0.1:
        estado = "RIESGOSO"
    else:
        estado = "ACEPTABLE"

    return {
        "estado_calidad": estado
    }
