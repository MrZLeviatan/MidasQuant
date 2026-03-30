
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class SelectionSort(BaseSort):
    """
    Encuentra el valor más pequeño y lo coloca al frente,
    repitiendo el proceso para el resto de la lista.
    """

    def sort(self, data):
        """
        Ordena la lista seleccionando mínimos sucesivamente
        """

        # Cantidad total de elementos en la lista.
        n = len(data)

        # Mueve el límite de la parte ordenada uno por uno.
        for i in range(n):

            # Paso 1: Suponemos que el primer elemento no ordenado es el mínimo.
            min_idx = i

            # Paso 2: Buscamos en el resto de la lista (desde i+1 hasta el final).
            for j in range(i + 1, n):

                # Comparamos el elemento de la posición 'j' con nuestro 'min_idx'
                # Si data[j] es menor, actualizamos quién es el nuevo mínimo.
                if self.compare(data[j], data[min_idx]):

                    # Guardamos el índice donde encontramos el nuevo valor más pequeño.
                    min_idx = j

            # Paso 3: Una vez revisada toda la sublista, intercambiamos valores.
            # Ponemos el mínimo encontrado en la posición 'i' (su lugar definitivo).
            data[i], data[min_idx] = data[min_idx], data[i]

        # Retornamos la lista, que ahora está completamente organizada.
        return data
