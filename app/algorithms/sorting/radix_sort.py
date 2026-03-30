
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class RadixSort(BaseSort):
    """
    Ordena procesando cada dígito individualmente,
        de derecha a izquierda.
    """

    def sort(self, data):
        """
        Orquestador que recorre los niveles de los dígitos.
        """

        # Caso Base: Si la lista está vacía, no hay nada que hacer.
        if not data:
            return data

        # Paso 1: Transformar objetos complejos en una clave numérica comparable.
        keys = [self._get_key(x) for x in data]

        # Paso 2: Encontrar el número máß grande para saber cuántos dígitos procesar.
        max_key = max(keys)

        # 'exp' representa la posición del dígito actual (1 para unidades...)
        exp = 1

        # Paso 3; Mientras el número máximo tenga un dígito en la posición 'exp':
        while max_key // exp > 0:

            # Ordenamos toda la lista basándonos solo en el dígito actual.
            self._counting_sort(data, keys, exp)

            # Movemos el foco al siguiente dígito a la izquierda (base 10).
            exp *= 10

        return data

    def _counting_sort(self, data, keys, exp):
        """
        Ordena los elementos basándose en un dígito específico (exp).
        """

        n = len(data)

        # Arreglo temporal donde construiremos el resultado de esta pasada.
        output = [None] * n

        # Contador para los dígitos del 0 al 9 (base 10).
        count = [0] * 10

        # Paso A: Contar cuántas veces aparece cada dígito (0-9) en la posición 'exp'.
        for key in keys:
            # Ejemplo: si el número es 456 y exp=10, el índice es (456 // 10) % 10 = 5.
            index = (key // exp) % 10
            count[index] += 1

        # Paso B: Acumular los conteos.
        # Esto nos dice la "posición final" en la que debe ir cada grupo de números.
        for i in range(1, 10):
            count[i] += count[i - 1]

        # Paso C: Construir el arreglo de salida de atrás hacia adelante.
        # Ir en reversa es CRÍTICO para que el algoritmo sea estable.
        for i in range(n - 1, -1, -1):
            key = keys[i]
            index = (key // exp) % 10

            # Colocamos el objeto en la posición que indica el contador acumulado.
            output[count[index] - 1] = data[i]
            # Restamos uno al contador para que el siguiente número igual retroceda
            count[index] -= 1

        # Paso D: Volcar los resultados de esta pasada a la data original.
        for i in range(n):
            data[i] = output[i]
            # Recalculamos la clave para que coincida con el nuevo orden de la data.
            keys[i] = self._get_key(data[i])

    def _get_key(self, obj):
        """
        Genera clave numérica compuesta.
        """
        # Convierte la fecha a entero compacto
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
