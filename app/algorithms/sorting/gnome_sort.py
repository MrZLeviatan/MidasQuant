# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class GnomeSort(BaseSort):
    """
    Un algoritmo minimalista que ordena moviéndose hacia
        adelante y atrás según sea necesario, como un gnomo de jardín.
    """

    def sort(self, data):
        """
        Ordena la lista con un solo recorrido dinámico.
        """

        # PASO 1: Empezamos en la primera posición (índice 0).
        index = 0

        # Guardamos el tamaño total para saber cuándo terminar el recorrido.
        n = len(data)

        # Paso 2: El ciclo continúa hasta que el gnomo recorra toda la fila.
        while index < n:

            # Regla A: Si el gnomo está al puro inicio, solo puede ir hacia adelante.
            if index == 0:
                index += 1

            # Regla B: Comparamos el actual con el anterior
            # Si el orden es correcto, el gnomo avanza tranquilo.
            elif not self.compare(data[index], data[index - 1]):
                index += 1

            # Regla C: Si encontramos un desorden...
            else:
                # Intercambio: Los cambiamos de lugar.
                data[index], data[index - 1] = data[index - 1], data[index]

                # Retroceso: El gnomo da un paso atrás para verificar si
                # el elemento movido ahora está en orden con su nuevo vecino anterior.
                index -= 1

        # Al final del bucle, la lista está garantizada a estar ordenada.
        return data
