from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# Nombre de import -> nombre de paquete en PyPI, para los casos donde no
# coinciden (lo que de verdad hace falta para traducir un ModuleNotFoundError
# en un "pip install <esto>" correcto).
IMPORT_TO_PACKAGE: dict[str, str] = {
    "yaml": "pyyaml",
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "google.protobuf": "protobuf",
    "dotenv": "python-dotenv",
    "jwt": "pyjwt",
    "dateutil": "python-dateutil",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyopenssl",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "serial": "pyserial",
    "usb": "pyusb",
    "markdown_it": "markdown-it-py",
}


def module_to_package(module_name: str) -> str:
    top_level = module_name.split(".")[0]
    return IMPORT_TO_PACKAGE.get(module_name, IMPORT_TO_PACKAGE.get(top_level, top_level))


def installed_version(package_name: str) -> str | None:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None
