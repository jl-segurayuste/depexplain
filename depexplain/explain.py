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


# Módulos que se quitaron de la biblioteca estándar y qué usar en su lugar (PEP 632 y PEP 594).
REMOVED_FROM_STDLIB: dict[str, tuple[str, str]] = {
    "distutils": ("3.12", "instala setuptools (trae un distutils compatible) o pasa a packaging/setuptools"),
    "imp": ("3.12", "usa importlib"),
    "asyncore": ("3.12", "usa asyncio"),
    "asynchat": ("3.12", "usa asyncio"),
    "smtpd": ("3.12", "usa aiosmtpd (pip install aiosmtpd)"),
    "cgi": ("3.13", "usa email.message o multipart; para salir del paso, pip install legacy-cgi"),
    "cgitb": ("3.13", "usa el módulo traceback"),
    "imghdr": ("3.13", "usa filetype o puremagic (pip install filetype)"),
    "sndhdr": ("3.13", "usa filetype (pip install filetype)"),
    "telnetlib": ("3.13", "usa telnetlib3 (pip install telnetlib3)"),
    "pipes": ("3.13", "usa shlex.quote"),
    "crypt": ("3.13", "usa hashlib o passlib (pip install passlib)"),
    "uu": ("3.13", "usa base64"),
    "xdrlib": ("3.13", "no tiene sustituto directo en la biblioteca estándar"),
    "nntplib": ("3.13", "no tiene sustituto directo en la biblioteca estándar"),
    "mailcap": ("3.13", "usa mimetypes"),
    "aifc": ("3.13", "usa soundfile (pip install soundfile)"),
    "audioop": ("3.13", "pip install audioop-lts"),
    "chunk": ("3.13", "no tiene sustituto directo en la biblioteca estándar"),
    "sunau": ("3.13", "usa soundfile (pip install soundfile)"),
    "spwd": ("3.13", "usa python-pam o lee /etc/shadow con permisos"),
    "nis": ("3.13", "no tiene sustituto directo en la biblioteca estándar"),
    "ossaudiodev": ("3.13", "usa pyalsaaudio o sounddevice"),
    "msilib": ("3.13", "no tiene sustituto directo en la biblioteca estándar"),
    "lib2to3": ("3.13", "usa libcst o parso"),
}

# Módulos de la biblioteca estándar que dependen de una librería del sistema al compilar Python:
# si faltan, no es un problema de pip.
_STDLIB_SYSTEM_LIBS: dict[str, str] = {
    "_ctypes": "libffi-dev", "ctypes": "libffi-dev",
    "_sqlite3": "libsqlite3-dev", "sqlite3": "libsqlite3-dev",
    "_tkinter": "tk-dev (o el paquete python3-tk)", "tkinter": "tk-dev (o el paquete python3-tk)",
    "_ssl": "libssl-dev", "ssl": "libssl-dev", "_hashlib": "libssl-dev",
    "_bz2": "libbz2-dev", "bz2": "libbz2-dev",
    "_lzma": "liblzma-dev", "lzma": "liblzma-dev",
    "zlib": "zlib1g-dev", "readline": "libreadline-dev",
    "_uuid": "uuid-dev", "_curses": "libncurses-dev", "curses": "libncurses-dev",
    "_dbm": "libgdbm-dev", "_gdbm": "libgdbm-dev",
}


def explain_undeclared(module_name: str) -> list[str]:
    """Qué hacer con un módulo que el proyecto no declara.

    Antes solo decía «añade '<módulo>' a requirements.txt»: con yaml, cv2 o sklearn eso es instalar
    un paquete que no es (los buenos son PyYAML, opencv-python y scikit-learn), y con distutils o
    _ctypes ni siquiera es cosa de pip."""
    import sys

    from depexplain.environment import module_to_package

    top = module_name.split(".")[0]
    if top in REMOVED_FROM_STDLIB:
        since, instead = REMOVED_FROM_STDLIB[top]
        return [
            f"'{top}' era de la biblioteca estándar y se quitó en Python {since}.",
            f"Solución: {instead}.",
        ]
    if top in _STDLIB_SYSTEM_LIBS:
        return [
            (f"'{top}' es de la biblioteca estándar, pero este Python se compiló sin la librería del "
            f"sistema que necesita ({_STDLIB_SYSTEM_LIBS[top]})."),
            ("Solución: instala esa librería y vuelve a compilar o instalar Python (pyenv, uv python "
            "install…), o usa el Python de la distribución."),
        ]
    if top in getattr(sys, "stdlib_module_names", ()):
        return [(f"'{top}' es de la biblioteca estándar: revisa si el nombre está bien escrito o si "
                "un fichero local con el mismo nombre lo está tapando.")]
    package = module_to_package(module_name)
    lines = [f"'{module_name}' no está declarado como dependencia en este proyecto."]
    if package.lower() != top.lower():
        lines.append(f"Ojo: el paquete que lo instala se llama '{package}', no '{top}'.")
    lines.append(f"Solución: añade '{package}' a requirements.txt/pyproject.toml (pip install {package}).")
    return lines
