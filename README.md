# depexplain

Traduce un `ImportError`/`ModuleNotFoundError` a un diagnóstico claro: qué
tienes instalado, qué pide el proyecto, y el comando exacto para arreglarlo —
en vez de tener que averiguarlo tú mismo comparando versiones a mano.

```
$ python3 app.py
...
ImportError: cannot import name 'BaseSettings' from 'pydantic'

$ echo "$ERROR" | depexplain explain
tienes 'pydantic' 2.13.4 instalado, pero el proyecto pide ==1.10.0.
Fix: pip install "pydantic==1.10.0"
```

## Por qué existe

"Tengo numpy 2 pero el proyecto necesita 1.26" es uno de los errores más
comunes y a la vez más tediosos de diagnosticar a mano: hay que mirar el
traceback, adivinar qué paquete lo causó (no siempre coincide con el nombre
del módulo — `yaml` es `pyyaml`, `cv2` es `opencv-python`...), comprobar qué
versión tienes instalada, y qué versión pide realmente el proyecto.
`depexplain` hace esas tres comprobaciones por ti.

## Instalación

Todavía no está en PyPI:

```bash
pip install git+https://github.com/jl-segurayuste/depexplain.git
```

## Uso

```bash
depexplain diagnose .                    # compara todo lo declarado vs. lo instalado
depexplain diagnose . --all              # incluye también lo que está OK
depexplain diagnose . --json
depexplain diagnose . --fail-on-problems # código de salida 1 si hay algo mal (para CI)

depexplain explain "ModuleNotFoundError: No module named 'yaml'"
echo "$ERROR" | depexplain explain       # o por stdin, pegando el traceback completo
depexplain explain --file traceback.txt
```

Lee `requirements.txt` y/o `pyproject.toml` (`[project.dependencies]` y
`[project.optional-dependencies]`), usando `packaging` para interpretar
correctamente los especificadores de versión (`>=`, `<`, `==`, `~=`...).
Nunca ejecuta el código del proyecto — solo introspecciona el entorno de
Python actual (`importlib.metadata`) y los ficheros de dependencias.

## Desarrollo

```bash
pip install -e ".[dev]"
ruff check .
pytest
```
