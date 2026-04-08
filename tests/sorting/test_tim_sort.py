"""
Test de rendimiento y robustez para TimSort

Responsabilidad:
- Obtener datos reales desde la base de datos
- Ejecutar el algoritmo completo
- Medir tiempo de ejecución
- Detectar fallos y límite de datos soportados
"""

import time
import pytest

from app.database.connection import SessionLocal
from app.database.models import SerieTemporalRaw
from app.algorithms.sorting.tim_sort import TimSort


class TestTimSort:

    def setup_method(self):
        """
        Inicializa recursos antes de cada test.
        """
        self.db = SessionLocal()
        self.sorter = TimSort()

    def teardown_method(self):
        # Cierra conexión después de cada test.
        self.db.close()

    def _get_data_from_db(self):
        # Obtiene todos los datos desde la base de datos.
        registros = self.db.query(SerieTemporalRaw).all()

        # Extrae los datos "Fecha y Close" de cada registro
        data = [
            r for r in registros
            if r.close is not None and r.fecha is not None
        ]

        return data

    def test_tim_sort_full_benchmark(self):
        """
        Ejecuta el algoritmo sobre todos los datos disponibles
        y mide su rendimiento.
        """

        data = self._get_data_from_db()

        # Si no hay registros en la base de datos
        assert len(data) > 0, "La base de datos no contiene datos válidos"

        # Validación estructural
        assert all(
            hasattr(x, "fecha") and hasattr(x, "close") for x in data
        ), "Los datos no cumplen con la estructura esperada"

        print(f"\n📊 Total de datos a ordenar: {len(data)}")

        # Captura de tiempo inicial
        start_time = time.time()

        try:
            # Ejecuta el ordenamiento sobre una copia de la BD
            sorted_data = self.sorter.sort(data.copy())

            # Captura el tiempo final
            duration = time.time() - start_time

            # Validación correcta
            expected = sorted(data, key=lambda x: (x.fecha, x.close))

            # Compara el resultado del algoritmo con la función nativa 'sorted'
            assert sorted_data == expected, "El algoritmo no ordenó correctamente"

            print("Ordenamiento exitoso")
            print(f"Tiempo total: {duration:.4f} segundos")
            print(f"Datos procesados: {len(data)}")

        except Exception as e:
            # Si ocurre un error lo captura el tiempo fallido
            duration = time.time() - start_time

            print("Fallo en ejecución")
            print(f"Tiempo hasta fallo: {duration:.4f} segundos")
            print(f"Datos soportados antes del fallo: {len(data)}")
            print(f"Error: {str(e)}")

            pytest.fail(f"El algoritmo falló con {len(data)} datos: {str(e)}")

    def test_tim_sort_stress_progressive(self):
        """
        Test progresivo: incrementa el tamaño de entrada
        para detectar el punto de fallo real.
        """

        full_data = self._get_data_from_db()

        assert len(full_data) > 0, "No hay datos suficientes"

        # Define el tamaño de los saltos (10% del total de datos cada vez).
        step = max(1, len(full_data) // 10)

        print("\n Iniciando test progresivo (TimSort)...")

        # Itera incrementando el tamaño del subconjunto de datos.
        for i in range(step, len(full_data) + 1, step):

            # Toma una tajada (slice) de tamaño 'i'
            subset = full_data[:i]

            try:
                start_time = time.time()

                # Prueba el algoritmo con 'i' elementos.
                self.sorter.sort(subset.copy())
                duration = time.time() - start_time
                print(f" OK -> {i} datos | {duration:.4f}s")

            except Exception as e:
                # Si falla en un punto intermedio, nos dice exactamente con cuántos
                print(f" FALLÓ en {i} datos")
                print(f" Error: {str(e)}")

                pytest.fail(f"Fallo en {i} datos: {str(e)}")

    def test_tim_sort_edge_cases(self):
        """
        Casos extremos básicos.
        """
        # Mock simple compatible con BaseSort
        class Mock:
            def __init__(self, fecha, close):
                self.fecha = fecha
                self.close = close

        # Lista vacía
        assert self.sorter.sort([]) == []

        # Un elemento
        single = [Mock(1, 100)]
        assert self.sorter.sort(single) == single

        # Ya ordenado
        ordered = [Mock(1, 10), Mock(2, 20), Mock(3, 30)]
        result = self.sorter.sort(ordered.copy())
        assert result == ordered

        # Orden inverso
        reverse = [Mock(3, 30), Mock(2, 20), Mock(1, 10)]
        result = self.sorter.sort(reverse.copy())
        expected = sorted(reverse, key=lambda x: (x.fecha, x.close))
        assert result == expected

        # Duplicados
        dup = [Mock(1, 10), Mock(1, 5), Mock(1, 10)]
        result = self.sorter.sort(dup.copy())
        expected = sorted(dup, key=lambda x: (x.fecha, x.close))
        assert result == expected
