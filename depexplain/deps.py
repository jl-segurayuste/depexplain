from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.markers import UndefinedEnvironmentName
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name


def _parse_requirement_line(line: str) -> Requirement | None:
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith("-"):
        return None
    try:
        return Requirement(line)
    except InvalidRequirement:
        return None


def _marker_applies(req: Requirement) -> bool:
    assert req.marker is not None
    try:
        return req.marker.evaluate({"extra": ""})
    except UndefinedEnvironmentName:
        return True  # marcador raro: mejor revisarlo que callarlo


def _add(declared: dict[str, SpecifierSet], req: Requirement) -> None:
    # Un marcador que no aplica aquí (`; sys_platform == "win32"`, `; python_version < "3.11"`)
    # significa que el paquete no hace falta en este entorno: antes salía como «falta instalar».
    if req.marker is not None and not _marker_applies(req):
        return
    # El mismo paquete en dos sitios («Django» y «django») se une y se suman las restricciones.
    key = next((k for k in declared if canonicalize_name(k) == canonicalize_name(req.name)), req.name)
    declared[key] = declared[key] & req.specifier if key in declared else req.specifier


def parse_requirements_txt(path: Path) -> dict[str, SpecifierSet]:
    if not path.exists():
        return {}
    declared: dict[str, SpecifierSet] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        req = _parse_requirement_line(line)
        if req is not None:
            _add(declared, req)
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
            _add(declared, req)
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
    for name, spec in parse_pyproject_toml(pyproject_path, include_extras=include_extras).items():
        _add(declared, Requirement(f"{name}{spec}"))
    return declared
