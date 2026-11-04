from conftest import write

from depexplain.deps import declared_dependencies, parse_pyproject_toml, parse_requirements_txt


def test_parse_requirements_txt_basico(project):
    write(project, "requirements.txt", "numpy>=1.26,<2\nrequests==2.31.0\n# comentario\n\n")
    declared = parse_requirements_txt(project / "requirements.txt")
    assert set(declared) == {"numpy", "requests"}
    assert "1.26" in str(declared["numpy"])


def test_parse_requirements_txt_ignora_opciones(project):
    write(project, "requirements.txt", "-r base.txt\n--index-url https://example.com\nflask\n")
    declared = parse_requirements_txt(project / "requirements.txt")
    assert set(declared) == {"flask"}


def test_parse_requirements_txt_fichero_inexistente(project):
    assert parse_requirements_txt(project / "no-existe.txt") == {}


def test_parse_pyproject_toml_dependencies(project):
    write(
        project,
        "pyproject.toml",
        '[project]\nname = "x"\ndependencies = ["pydantic>=2.6", "click"]\n',
    )
    declared = parse_pyproject_toml(project / "pyproject.toml")
    assert set(declared) == {"pydantic", "click"}


def test_parse_pyproject_toml_optional_dependencies_excluidas_por_defecto(project):
    write(
        project,
        "pyproject.toml",
        '[project]\nname = "x"\ndependencies = []\n'
        '[project.optional-dependencies]\ndev = ["pytest>=7.4"]\n',
    )
    declared = parse_pyproject_toml(project / "pyproject.toml")
    assert "pytest" not in declared


def test_parse_pyproject_toml_optional_dependencies_con_include_extras(project):
    write(
        project,
        "pyproject.toml",
        '[project]\nname = "x"\ndependencies = []\n'
        '[project.optional-dependencies]\ndev = ["pytest>=7.4"]\n',
    )
    declared = parse_pyproject_toml(project / "pyproject.toml", include_extras=True)
    assert "pytest" in declared


def test_parse_pyproject_toml_invalido_no_rompe(project):
    write(project, "pyproject.toml", "esto no es toml valido [[[")
    assert parse_pyproject_toml(project / "pyproject.toml") == {}


def test_declared_dependencies_none_si_no_hay_ficheros(project):
    assert declared_dependencies(project) is None


def test_declared_dependencies_combina_ambos_ficheros(project):
    write(project, "requirements.txt", "numpy>=1.26\n")
    write(project, "pyproject.toml", '[project]\nname = "x"\ndependencies = ["click"]\n')
    declared = declared_dependencies(project)
    assert set(declared) == {"numpy", "click"}


def test_declared_dependencies_vacio_pero_no_none_si_fichero_existe(project):
    write(project, "requirements.txt", "# nada declarado todavia\n")
    declared = declared_dependencies(project)
    assert declared == {}


def test_marcadores_que_no_aplican_se_ignoran(project):
    write(project, "requirements.txt",
          'pywin32>=300; sys_platform == "nonexistent-os"\n'
          'tomli>=2; python_version < "3.0"\n'
          'click>=8; python_version >= "3.0"\n')
    assert set(parse_requirements_txt(project / "requirements.txt")) == {"click"}


def test_mismo_paquete_en_dos_sitios_se_une(project):
    write(project, "requirements.txt", "Django>=4\n")
    write(project, "pyproject.toml", '[project]\nname = "x"\ndependencies = ["django<6"]\n')
    declared = declared_dependencies(project)
    assert list(declared) == ["Django"]
    assert str(declared["Django"]) == "<6,>=4"
