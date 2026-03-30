"""
Módulo de Transformación: Imputación de Datos (HU09)

Responsabilidad:
- Transformar datos crudos auditados en datos financieros aptos para análisis.
- Aplicar técnicas de imputación "relleno" para corregir valores nulos,
    inválidos o anómalos.
- Mantener un registro de trazabilidad de las correcciones aplicadas.
- Persistir los datos limpios y los registros de limpieza en la base de datos.
"""

# Importación de los modelos ORM para persistir los datos limpios y el log de cambios.
from app.database.models import SerieTemporalLimpia, RegistroLimpieza


class ImputadorSeriesTemporales:

    # Inicializa
    def __init__(self, db):
        self.db = db

    def procesar(self, dataset_auditado, activos):
        """
        Orquesta la imputación y persistencia. Recorre los activos y aplica
        las correcciones basadas en la auditoría previa.

        Complejidad O(n^2) porque tiene iteraciones anidadas.
        """

        # Itera sobre la lista de objetos de activos proporcionada.
        for activo in activos:

            # Extrae la información auditada correspondiente a este ticker.
            data = dataset_auditado.get(activo.ticker)

            # Si el activo no está en el dataset auditado, lo ignora y pasa.
            if not data:
                continue

            # Obtiene la lista de puntos de datos etiquetados
            serie = data["serie"]

            # Variable para aplicar Forward Fill
            ultimo_valor = None

            """
            Recorre cada punto de la serie con su índice para
                permitir búsquedas laterales.
            """
            for i, punto in enumerate(serie):

                # Valor original sin procesar, para trazabilidad.
                raw = punto["raw"] or {}

                # Almacena el valor original para mantener la trazabilidad en el log.
                valor_original = punto["valor"]
                # El valor final es el original a menos que se detecte un problema.
                valor_final = valor_original

                # Inicialización de variables para el registro de auditoría de limpieza.
                tipo_problema = None
                accion = None
                justificacion = None

                # 1. Gestión de Valores Nulos (Gaps)
                if punto["es_nulo"]:
                    tipo_problema = "missing_value"
                    # Aplica la técnica Forward Fill (usar el último precio conocido).
                    valor_final = self._aplicar_ffill(ultimo_valor)
                    accion = "forward_ffill"
                    justificacion = """
                        Dato faltante, se rellena con último valor conocido para
                        mantener continuidad
                    """

                # 2. Valores inválidos
                elif punto["es_invalido"]:
                    tipo_problema = "invalid_value"
                    # Corrige el valor mediante interpolación basada en vecinos.
                    valor_final = self._corregir_invalido(serie, i)
                    accion = "corrección / interpolación-lineal"
                    justificacion = """
                        Dato inválido corregido usando interpolación de vecinos,
                        ya que no es consistente con el mercado.
                    """

                # 3. Anomalías
                elif punto["es_anomalo"]:
                    tipo_problema = punto["tipo_anomalia"]
                    # Suaviza el salto extremo usando el promedio de los cercanos.
                    valor_final = self._interpolar(serie, i)
                    accion = "suavizado / interpolación"
                    justificacion = """
                        Variación extrema no consistente con mercado,
                        se suaviza usando promedio de vecinos para evitar distorsión.
                    """

                """
                4. Actualización del último valor conocido para Forward Fill:
                    Si el valor actual (original o corregido) es válido,
                    actualiza el rastreador para el próximo nulo.
                """
                if valor_final is not None:
                    ultimo_valor = valor_final

                # Upset (Remplaza Duplicados)

                # Selecciona la tabla y prepara un filtro
                self.db.query(SerieTemporalLimpia).filter(
                    # Busca el registro que corresponda al id
                    SerieTemporalLimpia.activo_id == activo.id_activo,
                    # Y a la fecha del punto actual,
                    SerieTemporalLimpia.fecha == punto["fecha"]
                    # Elimina cualquier registro que coincida con este filtro
                ).delete()

                # Persistir Serie Limpia
                serie_limpia = SerieTemporalLimpia(
                    activo_id=activo.id_activo,
                    fecha=punto["fecha"],
                    open=raw.get("open"),
                    high=raw.get("high"),
                    low=raw.get("low"),
                    close=valor_final,
                    volumen=raw.get("volumen")
                )
                # Añade el registro a la sesión de base de datos.
                self.db.add(serie_limpia)
                # Sincroniza con la BD para generar el ID de serie_limpia necesario
                self.db.flush()

                # Persistir Registro
                # Si hubo algún problema, guarda un registro detallado.
                if tipo_problema:
                    registro = RegistroLimpieza(
                        activo_id=activo.id_activo,
                        serie_limpia_id=serie_limpia.id_serie,
                        serie_raw_id=raw.get("id_serie"),
                        fecha_dato=punto["fecha"],
                        tipo_problema=tipo_problema,
                        accion_aplicada=accion,
                        valor_original=valor_original,
                        valor_final=valor_final,
                        justificacion=justificacion
                    )
                    # Se añade el registro a la BD.
                    self.db.add(registro)

    # Métodos de Imputación

    def _aplicar_ffill(self, ultimo_valor):
        """
        Implementación de lógica de 'Forward Fill'
            (rellenado hacia adelante)

        Complejidad: O(1)
        """
        return ultimo_valor

    def _interpolar(self, serie, index):
        """
        Interpolación simple:
            Calcula el promedio de los valores válidos más cercanos antes y después
            del índice actual para suavizar anomalías o corregir valores inválidos.
            (no nulos).

        Complejidad: O(n)
        """
        prev_val = None
        next_val = None

        # Bucle hacia atrás para encontrar el primer valor válido anterior al actual.
        for i in range(index - 1, -1, -1):
            valor_buscado = serie[i].get("valor")
            if valor_buscado is not None:
                prev_val = valor_buscado
                break

        # Bucle hacia adelante para encontrar el primer valor válido al actual.
        for i in range(index + 1, len(serie)):
            valor_buscado = serie[i].get("valor")
            if valor_buscado is not None:
                next_val = valor_buscado
                break

        # Lógica de validación estricta de None

        # Caso A: Si encontró ambos, retorna el promedio aritmético.
        if prev_val is not None and next_val is not None:
            return (prev_val + next_val) / 2

        # Caso B: Solo tenemos el vecino anterior
        if prev_val is not None:
            return prev_val

        # Caso C: Solo tenemos el vecino posterior
        if next_val is not None:
            return next_val

        # Caso D: No hay datos válidos en toda la serie
        return None

    def _corregir_invalido(self, serie, index):
        """
        Reemplaza valores inválidos delegando a la lógica de interpolación.
        """
        return self._interpolar(serie, index)
