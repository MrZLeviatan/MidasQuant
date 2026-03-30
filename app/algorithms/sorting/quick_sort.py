# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class QuickSort(BaseSort):
    """
    Ordenamiento rápido basado en particiones recursivas
    """

    def sort(self, data):
        """
        Inicializa el proceso recursivo en toda la extensión de la lista.
        """

        # Llamamos a la función auxiliar pasando el índice inicial (0) y el final (n-1).
        self._quick_sort(data, 0, len(data) - 1)

        # Retornamos la misma lista, ya modificada internamente.
        return data

    def _quick_sort(self, arr, low, high):
        """
        Divide el problema en sub-problemas cada vez más pequeños.
        """

        # Condición de Parada: Si el rango tiene sentido (al menor 2 elementos)
        if low < high:

            # Paso 1: Organizar la lista alrededor de un pivote y obtener su posición
            # 'pi' (partition index) es el lugar donde el pivote quedó fijo.
            pi = self._partition(arr, low, high)

            # Paso 2: Ordenar la mitad izquierda (desde el inicio antes del pivote)
            self._quick_sort(arr, low, pi - 1)

            # Paso 3: Ordenar la mitad derecha (desde después del pivote hasta el final)
            self._quick_sort(arr, pi + 1, high)

    def _partition(self, arr, low, high):
        """
        El corazón del algoritmo: reubica elementos frente al pivote
        """

        # Elegimos el último elemento como el 'pivote' (como referencia)
        pivot = arr[high]

        """
        Actúa como una barrera, Si todo lo que esté a la izquierda de 'i'
            es menor al pivote.
        Empieza en -1 (fuera del rango) porque aún no hemos encontrado menores
        """
        i = low - 1

        # Recorremos desde el inicio hasta el penúltimo elemento
        for j in range(low, high):

            # Expandimos la zona de los menores incrementando 'i'
            if self.compare(arr[j], pivot):
                i += 1
                # Intercambiamos el elemento menor encontrado con el que estaba
                arr[i], arr[j] = arr[j], arr[i]

        """
        Paso Final: El pivote (que estaba en 'high') se mueve justo
            después de la zona de menores.
        Esto pone al pivote en su lugar correcto: entre los menores y los mayores.
        """
        arr[i + 1], arr[high] = arr[high], arr[i + 1]

        # Retornamos la posición exacta donde quedó el pivote para seguir dividiendo.
        return i + 1
