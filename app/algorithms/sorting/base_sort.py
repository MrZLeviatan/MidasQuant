class BaseSort:
    """
    Clase base abstracta para todos los algoritmos de ordenamiento.
    Centraliza la lógica compartida entre todos los algoritmos de ordenamiento

    Función:
    - Define una sola vez cómo se ordena los datos.
    - Garantiza consistencia (todos ordenan lo mismo).
    - Escalabilidad a futuro
    """

    def compare(self, a, b):
        """
        Compara dos registros de SerieTemporalLimpia.

        Regla de Ordenamiento:
        - Ordenar por fechas (ascendentes)
        - Si la fecha es igual, ordenar por precio de cierre (close)
        """
        # Si las fechas son diferentes
        if a.fecha != b.fecha:
            # Ordenar por fecha ascendente
            return a.fecha < b.fecha

        # Si las fechas son iguales, ordenar por precio de cierre
        return a.close < b.close
