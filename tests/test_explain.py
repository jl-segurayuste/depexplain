from depexplain.explain import extract_module_name


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
