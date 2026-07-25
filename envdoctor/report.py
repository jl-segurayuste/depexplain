from __future__ import annotations

import json

from envdoctor.diagnose import Diagnosis

_LABELS = {"ok": "OK    ", "missing": "FALTA ", "version_mismatch": "VERSION"}


def to_console(diagnoses: list[Diagnosis], *, only_problems: bool = True) -> str:
    shown = [d for d in diagnoses if d.status != "ok"] if only_problems else diagnoses
    if not shown:
        return "Todo en orden: lo instalado cumple con lo que declara el proyecto."

    lines = []
    for d in shown:
        label = f"[{_LABELS[d.status]:<8}]"
        lines.append(f"{label} {d.explanation}")
        if d.fix_command:
            lines.append(f"           Fix: {d.fix_command}")
    problems = sum(1 for d in diagnoses if d.status != "ok")
    lines.append("")
    lines.append(f"Total: {problems} problema(s) de {len(diagnoses)} dependencia(s) revisada(s).")
    return "\n".join(lines)


def to_json(diagnoses: list[Diagnosis]) -> str:
    return json.dumps([d.model_dump() for d in diagnoses], ensure_ascii=False, indent=2)
