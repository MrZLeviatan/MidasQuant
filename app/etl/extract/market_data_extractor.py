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

import time

# Importación de librerías esenciales
from datetime import date

# Excepciones de las Fuentes
from ...exceptions import (
    YahooError,
    ExtraccionFallidaError
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
        Versión simplificada:
        - Se utiliza exclusivamente Yahoo Finance como fuente de datos.
        - Se elimina el failover para reducir complejidad y mejorar trazabilidad.

        Flujo:
        1. Validar ticker
        2. Preparar ticker para Yahoo
        3. Ejecutar extracción
        4. Validar datos OHLCV
        5. Retornar datos limpios

        Complejidad: O(n), dominada por la iteración de los datos retornados
        """
        # VALIDACIÓN DE ENTRADA
        validar_ticker_formato(ticker)

        try:
            # Preparar ticker específicamente para Yahoo
            ticker_preparado = self._preparar_ticker(ticker, "yahoo")

            # Ejecutar extracción
            datos = self._motor_yahoo(ticker_preparado, fecha_inicio, fecha_fin)

            # Validar resultado no vacío
            if not datos:
                raise ExtraccionFallidaError(ticker, ["Yahoo retornó datos vacíos"])

            # Validación de integridad OHLCV
            datos_validados = OHLCVValidador.validar(datos)

            if not datos_validados:
                raise ExtraccionFallidaError(
                    ticker,
                    ["Datos inválidos después de validación OHLCV"]
                )

            return datos_validados

        except YahooError as e:
            # Error específico de Yahoo
            raise ExtraccionFallidaError(ticker, [str(e)])

        except Exception as e:
            # Fallback defensivo
            raise ExtraccionFallidaError(ticker, [f"Error inesperado: {str(e)}"])

    # Motor Yahoo Finance
    def _motor_yahoo(self, ticker, f_inicio, f_fin):
        """
        Motor de extracción de datos históricos desde Yahoo Finance.
        - Utiliza el endpoint de Yahoo que retorna datos en formato JSON.
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
