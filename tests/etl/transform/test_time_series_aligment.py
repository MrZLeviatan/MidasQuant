"""
Objetivos:
- Validar la alineación de calendarios bursátiles.
"""
# Importar la herramienta de pruebas
import pytest
# Importa el tipo de dato fecha para las comparaciones
from datetime import date
# Importa la función que vamos a testear
from app.etl.transform.time_series_alignment import alinear_series_temporales


# Clase que simula el modelo 'Activo' de la BD.
class MockActivo:
    def __init__(self, id_activo, ticker):
        self.id_activo = id_activo
        self.ticker = ticker


# Clase que simula las consultas de SQLAlchemy (db.query(...))
class MockQuery:
    def __init__(self, data):
        self.data = data

    def distinct(self):
        return self

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self.data


# Clase que simula la sesión de la base de datos
class MockDB:
    def __init__(self, fechas_globales, datos_por_activo):
        # Lista de todas las fechas en la bd.
        self.fechas_globales = fechas_globales
        # Diccionario con precios por ID de activo
        self.datos_por_activo = datos_por_activo
        # Controla qué activo se está "consultando"
        self.current_activo_id = None

    def query(self, *args):
        # Si la consulta pide 1 columna, asumimos que es la línea de tiempo global
        if len(args) == 1:
            return MockQuery(self.fechas_globales)

        # Si pide 2 (fecha, close), asumimos que pide los precios de un activo
        elif len(args) == 2:
            # Query por activo
            data = self.datos_por_activo.get(self.current_activo_id, [])
            return MockQuery(data)

        return MockQuery([])

    def set_activo(self, activo_id):
        # Método auxiliar para Mock qué datos de activo debe devolver a continuación
        self.current_activo_id = activo_id


# Prepara el escenario antes de cada test
@pytest.fixture
def setup_mock_db():
    # Definimos 4 fechas globales
    fechas = [
        (date(2020, 1, 1),),
        (date(2020, 1, 2),),
        (date(2020, 1, 3),),
        (date(2020, 1, 4),),
    ]

    # Simulamos que AAPL no tiene datos el dia 3
    # Simulamos que ETH los tiene en todos
    datos = {
        1: [  # AAPL
            (date(2020, 1, 1), 100),
            (date(2020, 1, 2), 101),
            (date(2020, 1, 4), 103),
        ],
        2: [  # ETH
            (date(2020, 1, 1), 200),
            (date(2020, 1, 2), 201),
            (date(2020, 1, 3), 202),
            (date(2020, 1, 4), 203),
        ]
    }

    # Creamos la BD falsa
    db = MockDB(fechas, datos)

    # Creamos los activos falsos
    activos = [
        MockActivo(1, "AAPL"),
        MockActivo(2, "ETH-USD")
    ]

    fecha_inicio = date(2020, 1, 1)
    fecha_fin = date(2020, 1, 4)

    # Se entrega el escenario al test
    # CAINE?
    return db, activos, fecha_inicio, fecha_fin


# Verificación de estructura
def test_alineacion_estructura(setup_mock_db):
    # Carga el escenario
    db, activos, fecha_inicio, fecha_fin = setup_mock_db

    # asignar activo dinámicamente
    resultado = {}

    for activo in activos:
        # Prepara la BD para todos los activos
        db.set_activo(activo.id_activo)
        # Ejecuta la función real y guarda el resultado
        resultado.update(alinear_series_temporales(
            db, [activo], fecha_inicio, fecha_fin)
        )

    # Verifica el resultado ( AAPL tenga 4 fechas)
    assert "AAPL" in resultado
    assert "ETH-USD" in resultado
    assert len(resultado["AAPL"]) == 4


# Verificación de Huecos (Gaps)
def test_alineacion_valores_correctos(setup_mock_db):
    db, activos, fecha_inicio, fecha_fin = setup_mock_db

    resultado = {}

    for activo in activos:
        db.set_activo(activo.id_activo)
        resultado.update(alinear_series_temporales(
            db, [activo], fecha_inicio, fecha_fin)
        )

    aapl = resultado["AAPL"]

    # Se verifica que el día 3 de enero sea None para AAPL
    assert aapl[2]["valor"] is None  # 2020-01-03

    # Verificamos valores ya existentes
    assert aapl[0]["valor"] == 100
    assert aapl[1]["valor"] == 101
    assert aapl[3]["valor"] == 103


# Verificación si Huecos (Gaps)
def test_activo_sin_faltantes(setup_mock_db):
    db, activos, fecha_inicio, fecha_fin = setup_mock_db
    db.set_activo(2)
    resultado = alinear_series_temporales(
        db, [activos[1]], fecha_inicio, fecha_fin
    )
    eth = resultado["ETH-USD"]
    # Ningún None
    assert all(x["valor"] is not None for x in eth)


# Verifica que las fechas resultantes siempre estén en orden cronológico
def test_fechas_ordenadas(setup_mock_db):
    db, activos, fecha_inicio, fecha_fin = setup_mock_db
    db.set_activo(1)
    resultado = alinear_series_temporales(
        db, [activos[0]], fecha_inicio, fecha_fin
    )
    fechas = [x["fecha"] for x in resultado["AAPL"]]
    # Compara la lista con su versión ordenada
    assert fechas == sorted(fechas)


# Verifica qué pasa si la base de datos está totalmente vacía
def test_sin_datos():
    db = MockDB([], {})
    activos = [MockActivo(1, "AAPL")]
    fecha_inicio = date(2020, 1, 1)
    fecha_fin = date(2020, 1, 4)
    resultado = alinear_series_temporales(db, activos, fecha_inicio, fecha_fin)
    # El resultado debe ser una lista vacía
    assert resultado["AAPL"] == []
