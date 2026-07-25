from __future__ import annotations

from pathlib import Path
from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel

from depexplain.deps import declared_dependencies
from depexplain.environment import installed_version

Status = Literal["ok", "missing", "version_mismatch"]


class Diagnosis(BaseModel):
    package: str
    declared_constraint: str
    installed_version: str | None
    status: Status
    fix_command: str | None = None
    explanation: str


def _fix_command(package: str, constraint: SpecifierSet) -> str:
    spec = str(constraint)
    if spec:
        return f'pip install "{package}{spec}"'
    return f"pip install {package}"


def diagnose_package(package: str, constraint: SpecifierSet) -> Diagnosis:
    installed = installed_version(package)
    spec_str = str(constraint) or "(sin versión fijada)"

    if installed is None:
        return Diagnosis(
            package=package,
            declared_constraint=spec_str,
            installed_version=None,
            status="missing",
            fix_command=_fix_command(package, constraint),
            explanation=f"'{package}' no está instalado, pero el proyecto lo declara ({spec_str}).",
        )

    try:
        satisfied = Version(installed) in constraint
    except InvalidVersion:
        satisfied = True  # version no estandar (p.ej. de un VCS) -- no se puede comparar, no forzar

    if not satisfied:
        return Diagnosis(
            package=package,
            declared_constraint=spec_str,
            installed_version=installed,
            status="version_mismatch",
            fix_command=_fix_command(package, constraint),
            explanation=(
                f"tienes '{package}' {installed} instalado, pero el proyecto pide {spec_str}."
            ),
        )

    return Diagnosis(
        package=package,
        declared_constraint=spec_str,
        installed_version=installed,
        status="ok",
        explanation=f"'{package}' {installed} cumple lo que pide el proyecto ({spec_str}).",
    )


def diagnose_project(repo_path: Path, *, include_extras: bool = False) -> list[Diagnosis] | None:
    declared = declared_dependencies(repo_path, include_extras=include_extras)
    if declared is None:
        return None
    return [diagnose_package(pkg, spec) for pkg, spec in sorted(declared.items())]


def diagnose_project_by_import_name(
    repo_path: Path, module_name: str, *, include_extras: bool = True
) -> Diagnosis | None:
    """Busca en las dependencias declaradas la que probablemente corresponde
    a `module_name` (normalizando nombre de import vs. nombre de paquete),
    para el flujo `depexplain explain`. Aquí sí se incluyen los extras por
    defecto: si el error ya ocurrió, lo relevante es si el paquete que lo
    causó está declarado en algún sitio, sea obligatorio u opcional.
    """
    declared = declared_dependencies(repo_path, include_extras=include_extras)
    if not declared:
        return None

    from depexplain.environment import module_to_package

    candidate = canonicalize_name(module_to_package(module_name))
    for pkg, spec in declared.items():
        if canonicalize_name(pkg) == candidate:
            return diagnose_package(pkg, spec)
    return None
