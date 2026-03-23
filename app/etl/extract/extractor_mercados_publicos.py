"""
Este módulo implementa la extracción de datos históricos de activos financieros mediante
(OHLCV: Open, High, Low, Close, Volume) desde múltiples fuentes públicas sin depender de
librerías especializadas de alto nivel como yfinance.

El diseño sigue un enfoque de:
- Tolerancia a fallos (failover): intenta múltiples proveedores en orden de prioridad.
- Bajo acoplamiento: cada fuente está encapsulada en métodos independientes.
- Normalización de datos: los motores retornan una estructura de lista de diccionarios

Notas:
- No se usa Google Finance pues dejo de tener API pública oficial.
- No se usa Investing.com porque tiene una protección anti-bots agresiva,
lo cual recibiremos puros Error 403 casi siempre.
- SEC (EDGAR) no entrega el OHLCV
- BVC no tiene una API REST abierta y gratuita para históricos.
"""

# Librería para hacer request HTTP (consumir APIs)
import requests

# Manejo de timestamps y conversión a UNIX time
import time

# Lectura de datos en formato CSV
import csv

# Importación de librerías esenciales
import io
from datetime import datetime, date

# Excepciones de las Fuentes
from ...exceptions import (
    FuenteError,
    YahooError,
    StooqError,
    MarketWatchError,
    ExtraccionFallidaError
)

# Llamada a utilidades de validación y normalización
from ...utils.text_utils import validar_ticker_formato
from ...utils.date_utils import validar_rango_fechas


