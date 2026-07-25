from __future__ import annotations

import re

_MODULE_NOT_FOUND = re.compile(r"ModuleNotFoundError: No module named ['\"]([\w.]+)['\"]")
_IMPORT_ERROR_FROM = re.compile(r"ImportError: cannot import name ['\"][\w.]+['\"] from ['\"]([\w.]+)['\"]")
_IMPORT_ERROR_PLAIN = re.compile(r"ImportError: No module named ['\"]?([\w.]+)['\"]?")


def extract_module_name(error_text: str) -> str | None:
    for pattern in (_MODULE_NOT_FOUND, _IMPORT_ERROR_FROM, _IMPORT_ERROR_PLAIN):
        m = pattern.search(error_text)
        if m:
            return m.group(1)
    return None
