
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
        """
        Busca el hueco correcto para un nuevo valor de forma recursiva.
        """

        # Si el nuevo valor es 'menor' que el valor del nodo donde estamos parados...
        if self.compare(value, node.value):

            # Si el camino a la izquierda está libre, lo plantamos ahí.
            if node.left is None:
                node.left = TreeNode(value)
            # Si ya hay alguien, bajamos un nivel más por la izquierda y repetimos.
            else:
                self._insert(node.left, value)

        # Si el nuevo valor es 'mayor o igual'...
        else:
            # Si el camino a la derecha está vacío, lo colocamos ahí.
            if node.right is None:
                node.right = TreeNode(value)
            # Si está ocupado, bajamos un nivel por la derecha y repetimos.
            else:
                self._insert(node.right, value)

    def _inorder(self, node, result):
        """
        Visita el árbol en orden: los más pequeños primero,
            luego el centro, luego los grandes.
        """

        # Si el nodo actual no es nulo (existe):
        if node:

            # 1. Se va lo más a la izquierda posible (al valor más pequeño).
            self._inorder(node.left, result)

            # 2. Guarda el valor del nodo actual en la lista de resultados.
            result.append(node.value)

            # 3. Revisa los valores mayores en el lado derecho.
            self._inorder(node.right, result)
