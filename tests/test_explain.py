import pytest

from depexplain.explain import explain_undeclared, extract_module_name


def test_extrae_module_not_found_error():
    text = "Traceback...\nModuleNotFoundError: No module named 'numpy'"
    assert extract_module_name(text) == "numpy"


def test_extrae_module_not_found_error_submodulo():
    text = "ModuleNotFoundError: No module named 'google.protobuf'"
    assert extract_module_name(text) == "google.protobuf"


def test_extrae_import_error_cannot_import_name():
    text = "ImportError: cannot import name 'BaseSettings' from 'pydantic'"
    assert extract_module_name(text) == "pydantic"


def test_sin_patron_reconocible_devuelve_none():
    assert extract_module_name("esto no es un error de import") is None


def test_texto_vacio_devuelve_none():
    assert extract_module_name("") is None


@pytest.mark.parametrize("module, expected", [
    ("yaml", "pyyaml"),
    ("sklearn", "scikit-learn"),
    ("cv2.aruco", "opencv-python"),
    ("pkg_resources", "setuptools"),
    ("distutils", "3.12"),
    ("imghdr", "3.13"),
    ("_ctypes", "libffi-dev"),
    ("sqlite3", "libsqlite3-dev"),
    ("json", "biblioteca estándar"),
    ("requests", "pip install requests"),
])
def test_explain_undeclared(module, expected):
    assert expected in " ".join(explain_undeclared(module))
