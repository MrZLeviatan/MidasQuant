"""
Test de rendimiento y robustez para PigeonholeSort (HU: Benchmark Sorting)

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
from app.algorithms.sorting.pigeonhole_sort import PigeonholeSort


class DTO:
    def __init__(self, fecha, close):
        self.fecha = fecha
        self.close = close


class TestPigeonholeSort:

    def setup_method(self):
        self.db = SessionLocal()
        self.sorter = PigeonholeSort()

    def teardown_method(self):
        self.db.close()

    def _get_data_from_db(self):
        registros = self.db.query(SerieTemporalRaw).all()

        return [
            DTO(r.fecha, r.close)
            for r in registros
            if r.close is not None and r.fecha is not None
        ]

    def _extract_values(self, data):
        return [(x.fecha, x.close) for x in data]

    def test_pigeonhole_sort_full_benchmark(self):
        """
        Ejecuta el algoritmo completo sobre todos los datos.
        """

        data = self._get_data_from_db()

        assert len(data) > 0, "La base de datos no contiene datos válidos"

        assert all(
            hasattr(x, "fecha") and hasattr(x, "close") for x in data
        ), "Estructura inválida"

        print(f"\n📊 Total de datos a ordenar: {len(data)}")

        start_time = time.time()

        try:
            sorted_data = self.sorter.sort(data.copy())

            duration = time.time() - start_time

            expected = sorted(data, key=lambda x: (x.fecha, x.close))

            sorted_values = self._extract_values(sorted_data)
            expected_values = self._extract_values(expected)

            # Validación principal
            assert sorted_values == expected_values, \
                "El algoritmo no ordenó correctamente"

            # Validación adicional (muy importante aquí)
            assert len(sorted_data) == len(data), \
                "Se perdieron elementos en PigeonholeSort"

            print("Ordenamiento exitoso")
            print(f"Tiempo total: {duration:.4f} segundos")
            print(f"Datos procesados: {len(data)}")

        except Exception as e:
            duration = time.time() - start_time

            print("Fallo en ejecución")
            print(f"Tiempo hasta fallo: {duration:.4f} segundos")
            print(f"Datos soportados antes del fallo: {len(data)}")
            print(f"Error: {str(e)}")

            pytest.fail(f"Falló con {len(data)} datos: {str(e)}")

    def test_pigeonhole_sort_stress_progressive(self):
        """
        Test progresivo para evaluar escalabilidad.
        """

        full_data = self._get_data_from_db()

        assert len(full_data) > 0, "No hay datos suficientes"

        step = max(1, len(full_data) // 10)

        print("\n Iniciando test progresivo (PigeonholeSort)...")

        for i in range(step, len(full_data) + 1, step):

            subset = full_data[:i]

            try:
                start_time = time.time()

                self.sorter.sort(subset.copy())

                duration = time.time() - start_time

                print(f"OK -> {i} datos | {duration:.4f}s")

            except Exception as e:
                print(f"FALLÓ en {i} datos")
                print(f"Error: {str(e)}")

                pytest.fail(f"Fallo en {i} datos: {str(e)}")

    def test_pigeonhole_sort_edge_cases(self):
        """
        Casos extremos.
        """

        class Mock:
            def __init__(self, fecha, close):
                self.fecha = fecha
                self.close = close

        # Vacío
        assert self.sorter.sort([]) == []

        # Un elemento
        single = [Mock(1, 100)]
        assert self.sorter.sort(single) == single

        # Ordenado
        ordered = [Mock(1, 10), Mock(2, 20), Mock(3, 30)]
        result = self.sorter.sort(ordered.copy())
        assert self._extract_values(result) == self._extract_values(ordered)

        # Inverso
        reverse = [Mock(3, 30), Mock(2, 20), Mock(1, 10)]
        result = self.sorter.sort(reverse.copy())
        expected = sorted(reverse, key=lambda x: (x.fecha, x.close))
        assert self._extract_values(result) == self._extract_values(expected)

        # Duplicados
        dup = [Mock(1, 10), Mock(1, 5), Mock(1, 10)]
        result = self.sorter.sort(dup.copy())
        expected = sorted(dup, key=lambda x: (x.fecha, x.close))
        assert self._extract_values(result) == self._extract_values(expected)
