# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class PigeonholeSort(BaseSort):
    """
    Ideal para cuando los valores están en un rango conocido.
    - Mueve los objetos a 'nidos' basados en su valor numérico.
    - Requiere transformar los datos en claves numéricas.

    - Las analogías a nidos y palomas es por Palomar.
    """

    def sort(self, data):
        """
        Distribuye y luego recolecta los elementos para ordenarlos.
        """

        # Caso base: Si no hay datos, devolvemos la lista tal cual.
        if not data:
            return data

        # Paso 1: Transformar cada objeto complejo en un número entero (clave)
        # Esto genera una lista paralela de 'pesos' numéricos.
        keys = [self._get_key(x) for x in data]

        # Paso 2: Identificar los límites. El nido más bajo y el más alto.
        min_key = min(keys)
        max_key = max(keys)

        # Paso 3: Definir el tamaño del estante de nidos.
        # El +1 asegura que haya espacio para el último valor (el máximo)
        size = max_key - min_key + 1

        # Paso 4: CDrear los 'huecos' (nidos).
        # Es una lista de listas: cada posición puede recibir múltiples palomas.
        holes = [[] for _ in range(size)]

        # Paso 5: Distribución
        # Recorre la data y sus claves simultáneamente.
        for item, key in zip(data, keys):
            # Calcula el índice restando el mínimo (normalización).
            # Ejemplo: si el min es 100 y la clave es 105, va al hueco índice 5.
            holes[key - min_key].append(item)

        # Paso 6: Reconstrucción
        # Volcamos el contenido de los nidos de vuelta a la lista original
        i = 0
        for bucket in holes:
            for item in bucket:
                # Al recorrer 'holes' en orden, los elementos salen ordenados.
                data[i] = item
                i += 1

        return data

    def _get_key(self, obj):
        """
        Crea un identificador numérico único basado en la fecha y el precio.
        """

        # Convierte la fecha a segundos totales (un número entero grande).
        timestamp = int(obj.fecha.timestamp())

        """
        Convierte el precio 'close' a entero. Multiplica por 1000 para no
            perder los decimales (ej: 10.555 se vuelve 10555).
        """
        close = int(obj.close * 1000)

        """
        COMBINACIÓN: Desplaza el timestamp a la izquierda y suma el precio.
        - Esto asegura que la fecha sea el criterio principal y el precio el secundario.
        """
        return timestamp * 10**6 + close
