
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class HeapSort(BaseSort):
    """
    Convierte la lista en un árbol jerárquico para extraer
        siempre el valor máximo de forma eficiente.
    """

    def sort(self, data):
        """
        Orquestador de la construcción y extracción del montículo
        """

        # Longitud total de la lista.
        n = len(data)

        """
        Paso 1: Construir el Max-Heap.
        - Empezamos desde el último nodo que tiene hijos ( n // 2 - 1) hasta la raíz (0)
        - Vamos de abajo hacia arriba asegurando que todos los padres sean mayores
        """
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(data, n, i)

        # Paso 2: Extracción de Elementos
        # Recorremos la lista desde el final hacia el principio
        for i in range(n - 1, 0, -1):

            # El máximo está en data[0], Lo mandamos al final (posición 1)
            data[i], data[0] = data[0], data[i]

            """
            El nuevo valor de la raíz probablemente rompió la regla del heap.
            - Llamamos a _heapify en la raíz para que el nuevo máximo suba.
            - El tamaño 'n' ahora es 'i', ignorando lo que ya ordenamos al final.
            """
            self._heapify(data, i, 0)

        return data

    def _heapify(self, arr, n, i):
        """
        Ajusta un sub-árbol para que el nodo raíz sea el mayor de todos.
        """

        # Inicializamos, suponemos que el padre (i) es el más grande.
        largest = i

        # Calculamos las posiciones matemáticas de los hijos.
        left = 2 * i + 1
        right = 2 * i + 2

        """
        Si el hijo izquierdo existe y es mayor que el padre igual..
            Usamos self.compare para definir qué significa "mayor".
        """
        if left < n and self.compare(arr[largest], arr[left]):
            largest = left

        # Si el hijo derecho existe y es aún mayor que lo que tenemos en 'largest'
        if right < n and self.compare(arr[largest], arr[right]):
            largest = right

        # Si el 'largest' ya no es el padre original (i), hubo un cambio.
        if largest != i:
            # Intercambiamos el padre con su hijo más grande.
            arr[i], arr[largest] = arr[largest], arr[i]

            # Como el hijo bajó de nivel, podría haber roto el orden más abajo.
            # Aplicamos recursion en el sub-árbol afectado.
            self._heapify(arr, n, largest)
