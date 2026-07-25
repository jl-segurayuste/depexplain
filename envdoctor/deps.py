from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet


def _parse_requirement_line(line: str) -> Requirement | None:
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith("-"):
        return None
    try:
        return Requirement(line)
    except InvalidRequirement:
        return None


def parse_requirements_txt(path: Path) -> dict[str, SpecifierSet]:
    if not path.exists():
        return {}
    declared: dict[str, SpecifierSet] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        req = _parse_requirement_line(line)
        if req is not None:
            declared[req.name] = req.specifier
    return declared


def parse_pyproject_toml(path: Path, *, include_extras: bool = False) -> dict[str, SpecifierSet]:
    if not path.exists():
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}

    project = data.get("project", {})
    lines: list[str] = list(project.get("dependencies", []))
    if include_extras:
        for extra_deps in project.get("optional-dependencies", {}).values():
            lines.extend(extra_deps)

    declared: dict[str, SpecifierSet] = {}
    for line in lines:
        req = _parse_requirement_line(line)
        if req is not None:
            declared[req.name] = req.specifier
    return declared


def declared_dependencies(
    repo_path: Path, *, include_extras: bool = False
) -> dict[str, SpecifierSet] | None:
    """None si no hay ni requirements.txt ni pyproject.toml -- no aplica.
    Diccionario (posiblemente vacío) si al menos uno de los dos existe.

    Por defecto solo mira dependencias obligatorias: las de
    `[project.optional-dependencies]` (dev, test...) no tienen por qué estar
    instaladas en un entorno normal (p.ej. producción), así que exigirlas
    por defecto generaría falsos "falta instalar".
    """
    req_path = repo_path / "requirements.txt"
    pyproject_path = repo_path / "pyproject.toml"
    if not req_path.exists() and not pyproject_path.exists():
        return None

    declared = parse_requirements_txt(req_path)
    declared.update(parse_pyproject_toml(pyproject_path, include_extras=include_extras))
    return declared
