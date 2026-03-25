"""
Este módulo implementa la extracción de metadatos de activos financieros (nombres,
tipos de mercado y categorías) utilizando un sistema de consulta en cascada.

El diseño sigue un enfoque de:
- Tolerancia a fallos (failover): intenta múltiples proveedores (Yahoo Search,
    Stooq, Yahoo Quote) en orden de prioridad si uno falla o bloquea la petición.
- Bajo acoplamiento: cada fuente de datos está encapsulada en un método privado
    (_motor_*) independiente.
- Normalización de datos: independientemente de la fuente, el sistema retorna
    un diccionario con una estructura consistente (nombre, tipo_activo, mercado).
"""
# Librería para realizar peticiones HTTP
import requests

# Para gestionar pausas y evitar bloqueos (rate limiting)
import time

# Para generar tiempos de espera aleatorios
import random

# Importación de la excepción
from ...exceptions import ExtraccionFallidaError


class AssetMetadataExtractor:

    def __init__(self):
        """
        Inicializa la sesión HTTP y las cabeceras base.

        Complejidad: O(1)
        """
        # Reutilizar la conexión TCP y mejorar la eficiencia
        self.session = requests.Session()
        # Define cabeceras para evitar ser bloqueado por los servidores
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Referer": "https://finance.yahoo.com/"
        }

    def buscar_en_cascada(self, ticker: str) -> dict | None:
        """
        Coordina la búsqueda del activo a través de múltiples proveedores.

        Regla de negocio:
        - Si un motor falla, se registra el error y se pasa al siguiente.
        - Si todos fallan, lanza una excepción personalizada.

        Complejidad: O(k) donde k es el número de motores (fuentes) definidos.
        """
        # Lista de motores ordenados por confiabilidad/resistencia al bloqueo
        motores = [
            # Menos intrusivo, ideal para primera opción
            self._motor_yahoo_search,
            # Alternativa externa a Yahoo
            self._motor_stooq,
            # Oficial, pero más propenso a errores 429
            self._motor_yahoo_quote
        ]
        # Para la captura de errores sin parar el proceso
        errores_acumulados = []

        # Itera sobre los motores disponibles
        for i, motor in enumerate(motores, 1):
            try:
                # Intenta ejecutar el motor actual
                res = motor(ticker)
                if res:
                    # Si obtenemos datos, los retornamos inmediatamente
                    return res
                # Pausa aleatoria entre motores para no saturar las APIs
                time.sleep(random.uniform(0.5, 1.2))
            except Exception as e:
                # Se almacena el error específico para el reporte final si todo falla
                error_msg = f"Motor {i} ({motor.__name__}): {str(e)}"
                errores_acumulados.append(error_msg)
                print(f"   [Motor {i}] Error para {ticker}: {e}")
        # Si se agotan los motores sin éxito, se lanza la excepción
        raise ExtraccionFallidaError(ticker, errores_acumulados)

    # MOTOR 1: Yahoo Search
    def _motor_yahoo_search(self, ticker: str):
        """
        Consulta el endpoint de sugerencias de Yahoo Finance.

        Complejidad: O(1) - Petición única y acceso directo a claves del JSON.
        """
        # URL del endpoint de búsqueda de Yahoo que sugiere activos
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
        # Realiza la petición GET con timeout para evitar esperas infinitas
        res = self.session.get(url, headers=self.headers, timeout=5)
        if res.status_code == 200:
            # Extrae la lista de cotizaciones encontradas
            quotes = res.json().get("quotes", [])
            if quotes:
                # Toma el primer resultado (el más relevante)
                q = quotes[0]
                return {
                    "nombre": q.get("longname") or q.get("shortname") or ticker,
                    "tipo_activo": q.get("quoteType", "EQUITY"),
                    "mercado": q.get("exchDisp", "N/A")
                }
        return None

    # MOTOR 2: Stooq (Normalizado)
    def _motor_stooq(self, ticker: str):
        """
        Consulta la disponibilidad del activo en la base de datos de Stooq.

        Complejidad: O(1) - Formateo de string y validación de texto en respuesta.
        """
        # Adaptamos el ticker al formato Stooq (.US para acciones americanas)
        t_stooq = f"{ticker.replace('-USD', '')}.us" if "-USD" not in ticker else ticker
        # Endpoint para descarga de datos CSV/texto
        url = f"https://stooq.com/q/d/l/?s={t_stooq.lower()}&i=d"
        res = self.session.get(url, timeout=5)
        # Verificamos si la respuesta es válida y contiene cabeceras financieras
        if res.status_code == 200 and "Close" in res.text:
            return {
                "nombre": ticker,
                "tipo_activo": "ASSET",
                "mercado": "Stooq Global"
            }
        return None

    # MOTOR 3: Yahoo Quote (El oficial con riesgo 429)
    def _motor_yahoo_quote(self, ticker: str):
        """
        Consulta el endpoint oficial de cotizaciones en tiempo real de Yahoo.

        Complejidad: O(1) - Extracción directa del primer elemento del resultado.
        """
        # URL que devuelve información detallada de símbolos específicos
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
        res = self.session.get(url, headers=self.headers, timeout=5)
        if res.status_code == 200:
            # Navega por el JSON para encontrar la lista de resultados
            result = res.json().get("quoteResponse", {}).get("result", [])
            if result:
                q = result[0]
                return {
                    "nombre": q.get("longName") or q.get("shortName"),
                    "tipo_activo": q.get("quoteType"),
                    "mercado": q.get("market")
                }
        return None
