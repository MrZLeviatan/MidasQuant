# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class BucketSort(BaseSort):
    """
    Divide la data en grupos (buckets), ordena cada grupo
        por separado y luego los une.
    """

    def sort(self, data):
        """
        Orquestador del ordenamiento por baldes.
        """

        # Caso Base: Si no hay elementos, no hay nada que procesar.
        if not data:
            return data

        # Paso 1: Transformar objetos en números para poder calcular su posición.
        keys = [self._get_key(x) for x in data]

        # Paso 2: Identificar los valores extremos para definir el rango de los baldes.
        min_key = min(keys)
        max_key = max(keys)

        if max_key == min_key:
            return data  # ya está ordenado

        # Normalización
        normalized_keys = [
            (k - min_key) / (max_key - min_key)
            for k in keys
        ]

        # Paso 3: Definir cuántos baldes usaremos. Se usa la misma cantidad que elemento
        bucket_count = len(data)

        # Paso 4: Crear la estructura de baldes (una lista de listas vacías).
        buckets = [[] for _ in range(bucket_count)]

        # Paso 5: Reparto de Elementos (Scatter)
        for item, norm_key in zip(data, normalized_keys):
            """
            Formula de Normalización:
            - Convierte la clave en un índice entre 0 y bucket_count - 1
            - (ky - min) / (rango total) da un porcentaje entre 0 a 1.
            - Al multiplicar por (bucker_count_1), nos da la posición exacta del balde.
            """
            index = int(norm_key * (bucket_count - 1))

            # Metemos el objeto original en el balde que le corresponde.
            buckets[index].append(item)

        # Paso 6: Ordenar y Recolectar (Gather)
        result = []
        for bucket in buckets:
            # Ordenamos cada balde individualmente (es ideal para baldes pequeños).
            self._insertion_sort(bucket)
            # Concatenamos el contenido del balde ya ordenado al resultado final.
            result.extend(bucket)

        return result

    def _get_key(self, obj):
        """
        Genera clave numérica estable para Bucket Sort.
        """

        # Fecha → entero compacto
        fecha = obj.fecha
        fecha_int = fecha.year * 10000 + fecha.month * 100 + fecha.day

        # Close seguro
        close = int((obj.close or 0) * 1000)

        return fecha_int * 10**4 + close

    def _insertion_sort(self, arr):
        """
        Insertion Sort usando compare() (consistencia del sistema)
        """

        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1

            # Usar compare del BaseSort
            while j >= 0 and self.compare(key, arr[j]):
                arr[j + 1] = arr[j]
                j -= 1

            arr[j + 1] = key
