"""
Extractor de Datos de Mercado (HU05)

Responsabilidad:
- Extraer datos históricos de activos financieros (OHLCV) desde Yahoo Finance.
- Validar la integridad de los datos extraídos
- Reintento de 3 veces con backoff exponencial para errores
    temporales (timeouts, rate limits)

Notas:
- No se usa Google Finance pues dejo de tener API pública oficial.
- No se usa Investing.com porque tiene una protección anti-bots agresiva,
    lo cual recibiremos puros Error 403 casi siempre.
- SEC (EDGAR) no entrega el OHLCV
- BVC no tiene una API REST abierta y gratuita para históricos.
"""

# Librería para hacer request HTTP (consumir APIs)
import requests

import time

# Importación de librerías esenciales
from datetime import date

from typing import List

# Excepciones de las Fuentes
from ...exceptions import (
    YahooError,
    ExtraccionFallidaError,
    FuenteError
)

# Llamada a utilidades de validación y normalización
from ...utils.text_utils import validar_ticker_formato


class ExtractorFinanciero:
    """
    Clase optimizada para extraer datos de múltiples fuentes.
    """

    def __init__(self):
        """
        Se define un atributo de instancia para headers HTTP.
        - Se simula una navegación real para evitar bloqueos por parte de las APIs.
        - Muchas APIs bloquean request sin User-Agent
        - El User-Agent es una técnica básica, no garantiza anonimato ni evasion
            de sistemas avanzados de detección.
        """
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def _preparar_ticker(self, ticker: str, fuente: str) -> str:
        """
        Normaliza el ticker según la fuente.
        Para activos colombianos, añade el sufijo necesario.

        Complejidad: O(1) por acceso directo a lista y operaciones de string
        """
        activos_colombia = [
            'ECOPETROL', 'GEB', 'ISA', 'BCOLOMBIA', 'PFBCOLOM', 'NUTRESA'
        ]

        t = ticker.upper()
        if t in activos_colombia:
            if fuente == "yahoo":
                return f"{t}.CL"
        return t

    def extraer(self, ticker: str, fecha_inicio: date, fecha_fin: date):
        """
        Orquestador principal de extracción de datos financieros.

        Flujo:
        1. Validar ticker
        2. Preparar ticker para Yahoo
        3. Ejecutar extracción (3 intentos)
        4. Validar datos OHLCV
        5. Retornar datos limpios

        Complejidad: O(n^2), dominada por la iteración de los datos retornados
            y la complejidad del método de Yahoo.
        """
        # VALIDACIÓN DE ENTRADA
        validar_ticker_formato(ticker)

        # Para listar errores
        errores_acumulados: List[FuenteError] = []

        try:
            # Preparar ticker específicamente para Yahoo
            ticker_preparado = self._preparar_ticker(ticker, "yahoo")

            # Lista para almacenar datos sin procesar de la extracción
            datos_raw = []

            # Códigos de error que se consideran para el reintento
            RETRYABLE_CODES = {"TIMEOUT", "RATE_LIMIT", "HTTP_ERROR"}

            for intento in range(1, 4):  # Intentar hasta 3 veces
                try:
                    # Ejecutar extracción
                    datos_raw = self._motor_yahoo(
                        ticker_preparado, fecha_inicio, fecha_fin
                    )
                    break

                # Manejo de errores específicos de Yahoo
                except YahooError as e:
                    errores_acumulados.append(e)

                    # No reintentar errores lógicos
                    if e.code not in RETRYABLE_CODES:
                        raise e

                    # Estrategia de backoff exponencial simple
                    if intento < 3:
                        time.sleep(2 * intento)
                    else:
                        raise e

            # Validar resultado no vacío
            if not datos_raw:
                raise FuenteError(
                    fuente="Yahoo Finance",
                    etapa="extraction",
                    message=f"No hay datos históricos para {ticker} en este rango.",
                    detail="La API retornó una lista vacía.",
                    code="DATOS_NO_ENCONTRADOS"
                )

            # Validación de integridad OHLCV
            datos_validados = OHLCVValidador.validar(datos_raw)

            if not datos_validados:
                raise FuenteError(
                    fuente="Yahoo Finance",
                    etapa="validation",
                    message="Los datos obtenidos están corruptos o incompletos.",
                    detail="Validación OHLCV falló para todos los registros.",
                    code="DATOS_INVALIDOS"
                )

            return datos_validados

        except YahooError as e:
            # Error específico del motor Yahoo
            errores_acumulados.append(e)
            raise ExtraccionFallidaError(ticker, errores_acumulados)

        except FuenteError as e:
            # Errores de lógica (sin datos o datos corruptos)
            errores_acumulados.append(e)
            raise ExtraccionFallidaError(ticker, errores_acumulados)

        except Exception as e:
            # Error de infraestructura o bug no controlado
            error_genérico = FuenteError(
                fuente="ExtractorFinanciero",
                etapa="orchestration",
                message="Error crítico en el motor de extracción.",
                detail=str(e),
                code="INTERNAL_EXTRACTOR_ERROR"
            )
            errores_acumulados.append(error_genérico)
            raise ExtraccionFallidaError(ticker, errores_acumulados)

    # Motor Yahoo Finance
    def _motor_yahoo(self, ticker, f_inicio, f_fin):
        """
        Motor de extracción de datos históricos desde Yahoo Finance.
        - Utiliza el endpoint de Yahoo que retorna datos en formato JSON.
        - Convierte un rango de fechas a timestamps UNIX y normaliza la respuesta
            a formato OHLCV.

        Complejidad: O(n), debido a las iteraciones en los timestamps devueltos
        """
        try:
            # Conversión de fechas a timestamps UNIX (segundos desde epoch)
            # Yahoo requiere timestamps en lugar de fechas formateadas
            p1 = int(time.mktime(f_inicio.timetuple()))
            p2 = int(time.mktime(f_fin.timetuple()))

            # Construcción del endpoint dinámico con el ticker
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

            # Parámetros de la consulta:
            # - period1 / period2: rango temporal
            # - interval: frecuencia de datos (1 día)
            # - events: tipo de datos
            params = {
                "period1": p1,
                "period2": p2,
                "interval": "1d",
                "events": "history"
            }

            # Ejecución de la petición HTTP GET
            res = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=12  # evita bloqueos indefinidos
            )

            # Manejo de Rate Limit
            if res.status_code == 429:
                raise YahooError(
                    ticker=ticker,
                    etapa="request",
                    message="Yahoo limitó la conexión (429).",
                    detail="Rate Limit",
                    code="RATE_LIMIT"
                )

            # Error HTTP generales
            if res.status_code != 200:
                raise YahooError(
                    ticker=ticker,
                    etapa="request",
                    message="No se pudo obtener datos históricos desde Yahoo.",
                    detail=f"HTTP {res.status_code}",
                    code="HTTP_ERROR"
                )

            # Conversión de la respuesta JSON a diccionario Python
            data = res.json()

            # Validaciones defensivas (evita KeyError)
            result = data.get("chart", {}).get("result")

            # Si no hay datos, retorna vacío
            if not result:
                return []

            # Desestructuración del JSON de Yahoo
            # 'chart' → 'result' → lista → primer elemento
            res_0 = result[0]
            # Extracción de timestamps (puede no existir → fallback a lista vacía)
            tamps = res_0.get('timestamp', [])
            # Extracción de datos OHLCV dentro de 'indicators'
            quotes = res_0.get("indicators", {}).get('quote', [{}])[0]

            data = []

            # Itera sobre cada día
            for i in range(len(tamps)):
                try:
                    # Se obtiene precio de cierre
                    close = quotes.get("close", [])[i]

                    # Filtrar datos inválidos
                    if close is None:
                        continue

                    # Normalización de registro
                    data.append({
                        "fecha": date.fromtimestamp(tamps[i]),
                        "open": float(quotes.get("open", [])[i] or 0),
                        "high": float(quotes.get("high", [])[i] or 0),
                        "low": float(quotes.get("low", [])[i] or 0),
                        "close": float(close),
                        "volumen": float(quotes.get("volume", [])[i] or 0)
                    })

                # Manejo de datos corruptos
                except (IndexError, TypeError, ValueError):
                    continue  # skip datos corruptos

            return data

        except requests.Timeout:
            raise YahooError(
                ticker, "request",
                "Yahoo tardó demasiado en responder.", "Timeout", "TIMEOUT"
            )
        except Exception as e:
            if isinstance(e, YahooError):
                raise e
            raise YahooError(
                ticker, "parse",
                "Error procesando el JSON de Yahoo.", str(e), "JSON_PARSE_ERROR"
            )


