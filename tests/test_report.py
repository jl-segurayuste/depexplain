from envdoctor.diagnose import Diagnosis
from envdoctor.report import to_console, to_json


def test_to_console_todo_ok():
    diagnoses = [
        Diagnosis(package="click", declared_constraint="", installed_version="8.1", status="ok", explanation="ok")
    ]
    out = to_console(diagnoses)
    assert "Todo en orden" in out


def test_to_console_muestra_problemas():
    diagnoses = [
        Diagnosis(
            package="numpy",
            declared_constraint=">=1.26,<2",
            installed_version="2.1.0",
            status="version_mismatch",
            fix_command='pip install "numpy>=1.26,<2"',
            explanation="tienes numpy 2.1.0, el proyecto pide >=1.26,<2",
        )
    ]
    out = to_console(diagnoses)
    assert "[VERSION" in out
    assert "pip install" in out
    assert "🔧" not in out and "⚠" not in out


def test_to_console_only_problems_oculta_ok_por_defecto():
    diagnoses = [
        Diagnosis(package="a", declared_constraint="", installed_version="1", status="ok", explanation="a ok"),
        Diagnosis(package="b", declared_constraint="", installed_version=None, status="missing", explanation="b falta", fix_command="pip install b"),
    ]
    out = to_console(diagnoses)
    assert "a ok" not in out
    assert "b falta" in out


def test_to_json_valido():
    diagnoses = [
        Diagnosis(package="click", declared_constraint="", installed_version="8.1", status="ok", explanation="ok")
    ]
    out = to_json(diagnoses)
    assert '"package": "click"' in out
