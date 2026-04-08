
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class TimSort(BaseSort):
    """
    TimSort: El estándar de oro.
    Usa Insertions Sort para fragmento pequeños y los une con Merge Sort.

    Nota: El TimSort real es complejo (muy complejo), se usa una versión
        mas educativa y válida.
    """

    # Tamaño fijo del bloque. 32 es el equilibrio ideal entre velocidad y memoria.
    RUN = 32

    def sort(self, data):
        """
        Método principal que orquesta el ordenamiento.
        """

        # Obtener tamaño de la lista
        n = len(data)

        # Paso 1: Ordenar Mini-Bloques
        # Salta de 32 en 32 (el tamaño de RUN) a través de toda la lista.
        for start in range(0, n, self.RUN):

            # Define el final del bloque, asegurándose de no pasarse del final..
            end = min(start + self.RUN - 1, n - 1)

            # Ordena ese pequeño bloque de máximo 32 elementos "in-place".
            self._insertion_sort(data, start, end)

        # Paso 2: Mezclar los bloques ordenados

        # Se mezclan grupos de tamaño 32, luego 64, 128...
        size = self.RUN
        while size < n:

            # Recorre la lista buscando dos bloques adyacentes para mezclarlos
            for left in range(0, n, 2 * size):

                # 'mid' es el final del primer bloque
                mid = min(n - 1, left + size - 1)
                # 'right' es el final del segundo bloque
                right = min((left + 2 * size - 1), (n - 1))

                # Si el bloque derecho existe, los mezcla en uno solo ordenado.
                if mid < right:
                    self._merge(data, left, mid, right)

            # Duplica el tamaño de los grupos a mezclar en la siguiente vuelta.
            size *= 2

        return data

    def _insertion_sort(self, arr, left, right):
        """
        Ordena un sub-tramo moviendo elementos como si fueran cartas.
        """

        # Empieza desde el segundo elemento del tramo (el primero ya está "ordenado").
        for i in range(left + 1, right + 1):

            # 'key' es el elemento que vamos a intentar posicionar.
            key = arr[i]

            # 'j' es el índice del elemento justo a la izquierda de 'key'.
            j = i - 1

            # Mientras el vecino izquierdo sea mayor que nuestra 'key'...
            while j >= left and self.compare(key, arr[j]):
                # Desplaza el vecino hacia la derecha para hacer espacio.
                arr[j + 1] = arr[j]
                j -= 1

            # Ponemos la 'key' en el hueco que quedó libre.
            arr[j + 1] = key

    def _merge(self, arr, left, mid, right):
        """
        Fusiona dos mitades ya ordenadas en una sola secuencia.
        """

        # Divide el tramo en dos listas temporales para comparar sus elementos.
        left_part = arr[left:mid + 1]
        right_part = arr[mid + 1:right + 1]

        # Movimientos de puntero para recorrer (i = izquierda, j = derecha)
        i = 0
        j = 0
        # Puntero para escribir el resultado en la lista original
        k = left

        # Mientras ambas mitades tengan elementos por comparar:
        while i < len(left_part) and j < len(right_part):
            # Compara el frente de ambas listas y coloca el menor en 'arr'.
            if self.compare(left_part[i], right_part[j]):
                arr[k] = left_part[i]
                i += 1
            elif self.compare(right_part[j], left_part[i]):
                arr[k] = right_part[j]
                j += 1
            else:
                # Caso igualdad → PRIORIDAD A LA IZQUIERDA (estabilidad)
                arr[k] = left_part[i]
                i += 1

            k += 1

        # Si quedaron elementos en la izquierda, los copia todos.
        while i < len(left_part):
            arr[k] = left_part[i]
            i += 1
            k += 1

        # Si quedaron elementos en la derecha, los copia todos.
        while j < len(right_part):
            arr[k] = right_part[j]
            j += 1
            k += 1
