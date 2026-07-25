# Contribuir

## Añadir un mapeo import → paquete

Si te encuentras con un módulo cuyo nombre de import no coincide con el
nombre del paquete en PyPI (como `yaml` → `pyyaml`), añádelo a
`IMPORT_TO_PACKAGE` en `depexplain/environment.py` y añade un test en
`tests/test_environment.py`.

## Antes de un PR

- `ruff check .` y `pytest` en verde.
- Cambios en el parseo de `requirements.txt`/`pyproject.toml`
  (`depexplain/deps.py`) necesitan tests con casos reales de sintaxis
  (comentarios, extras, marcadores de entorno, `-r otro.txt`...).
- Ningún comando ejecuta código del proyecto analizado ni instala nada por
  su cuenta — solo lee ficheros e introspecciona el entorno actual.
