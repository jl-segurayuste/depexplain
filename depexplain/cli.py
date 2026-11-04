from __future__ import annotations

import argparse
import sys
from pathlib import Path

from depexplain.diagnose import diagnose_project, diagnose_project_by_import_name
from depexplain.explain import explain_undeclared, extract_module_name
from depexplain.report import to_console, to_json


def _cmd_diagnose(args: argparse.Namespace) -> int:
    repo_path = Path(args.path).resolve()
    diagnoses = diagnose_project(repo_path, include_extras=args.include_extras)
    if diagnoses is None:
        print("No aplica: no se encontró requirements.txt ni pyproject.toml.")
        return 0

    if args.json:
        print(to_json(diagnoses))
    else:
        print(to_console(diagnoses, only_problems=not args.all))

    if args.fail_on_problems and any(d.status != "ok" for d in diagnoses):
        return 1
    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    if args.file:
        error_text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        error_text = args.text
    else:
        error_text = sys.stdin.read()

    module_name = extract_module_name(error_text)
    if module_name is None:
        print("No he reconocido ningún ModuleNotFoundError/ImportError en ese texto.")
        return 1

    repo_path = Path(args.path).resolve()
    diagnosis = diagnose_project_by_import_name(repo_path, module_name)
    if diagnosis is None:
        for line in explain_undeclared(module_name):
            print(line)
        return 1

    print(diagnosis.explanation)
    if diagnosis.fix_command:
        print(f"Fix: {diagnosis.fix_command}")
    return 0 if diagnosis.status == "ok" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="depexplain")
    sub = parser.add_subparsers(dest="command", required=True)

    p_diagnose = sub.add_parser("diagnose", help="Compara lo instalado contra lo declarado")
    p_diagnose.add_argument("path", nargs="?", default=".")
    p_diagnose.add_argument("--all", action="store_true", help="Muestra también los que están OK")
    p_diagnose.add_argument(
        "--include-extras", action="store_true", help="Incluye también optional-dependencies (dev, test...)"
    )
    p_diagnose.add_argument("--json", action="store_true")
    p_diagnose.add_argument("--fail-on-problems", action="store_true")
    p_diagnose.set_defaults(func=_cmd_diagnose)

    p_explain = sub.add_parser("explain", help="Explica un ModuleNotFoundError/ImportError concreto")
    p_explain.add_argument("text", nargs="?", default=None, help="El error, como texto")
    p_explain.add_argument("--file", default=None, help="Leer el error de un fichero")
    p_explain.add_argument("--path", default=".", help="Directorio del proyecto")
    p_explain.set_defaults(func=_cmd_explain)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
