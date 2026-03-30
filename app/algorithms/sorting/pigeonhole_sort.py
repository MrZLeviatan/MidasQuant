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

        # Normalización de claves grandes a pequeñas
        sorted_unique_keys = sorted(set(keys))

        # Mapa: clave original → índice compacto
        key_to_index = {
            key: idx for idx, key in enumerate(sorted_unique_keys)
        }

        # Convertimos claves a rango [0..n]
        normalized_keys = [key_to_index[k] for k in keys]

        # Paso 3: Definir el tamaño del estante de nidos.
        # El +1 asegura que haya espacio para el último valor (el máximo)
        size = len(sorted_unique_keys)

        # Paso 4: CDrear los 'huecos' (nidos).
        # Es una lista de listas: cada posición puede recibir múltiples palomas.
        holes = [[] for _ in range(size)]

        # Paso 5: Distribución
        # Recorre la data y sus claves simultáneamente.
        for item, key in zip(data, normalized_keys):
            # Calcula el índice restando el mínimo (normalización).
            # Ejemplo: si el min es 100 y la clave es 105, va al hueco índice 5.
            holes[key].append(item)

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

        # Convertir fecha a entero compacto YYYYMMDD
        fecha = obj.fecha
        fecha_int = fecha.year * 10000 + fecha.month * 100 + fecha.day

        """
        Convierte el precio 'close' a entero. Multiplica por 1000 para no
            perder los decimales (ej: 10.555 se vuelve 10555).
        """
        close = int((obj.close or 0) * 1000)

        """
        COMBINACIÓN: Desplaza el timestamp a la izquierda y suma el precio.
        - Esto asegura que la fecha sea el criterio principal y el precio el secundario.
        """
        return fecha_int * 10**4 + close
