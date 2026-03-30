
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class CombSort(BaseSort):
    """
    Comb Sort: Una mejora del Bubble Sort que elimina elementos desordenados
    a grandes distancias usando un espacio (gap) decreciente.
    """

    def sort(self, data):
        """
        Ordena la lista optimizando los intercambios iniciales.
        """

        # Almacena la cantidad total de elementos en la lista.
        n = len(data)

        # La distancia inicial entre los elementos a comparar
        gap = n

        # Factor de reducción para el gap en cada vuelta
        shrink = 1.3

        # Bandera para saber si hubo intercambio
        swapped = True

        # El ciclo sigue si el gap todavía no es 1, o si aún hubo cambios en la pasada
        while gap > 1 or swapped:

            # Paso 1: Reducir el gap dividiéndolo por el factor de encogimiento
            gap = int(gap / shrink)

            # Paso 2: El gap mínimo permitido es 1 (comparar vecinos)
            if gap < 1:
                gap = 1

            # Reiniciamos la bandera, se asume que no habrá cambios en la vuelta
            swapped = False

            # Paso 3: Recorrer la lista desde el inicio hasta 'n-gap'
            # Esto evita que 'i + gap' se salga de los límites de la lista.
            for i in range(0, n - gap):

                # Compara el elemento actual con el que está a una distancia 'gap'.
                # self.compare devuelve True si el orden es incorrecto según la lógica
                if self.compare(data[i + gap], data[i]):

                    # Intercambiar si están en el orden equivocado, se cruzan.
                    data[i], data[i + gap] = data[i + gap], data[i]

                    # Marcar que hubo cambio
                    swapped = True

        # Retorna la lista ya refinada y ordenada.
        return data
