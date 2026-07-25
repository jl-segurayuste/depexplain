from conftest import write
from packaging.specifiers import SpecifierSet

import depexplain.diagnose as diagnose_module
from depexplain.diagnose import diagnose_package, diagnose_project, diagnose_project_by_import_name


def test_diagnose_package_ok(monkeypatch):
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: "1.26.4")
    d = diagnose_package("numpy", SpecifierSet(">=1.26,<2"))
    assert d.status == "ok"
    assert d.fix_command is None


def test_diagnose_package_missing(monkeypatch):
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: None)
    d = diagnose_package("numpy", SpecifierSet(">=1.26,<2"))
    assert d.status == "missing"
    assert "pip install" in d.fix_command


def test_diagnose_package_version_mismatch(monkeypatch):
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: "2.1.0")
    d = diagnose_package("numpy", SpecifierSet(">=1.26,<2"))
    assert d.status == "version_mismatch"
    assert "2.1.0" in d.explanation
    assert ">=1.26" in d.fix_command and "<2" in d.fix_command


def test_diagnose_package_sin_constraint_siempre_ok_si_instalado(monkeypatch):
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: "9.9.9")
    d = diagnose_package("click", SpecifierSet(""))
    assert d.status == "ok"


def test_diagnose_project_agrega_todos_los_paquetes(project, monkeypatch):
    write(project, "requirements.txt", "numpy>=1.26,<2\nrequests\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: {"numpy": "2.1.0", "requests": "2.31.0"}.get(pkg))
    results = diagnose_project(project)
    by_pkg = {d.package: d for d in results}
    assert by_pkg["numpy"].status == "version_mismatch"
    assert by_pkg["requests"].status == "ok"


def test_diagnose_project_none_sin_ficheros(project):
    assert diagnose_project(project) is None


def test_diagnose_project_by_import_name_mapea_pyyaml(project, monkeypatch):
    write(project, "requirements.txt", "pyyaml>=6.0\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: None)
    d = diagnose_project_by_import_name(project, "yaml")
    assert d is not None
    assert d.package == "pyyaml"
    assert d.status == "missing"


def test_diagnose_project_by_import_name_no_declarado(project):
    write(project, "requirements.txt", "click>=8.0\n")
    d = diagnose_project_by_import_name(project, "numpy")
    assert d is None
