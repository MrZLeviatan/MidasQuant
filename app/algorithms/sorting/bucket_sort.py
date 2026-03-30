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

        # Paso 3: Definir cuántos baldes usaremos. Se usa la misma cantidad que elemento
        bucket_count = len(data)

        # Paso 4: Crear la estructura de baldes (una lista de listas vacías).
        buckets = [[] for _ in range(bucket_count)]

        # Paso 5: Reparto de Elementos (Scatter)
        for item, key in zip(data, keys):
            """
            Formula de Normalización:
            - Convierte la clave en un índice entre 0 y bucket_count - 1
            - (ky - min) / (rango total) da un porcentaje entre 0 a 1.
            - Al multiplicar por (bucker_count_1), nos da la posición exacta del balde.
            """
            index = int((key - min_key) / (max_key - min_key + 1) * (bucket_count - 1))

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