class ExtractorFinanciero:
    """
    Clase optimizada para extraer datos de múltiples fuentes.
    """

    def __init__(self):
        self.headers = {
            """
            Se define un atributo de instancia para headers HTTP.
            - Se simula una navegación real para evitar bloqueos por parte de las APIs.
            - Muchas APIs bloquean request sin User-Agent
            - El User-Agent es una técnica básica, no garantiza anonimato ni evasion
            de sistemas avanzados de detección.
            """

            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    # Método principal (orquestador)
    def extraer(self, ticker: str, fecha_inicio: date, fecha_fin: date):
        """
        Orquestador principal de extracción de datos financieros.

        - Itera secuencialmente sobre una lista de motores de extracción
        - Facilidad en agregar nuevas fuentes
        - Implementación de failover

        Complejidad: O(n) por la iteración en los diferentes motores
        """
        fuentes = [
            self._motor_yahoo,
            self._motor_stooq,
            self._motor_marketwatch
        ]

        # VALIDACIÓN DE ENTRADA
        # Validar formato de cada ticker
        validar_ticker_formato(ticker)

        # Validar fechas (orden correcto)
        validar_rango_fechas(fecha_inicio, fecha_fin)

        # Acumulador de errores por fuente para trazabilidad
        errores = []

        # Iteración secuencial sobre motores
        for motor in fuentes:
            try:
                # Ejecutar el motor actual
                datos = motor(ticker, fecha_inicio, fecha_fin)
                # Validación de resultado no vacío
                if datos:
                    datos = OHLCVValidador.validar(datos)
                    if datos:
                        return datos

            # Captura errores de dominio sin interrumpir el flujo
            except FuenteError as e:
                errores.append(str(e))
        # Manda la excepción si hay mas de un error posible
        raise ExtraccionFallidaError(ticker, errores)

    # --- MOTORES INTERNOS ---

    # Motor Yahoo Finance
    def _motor_yahoo(self, ticker, f_inicio, f_fin):
        """
        Motor de extracción de datos históricos desde Yahoo Finance.

        Utiliza el endpoint de Yahoo que retorna datos en formato JSON.
        Convierte un rango de fechas a timestamps UNIX y normaliza la respuesta
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
                timeout=10  # evita bloqueos indefinidos
            )

            # Validación de respuesta HTTP (lanza HTTPError si status != 200)
            res.raise_for_status()

            # Conversión de la respuesta JSON a diccionario Python
            json_data = res.json()

            # Validaciones defensivas (evita KeyError)
            chart = json_data.get("chart", {})
            result = chart.get("result")

            # Si no hay datos, retorna vacío
            if not result:
                return []

            # Navegación de la estructura interna del JSON
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

        except Exception as e:
            # Encapsulación del error en excepción de dominio
            raise YahooError(ticker, e)

    # Motor Stooq
    def _motor_stooq(self, ticker, f_inicio, f_fin):
        """
        Motor de extracción de datos históricos desde Stooq

        Utiliza el endpoint de Stooq que retorna datos en formato CSV
        (Muy bueno para índices globales). Normaliza las columnas y filas
        a formato OHLCV.

        Complejidad: O(n), debido a las iteraciones en el CSV
        """
        try:
            # Convierte el ticker a minúsculas / si no tiene sufijo lo agrega
            stooq_ticker = ticker.lower() if "." in ticker else f"{ticker.lower()}.us"

            """
            Constructor de la URL con:
            - s= ticker
            - d1= fecha inicio
            - d2= fecha fin
            - i=d = intervalo diario

            El strftime convierte la fecha en el formato requerido por Stooq
            """
            d1 = f_inicio.strftime('%Y%m%d')
            d2 = f_fin.strftime('%Y%m%d')
            url = f"https://stooq.com/q/d/l/?s={stooq_ticker}&d1={d1}&d2={d2}&i=d"

            # Hacer petición GET con el header, entre otras cosas
            res = requests.get(url, headers=self.headers, timeout=10)
            # Valida respuesta HTTP
            res.raise_for_status()

            # Validador de respuesta vacía
            if not res.text.strip():
                return []

            # Conversión CSV a diccionario Python
            lector = csv.DictReader(io.StringIO(res.text))

            data = []

            # Itera sobre cada fila del CSV
            for fila in lector:
                try:
                    # Se obtiene precio de cierre
                    close = fila.get("Close")

                    # Filtrar datos inválidos
                    if not close:
                        continue

                    # Normalización para datos OHLCV
                    data.append({
                        "fecha": datetime.strptime(fila['Date'], '%Y-%m-%d').date(),
                        "open": float(fila.get("Open") or 0),
                        "high": float(fila.get("High") or 0),
                        "low": float(fila.get("Low") or 0),
                        "close": float(close),
                        "volumen": float(fila.get("Volume") or 0)
                    })

                # Manejo de datos corruptos
                except (ValueError, TypeError):
                    continue  # skip datos corruptos

            return data

        # Encapsulación del error en excepción de dominio
        except Exception as e:
            raise StooqError(ticker, e)

    # Motor MarketWatch
    def _motor_marketwatch(self, ticker, f_inicio, f_fin):
        """
        Motor de extracción desde MarketWatch (implementación parcial / placeholder)

        Utiliza el endpoint de MarketWatch que retorna datos en formato HTML/CSV
        y se normaliza a formato OHLCV.

        Ejemplo de 'Scraping ético' manual de MarketWatch.

        Complejidad: O(n) por la iteración en su número de registros
        """
        try:

            # Marketwatch usa una estructura de URL para histórico fácil de predecir
            url = f"https://www.marketwatch.com/investing/stock/{ticker}/download-data"
            # Parámetros requeridos por MarketWatch
            params = {
                "startDate": f_inicio.strftime('%m/%d/%Y'),
                "endDate": f_fin.strftime('%m/%d/%Y'),
            }

            # Request HTTP
            res = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10
            )

            # Validación HTTP
            res.raise_for_status()

            content = res.text.strip()

            # Validación de contenido vacío
            if not content:
                return []

            # Detección de formato (HTML y CSV)
            # Si contiene tags HTML -> probablemente bloqueado o página web
            if "<html" in content.lower():
                raise MarketWatchError(ticker, "Respuesta en HTML, posible bloqueo")

            # Conversión del CSV en memoria
            lector = csv.DictReader(io.StringIO(res.text))

            # Validación de columnas esperadas
            columnas_esperadas = {"Date", "Open", "High", "Low", "Close", "Volume"}

            # Lector de encabezado del CSV
            if not lector.fieldnames:
                raise MarketWatchError(ticker, "CSV sin encabezados")

            # Obtención de columnas recibidas de la petición
            columnas_recibidas = set(lector.fieldnames)

            # Comparación de columnas
            if not columnas_esperadas.issubset(columnas_recibidas):
                raise MarketWatchError(
                    ticker,
                    f"Estructura inesperada. Columnas recibidas: {columnas_recibidas}"
                )

            data = []

            # Iteración sobre cada fila del CSV
            for fila in lector:
                try:
                    # Validación mínima
                    close = fila.get("Close")

                    # Filtrar datos inválidos
                    if not close:
                        continue

                    # Construcción del registro normalizado
                    data.append({
                        "fecha": datetime.strptime(fila["Date"], "%m/%d/%Y").date(),
                        "open": float(fila.get("Open") or 0),
                        "high": float(fila.get("High") or 0),
                        "low": float(fila.get("Low") or 0),
                        "close": float(close),
                        "volumen": float(fila.get("Volume") or 0)
                    })

                # Manejo de datos corruptos
                except (ValueError, TypeError, KeyError):
                    continue

            return data

        except Exception as e:
            # Encapsulación en excepción de dominio
            raise MarketWatchError(ticker, e)


# Validador OHLCV
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
    def validar(data: list[dict]) -> list[dict]:
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
