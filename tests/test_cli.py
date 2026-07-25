from conftest import write

import depexplain.diagnose as diagnose_module
from depexplain.cli import main


def test_diagnose_sin_ficheros_exit_0(project, capsys):
    rc = main(["diagnose", str(project)])
    assert rc == 0
    assert "No aplica" in capsys.readouterr().out


def test_diagnose_ok_exit_0(project, monkeypatch, capsys):
    write(project, "requirements.txt", "click>=8.0\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: "8.1.0")
    rc = main(["diagnose", str(project), "--fail-on-problems"])
    assert rc == 0


def test_diagnose_con_problema_exit_1_si_fail_on_problems(project, monkeypatch, capsys):
    write(project, "requirements.txt", "numpy>=1.26,<2\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: None)
    rc = main(["diagnose", str(project), "--fail-on-problems"])
    assert rc == 1


def test_diagnose_json(project, monkeypatch, capsys):
    write(project, "requirements.txt", "click>=8.0\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: "8.1.0")
    main(["diagnose", str(project), "--json"])
    out = capsys.readouterr().out
    assert '"package"' in out


def test_explain_con_texto_directo(project, monkeypatch, capsys):
    write(project, "requirements.txt", "pyyaml>=6.0\n")
    monkeypatch.setattr(diagnose_module, "installed_version", lambda pkg: None)
    rc = main(["explain", "ModuleNotFoundError: No module named 'yaml'", "--path", str(project)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "pyyaml" in out
    assert "pip install" in out


def test_explain_no_declarado(project, capsys):
    write(project, "requirements.txt", "click>=8.0\n")
    rc = main(["explain", "ModuleNotFoundError: No module named 'numpy'", "--path", str(project)])
    assert rc == 1
    assert "no está declarado" in capsys.readouterr().out


def test_explain_texto_sin_patron(project, capsys):
    rc = main(["explain", "esto no es un error", "--path", str(project)])
    assert rc == 1
    assert "No he reconocido" in capsys.readouterr().out
