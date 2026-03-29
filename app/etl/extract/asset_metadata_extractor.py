"""
Extractor de Metadatos de Activos Financieros (HU05)

Responsabilidad:
- Dado un ticker, buscar su información en múltiples fuentes en cascada
    (Yahoo Search, Stooq, Yahoo Quote).
- Normalizar la información obtenida en un formato consistente.
- Manejar errores específicos de cada fuente y acumularlos para reportar
    fallos detallados.
- Implementar una estrategia de failover para garantizar
    la máxima resiliencia ante bloqueos o fallos de proveedores.

El diseño sigue un enfoque de:
- Tolerancia a fallos (failover): intenta múltiples proveedores en orden de prioridad,
    si uno falla o bloquea la petición.
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

from typing import List, Dict, Any, Optional

# Importación de la excepción
from ...exceptions import (
    ExtraccionFallidaError,
    FuenteError,
    YahooError,
    StooqError
)


class AssetMetadataExtractor:

    def __init__(self):
        """
        Inicializa la sesión HTTP y las cabeceras base.
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

    def buscar_en_cascada(self, ticker: str) -> Dict[str, Any]:
        """
        Coordina la búsqueda del activo a través de múltiples proveedores.

        Regla de negocio:
        - Si un motor falla, se registra el error y se pasa al siguiente.
        - Si todos fallan, lanza una excepción personalizada.
        - Metodología failover.

        Complejidad: O(n) por las iteraciones sobre los motores
        """
        # Lista de motores ordenados por confiabilidad/resistencia al bloqueo
        motores = [
            # Menos intrusivo, ideal para primera opción
            ("Yahoo Search", self._motor_yahoo_search),
            # Alternativa externa a Yahoo
            ("Stooq", self._motor_stooq),
            # Oficial, pero más propenso a errores 429
            ("Yahoo Quote" , self._motor_yahoo_quote)
        ]
        # Para la captura de errores sin parar el proceso
        errores_acumulados: List[FuenteError] = []

        # Itera sobre los motores disponibles
        for nombre, motor in motores:
            try:
                # Intenta ejecutar el motor actual
                res = motor(ticker)
                if res:
                    # Si obtenemos datos, los retornamos inmediatamente
                    return res

                # Caso: respuesta vacía
                # Si el motor responde pero no encuentra el activo
                errores_acumulados.append(
                    FuenteError(
                        fuente=nombre,
                        etapa="empty_response",
                        message=f"{nombre} no encontró información del activo.",
                        detail="Respuesta válida pero sin datos",
                        code="RESULTADO_VACÍO"
                    )
                )

            # Captura errores específicos de nuestra lógica de extracción
            except FuenteError as e:
                # Guarda el error y continúa con el siguiente motor de la lista.
                errores_acumulados.append(e)

            # Captura cualquier otro error inesperado.
            except Exception as e:
                # Empaqueta el error genérico en nuestra clase FuenteError
                errores_acumulados.append(
                    FuenteError(
                        fuente=nombre,
                        etapa="unknown",
                        message=f"Error inesperado en {nombre}.",
                        detail=str(e),
                        code="ERROR_DESCONOCIDO"
                    )
                )

            # Pausa obligatoria al final de cada intento para reducir la carga.
            time.sleep(random.uniform(0.4, 0.8))

        # Lanza una excepción personalizada que incluye todos los errores
        raise ExtraccionFallidaError(ticker=ticker, errores=errores_acumulados)

    # --- MOTORES PRIVADOS ---

    # MOTOR 1: Yahoo Search / finance
    def _motor_yahoo_search(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Consulta el endpoint de sugerencias de Yahoo Finance.

        Complejidad: O(1) - Petición única y acceso directo a claves del JSON.
        """
        # URL del endpoint de búsqueda de Yahoo que sugiere activos
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"

        try:
            # Realiza la petición GET con timeout para evitar esperas infinitas
            res = self.session.get(url, headers=self.headers, timeout=5)

            # Validación de status HTTP
            if res.status_code != 200:
                raise YahooError(
                    ticker=ticker,
                    etapa="request",
                    message="No se pudo consultar Yahoo (Search).",
                    detail=f"HTTP {res.status_code}",
                    code="HTTP_ERROR"
                )

            # Extrae la lista de cotizaciones encontradas
            data = res.json()
            quotes = data.get("quotes", [])

            # Si la lista está vacía, el activo no existe en la bd de búsqueda de Yahoo.
            if not quotes:
                return None

            # Toma el primer resultado (el más relevante)
            q = quotes[0]

            # Retorna un diccionario normalizado con la información básica del activo.
            return {
                "nombre": q.get("longname") or q.get("shortname") or ticker,
                "tipo_activo": q.get("quoteType", "EQUITY"),
                "mercado": q.get("exchDisp", "N/A")
            }

        # Captura errores de red genéricos (DNS, sin internet, conexión rechazada).
        except (requests.RequestException, ValueError) as e:
            raise YahooError(
                ticker=ticker,
                etapa="request",
                message="Error de conexión con Yahoo.",
                detail=str(e),
                code="ERROR_CONEXIÓN"
            )

    # MOTOR 2: Stooq (Normalizado)
    def _motor_stooq(self, ticker: str) -> Optional[Dict[str, Any]] :
        """
        Consulta la disponibilidad del activo en la base de datos de Stooq.

        Complejidad: O(1) - Formateo de string y validación de texto en respuesta.
        """
        try:
            # Adaptamos el ticker al formato Stooq (.US para acciones americanas)
            adjusted = ticker.replace('-USD', '')
            t_stooq = f"{adjusted}.us" if "-USD" not in ticker else ticker

            # Endpoint para descarga de datos CSV/texto
            url = f"https://stooq.com/q/d/l/?s={t_stooq.lower()}&i=d"

            res = self.session.get(url, timeout=5)

            # Validación de status HTTP
            if res.status_code != 200:
                raise StooqError(
                    ticker=ticker,
                    etapa="request",
                    message="No se pudo consultar Stooq.",
                    detail=f"HTTP {res.status_code}",
                    code="HTTP_ERROR"
                )

            # Verificamos si la respuesta es válida y contiene cabeceras financieras
            if "Close" not in res.text:
                return None

            # Retornamos un diccionario con valores genéricos
            return {
                "nombre": ticker,
                "tipo_activo": "ASSET",
                "mercado": "Stooq Global"
            }

        # Captura de error si el servidor de Stooq
        except requests.RequestException as e:
            raise StooqError(
                ticker=ticker, etapa="network",
                message="Fallo de red al conectar con Stooq.",
                detail=str(e),
                code="ERROR_CONEXIÓN"
            )

    # MOTOR 3: Yahoo Quote (El oficial con riesgo 429)
    def _motor_yahoo_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Consulta el endpoint oficial de cotizaciones en tiempo real de Yahoo.

        Complejidad: O(1) - Extracción directa del primer elemento del resultado.
        """
        # URL que devuelve información detallada de símbolos específicos
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"

        try:
            # Realizar la petición GET
            res = self.session.get(url, headers=self.headers, timeout=5)

            # Manejo explícito de rate limit
            if res.status_code == 429:
                raise YahooError(
                    ticker=ticker,
                    etapa="request",
                    message="Yahoo está limitando las consultas.",
                    detail="HTTP 429 - Rate Limit",
                    code="LIMITACIÓN_RATE"
                )

            # Validación para cualquier otro error HTTP (500, 404, etc.)
            if res.status_code != 200:
                raise YahooError(
                    ticker=ticker,
                    etapa="request",
                    message="Error al consultar Yahoo (Quote).",
                    detail=f"HTTP {res.status_code}",
                    code="HTTP_ERROR"
                )

            # Convierte la respuesta JSON en un diccionario de Python.
            data = res.json()
            result = data.get("quoteResponse", {}).get("result", [])

            # Si la lista está vacía, el ticker no existe para este motor específico.
            if not result:
                return None

            # Tomamos el primer resultado encontrado.
            q = result[0]

            # Retorna los metadatos normalizados.
            return {
                "nombre": q.get("longName") or q.get("shortName"),
                "tipo_activo": q.get("quoteType"),
                "mercado": q.get("market")
            }

        # Control de excepciones generales
        except (requests.RequestException, ValueError) as e:
            raise YahooError(
                ticker=ticker, etapa="parse",
                message="Error procesando la respuesta de Yahoo Quote.",
                detail=str(e),
                code="JSON_PARSE_ERROR"
            )