class OHLCVValidador:
    """
    Validador de integridad de datos financieros OHLCV.

    - Valida estructura de datos (schema)
    - Valida reglas financieras (consistencias OHLC)
    - Elimina datos corruptos o inconsistentes
    - Garantiza unicidad temporal
    - Ordenar cronológicamente los datos
    """

    # Método puro
    @staticmethod
    def validar(data: List[dict]) -> List[dict]:
        """
        Valida y limpia una lista de registros OHLCV.
        Retorna: Lista limpia y validada

        Complejidad O(n log n) por el sort
        """
        # Evita procesamiento innecesarios
        if not data:
            return []

        data_limpia = []
        fechas_vistas = set()

        # Extracción + normalización de tipos
        for fila in data:
            try:
                f = fila["fecha"]
                o = float(fila["open"])
                h = float(fila["high"])
                lo = float(fila["low"])
                c = float(fila["close"])
                v = float(fila["volumen"])

                # Validaciones financieras
                if not (lo <= o <= h and lo <= c <= h):
                    continue

                # Redundante, pero necesario
                if h < lo:
                    continue
                # Volumen nunca negativo
                if v < 0:
                    continue

                # Duplicados, garantiza unicidad temporal
                if f in fechas_vistas:
                    continue

                fechas_vistas.add(f)

                # Mantiene consistencia del output
                data_limpia.append({
                    "fecha": f,
                    "open": o,
                    "high": h,
                    "low": lo,
                    "close": c,
                    "volumen": v
                })

            except (KeyError, TypeError, ValueError):
                continue

        # Orden temporal
        data_limpia.sort(key=lambda x: x["fecha"])

        return data_limpia
