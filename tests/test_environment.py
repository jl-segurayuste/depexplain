from depexplain.environment import installed_version, module_to_package


def test_module_to_package_mapeo_conocido():
    assert module_to_package("yaml") == "pyyaml"
    assert module_to_package("PIL") == "pillow"
    assert module_to_package("bs4") == "beautifulsoup4"


def test_module_to_package_submodulo_usa_top_level():
    assert module_to_package("google.protobuf") == "protobuf"


def test_module_to_package_desconocido_se_devuelve_igual():
    assert module_to_package("requests") == "requests"


def test_installed_version_paquete_real():
    assert installed_version("pydantic") is not None


def test_installed_version_paquete_inexistente():
    assert installed_version("esto-no-existe-seguro-12345") is None
