import sys


def test_python_es_3_12_o_mayor():
    assert sys.version_info >= (3, 12), (
        "Python versión mayor que 3.12 es requerida para ejecutar las pruebas."
    )
