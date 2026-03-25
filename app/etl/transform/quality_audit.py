"""
Actúa como un Auditor de Calidad. Su objetivo es procesar series temporales
ya alineadas para etiquetar datos faltantes, detectar precios financieros
imposibles e identificar saltos de precios sospechosos.

Finalmente genera un "informe" porcentual y un diagnóstico sobre si los datos
de cada activo son lo suficientemente confiable para ser usado en el modelo.
"""


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

        # Lista temporal para ir guardando los puntos de datos ya etiquetados.
        serie_limpia = []

        # 1. Clasificación básica
        # Recorre cada diccionario del calendario creado anteriormente.
        for punto in serie:
            # Extrae el precio de cierre para facilitar su manipulación.
            valor = punto["valor"]

            # Crea un nuevo objeto con "flags" de estado.
            punto_clean = {
                # Mantiene la fecha original.
                "fecha": punto["fecha"],
                # Mantiene el precio original.
                "valor": valor,
                # Marca True si no hay datos (gap detectado).
                "es_nulo": valor is None,
                # Preparación para errores financiero.
                "es_invalido": False,
                # Preparación para cambios bruscos.
                "es_anomalo": False
            }

            """
            Validación financiera básica

            - Si el dato existe, verifica que el precio tenga sentido
            - No puede ser cero o negativo
            """
            if valor is not None:
                if valor <= 0:
                    # Marca el dato como basura técnica si el precio es <= 0.
                    punto_clean["es_invalido"] = True
            # Guarda el punto con sus nuevas etiquetas en la lista del activo.
            serie_limpia.append(punto_clean)

        """
        Detección de anomalías

        Comparamos cada precio con el anterior,por eso se empieza
            desde el índice 1.
        """
        for i in range(1, len(serie_limpia)):
            # Obtiene el precio de hoy.
            actual = serie_limpia[i]["valor"]
            # Obtiene el precio de ayer (registro anterior).
            previo = serie_limpia[i - 1]["valor"]

            # Solo comparamos si ambos días tienen datos y el anterior no es cero.
            if actual is not None and previo is not None and previo != 0:
                # Calcula el porcentaje de cambio absoluto (no importar si subió o bajó)
                variacion = abs((actual - previo) / previo)

                """
                Si el precio cambió máß de un 30% en un solo día, se etiqueta como
                    sospechoso de crímenes.
                """
                if variacion > 0.3:
                    serie_limpia[i]["es_anomalo"] = True

        """
        Métricas de calidad
        """
        # Cuenta cuántos registros totales tiene el activo.
        total = len(serie_limpia)

        # Cuenta cuántos registros tienen cada etiqueta de error activada.
        nulos = sum(1 for x in serie_limpia if x["es_nulo"])
        invalidos = sum(1 for x in serie_limpia if x["es_invalido"])
        anomalias = sum(1 for x in serie_limpia if x["es_anomalo"])

        # Calcula estadísticas porcentuales para el reporte final.
        calidad = {
            "total_registros": total,
            # Porcentaje de Huecos (Gaps).
            "pct_nulos": nulos / total if total else 0,
            # Porcentaje de precios <=0
            "pct_invalidos": invalidos / total if total else 0,
            # Porcentaje de saltos bruscos (cambios anómalos)
            "pct_anomalias": anomalias / total if total else 0
        }

        """
        Diagnóstico

        Clasifica la series según la gravedad de sus fallos:
        - Si faltan más del 20% de los datos, la serie no sirve mucho.
        - Si hay demasiados huecos (>10%), la serie serán volatiles/poco fiables.
        - Si pasa los filtros, se considera apta para análisis.
        """
        if calidad["pct_nulos"] > 0.2:
            estado = "DEFICIENTE"
        elif calidad["pct_anomalias"] > 0.1:
            estado = "RIESGOSO"
        else:
            estado = "ACEPTABLE"

        # Empaqueta el veredictos final.
        diagnostico = {
            "estado_calidad": estado
        }

        """
        Resultado final por activo

        Agrupa la serie etiquetada, las estadísticas y el diagnóstico bajo
            el nombre del activo.
        """
        resultado[ticker] = {
            "serie": serie_limpia,
            "calidad": calidad,
            "diagnostico": diagnostico
        }

    # Devuelve el objeto completo con la auditoría de todos los activos procesados.
    return resultado
