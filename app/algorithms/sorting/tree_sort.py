
# Importa la base para mantener estructura del proyecto
from app.algorithms.sorting.base_sort import BaseSort


class TreeNode:
    """
    Representa un 'nodo' o ramificación individual del árbol
    """

    def __init__(self, value):
        # Dato real que queremos guardar
        self.value = value

        # Puntero al hijo izquierdo (donde irán los valores menores)
        self.left = None

        # Puntero al hijo derecho (donde irán los valores mayores)
        self.right = None


class TreeSort(BaseSort):
    """
    Algoritmo que ordena transformando una lista en un árbol binario.
    """

    def _key(self, obj):
        """
        Genera una clave ordenable total para cada elemento.
        """
        return (obj.fecha, obj.close, id(obj))

    def sort(self, data):
        """
        Convierte una lista en árbol y luego la extrae ordenada
        """

        # Caso base: Si la lista está vacía, no hay nada que hacer.
        if not data:
            return data

        # Paso 1: Establecer el primer elemento como la raíz (el centro del árbol).
        root = TreeNode(data[0])

        # Paso 2: Insertar todos los demás elementos en el árbol uno por uno.
        for item in data[1:]:
            self._insert(root, item)

        # Paso 3: Recuperar los datos. Preparamos una lista vacía para el resultado.
        result = []

        # Ejecuta el recorrido 'inorder' empezando desde la raíz para llenar 'result'.
        self._inorder(root, result)

        return result

    def _insert(self, node, value):
        current = node
        value_key = self._key(value)

        while True:
            current_key = self._key(current.value)

            # Si es menor → izquierda
            if value_key < current_key:
                if current.left is None:
                    current.left = TreeNode(value)
                    return
                current = current.left

            # Mayor o igual → derecha (maneja duplicados correctamente)
            else:
                if current.right is None:
                    current.right = TreeNode(value)
                    return
                current = current.right

    def _inorder(self, node, result):
        """
        Visita el árbol en orden: los más pequeños primero,
            luego el centro, luego los grandes.
        """
        stack = []
        current = node

        while stack or current:

            # 1. Se va lo más a la izquierda posible (al valor más pequeño).
            while current:
                stack.append(current)
                current = current.left

                # 2. Guarda el valor del nodo actual en la lista de resultados.
                current = stack.pop()
                result.append(current.value)

                # 3. Revisa los valores mayores en el lado derecho.
                current = current.right
