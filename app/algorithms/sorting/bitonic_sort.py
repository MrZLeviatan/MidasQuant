
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class BitonicSort(BaseSort):
    """
    Algoritmo de red de ordenamiento ideal para hardware paralelo.
    """

    def sort(self, data):
        """
        Inicia la construcción de la secuencia bitónica.
        """

        # Obtener tamaño
        n = len(data)

        # Paso 1: Llamada recursiva inicial.
        # 'low' es el inicio (0), 'cnt' es el total (n) y 'True' orden Ascendente
        self._bitonic_sort(data, 0, n, True)

        return data

    def _bitonic_sort(self, arr, low, cnt, ascending):
        """
        Crea una secuencia bitónica (una mitad sube, la otra baja)
        """

        # Condición de parada: Si queda más de un elemento por procesar.
        if cnt > 1:

            # Calculamos la mitad del bloque actual.
            k = cnt // 2

            # Paso A: Ordenar la primera mitad hacia Arriba (True).
            self._bitonic_sort(arr, low, k, True)

            # Paso B: Ordenar la segunda mitad hacia Abajo (False)
            self._bitonic_sort(arr, low + k, k, False)

            """
            Paso C: Ahora que tenemos una mitad subiendo y otra bajando,
                las mezclamos para unificarlas en la dirección final deseada.
            """
            self._bitonic_merge(arr, low, cnt, ascending)

    def _bitonic_merge(self, arr, low, cnt, ascending):
        """
        La mezcla mágica. Aplasta la secuencia bitónica para dejarla totalmente ordenada
        """
        # Condición de parada: Si queda más de un elemento por procesar.
        if cnt > 1:
            # Distancia de comparación (salto)
            k = cnt // 2

            # Paso 1: Comparar elementos a distancia 'k'
            for i in range(low, low + k):

                # Si queremos orden Ascendente:
                if ascending:
                    # Si el de la derecha es menor que el de la izquierda, se cruzan
                    if self.compare(arr[i + k], arr[i]):
                        arr[i], arr[i + k] = arr[i + k], arr[i]
                # Si queremos orden Descendente
                else:
                    # Si el de la izquierda es menor que el de la derecha, se cruzan.
                    if self.compare(arr[i], arr[i + k]):
                        arr[i], arr[i + k] = arr[i + k], arr[i]

            # Paso 2: Recursion
            # Repetimos el proceso con los dos nuevos sub-bloques creados.
            # Esto va 'refinando' el orden hasta que el salto sea 0.
            self._bitonic_merge(arr, low, k, ascending)
            self._bitonic_merge(arr, low + k, k, ascending)
