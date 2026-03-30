
import time
from copy import deepcopy

# Importar modelo
from app.database.models import SerieTemporalLimpia

# Importar algoritmos de ordenamiento
from app.algorithms.sorting import get_all_algorithms


class SortingService:
    """
    Servicio orquestador para ejecutar y medir
        algoritmos de ordenamiento sobre SerieTemporalLimpia.
    """

    def __init__(self, db_session):
        """
        Recibe la conexión de la BD.
        """
        self.db = db_session

    def obtener_datos(self):
        """
        Obtiene todos los registros de la tabla SerieTemporalLimpia.
        """
        # Devuelve la lista de las SerieTemporalLimpia
        return self.db.query(SerieTemporalLimpia).all()

    def obtener_datos_limitados(self, limite=100):
        """
        Obtiene una muestra controlada de datos.
        """
        return self.db.query(SerieTemporalLimpia).limit(limite).all()

    def medir_tiempo(self, algoritmo, data):
        """
        Cronometra cuánto tarda un algoritmo específico en ordenar la data.

        - Se trabaja con Segundo (time.perf_counter()) de forma precisa.
        """

        print(f"Probando: {algoritmo}...", end=" ", flush=True)

        """
        CLAVE: Crea una copia exacta de los datos para que cada prueba empiece de cero.
            Sin esto, el primer algoritmo ordenaría los datos para todos los demás.
        """
        data_copy = deepcopy(data)

        # Marca el inicio del cronómetro con alta precisión.
        inicio = time.perf_counter()

        # Llama al método .sort() del algoritmo que estemos probando.
        algoritmo.sort(data_copy)

        # Marca el final del cronómetro justo después de que el algoritmo termina.
        fin = time.perf_counter()

        # Devuelve el tiempo exacto transcurrido
        return fin - inicio

    def ejecutar_benchmark(self, data=None):
        """
        Ejecuta todos los algoritmos y mide sus tiempos (genera reporte)
        """

        # Si no se pasa data, usa dataset completo
        if data is None:
            data = self.obtener_datos()

        # Validación
        if not data:
            return None

        # 2. Carga todos los algoritmos disponibles (QuickSort, TimSort, etc.).
        algoritmos = get_all_algorithms()

        # Diccionario para guardar las estadísticas de cada uno.
        resultados = {}

        print("Iniciando Benchmark de Algoritmos")

        # 3.Itera sobre cada algoritmo del sistema.
        for nombre, algoritmo in algoritmos.items():

            try:
                # Intenta medir el tiempo de ejecución.
                tiempo = self.medir_tiempo(algoritmo, data)

                # Guarda el tiempo y la cantidad de registros procesados.
                resultados[nombre] = {
                    "tiempo": tiempo,
                    "tamano": len(data)
                }

            except Exception as e:
                # Manejo de errores (importante para defensa)
                # Esto evita que el benchmark se caiga por completo.
                resultados[nombre] = {
                    "tiempo": None,
                    "tamano": len(data),
                    "error": str(e)
                }

        print("Benchmark completado con éxito.\n")

        # Retorna el mapa completo de resultados
        return resultados

    def obtener_top_15_volumen(self):
        """
        Obtiene los 15 registros con mayor volumen
        y los ordena de forma ASCENDENTE por fecha.
        """

        data = self.obtener_datos()

        if not data:
            return []

        # Ordenamos por volumen de MAYOR a MENOR para identificar los 15 más grandes.
        data_sorted = sorted(
            data,
            key=lambda x: x.volumen or 0,
            reverse=True
        )

        # Tomar TOP 15
        top_15 = data_sorted[:15]

        # Ahora los re-ordenamos de forma ASCENDENTE (de menor a mayor volumen).
        top_15_ascendente = sorted(
            top_15,
            key=lambda x: x.volumen or 0
        )

        return top_15_ascendente
