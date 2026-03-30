
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class BinaryInsertionSort(BaseSort):
    """
    Optimiza la búsqueda del lugar de inserción
        mediante una estrategia de búsqueda binaria.
    """

    def sort(self, data):
        """
        Recorre la lista e inserta cada elemento en su lugar óptimo.
        """

        # Paso 1: Empezamos desde el segundo elemento (índice 1).
        # El primero (indice 0) se considera "ya ordenado" por si solo.
        for i in range(1, len(data)):

            # 'key' es el valor que queremos ubicar correctamente.
            key = data[i]

            # Paso 2: Llamamos a la búsqueda binaria para encontrar el índice exacto
            # donde 'key' debería estar dentro de la sublista ya ordenada (0 a i-1)
            pos = self._binary_search(data, key, 0, i - 1)

            # Paso 3: Hacer Hueco.
            # Empezamos desde la posición actual de 'key' (i-1) hacia la izquierda.
            j = i - 1
            # Movemos cada elemento una posición a la derecha hasta llegar al 'pos'
            while j >= pos:
                data[j + 1] = data[j]
                j -= 1

            # Paso 4: Inserta
            # Ponemos nuestra 'key' en el espacio vacío que quedó en 'pos'
            data[pos] = key

        return data

    def _binary_search(self, arr, key, low, high):
        """
        Encuentra el índice de inserción dividiendo el rango a la mitad.
        """

        # Mientras haya rango válido ( no se hayan cruzado los índices)
        while low <= high:

            # Calculamos el centro del rango actual.
            mid = (low + high) // 2

            # Si nuestra 'key' es menor que el elemento del medio...
            if self.compare(key, arr[mid]):
                # Descartamos la mitad derecha; el lugar está en la izquierda
                high = mid - 1
            else:
                # Si es mayor o igual, descartamos la mitad izquierda
                low = mid + 1

        # Al final, 'low' siempre contendrá el índice exacto donde debe ir 'key'
        # para mantener el orden de la lista
        return low
