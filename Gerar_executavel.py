"""Gera a distribuição Windows one-folder do Controle de Ponto."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
OUTPUT_DIR = DIST_DIR / "ControleDePonto"


def _data_argument(source: Path) -> list[str]:
    """Retorna um argumento --add-data no formato aceito pelo Windows."""
    return ["--add-data", f"{source};."]


def main() -> int:
    if not (PROJECT_ROOT / "Icone.png").is_file():
        raise FileNotFoundError("Icone.png não foi encontrado na raiz do projeto.")
    if not (PROJECT_ROOT / "Icone.ico").is_file():
        raise FileNotFoundError("Icone.ico não foi encontrado na raiz do projeto.")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name",
        "ControleDePonto",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(BUILD_DIR),
        "--contents-directory",
        ".",
        "--icon",
        str(PROJECT_ROOT / "Icone.ico"),
        "--collect-submodules",
        "app",
        *(_data_argument(PROJECT_ROOT / "Icone.png")),
    ]

    for optional_file in ("Config.json", "config.json", "logo.png", "logomarca.png"):
        path = PROJECT_ROOT / optional_file
        if path.is_file():
            command.extend(_data_argument(path))

    command.append(str(PROJECT_ROOT / "main.py"))
    print("Gerando executável em:", OUTPUT_DIR)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    print("Executável gerado em:", OUTPUT_DIR / "ControleDePonto.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
