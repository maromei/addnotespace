import os
import sys
import shutil
from pathlib import Path

from cx_Freeze import setup, Executable
from src.__about__ import __version__

version = __version__
build_name = f"addnotespace_v{version}_x86"
build_path = f"build/{build_name}"
build_zip = f"{build_path}.zip"

if Path(build_path).exists():
    shutil.rmtree(build_path)
if Path(build_zip).exists():
    os.remove(build_zip)

build_options = {
    "packages": [],
    "excludes": ["GitPython"],
    "build_exe": build_path,
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable("src/main.py", base=base, icon="addnotespace.ico"),
    Executable("src/bulk_run.py", base=base, icon="addnotespace.ico"),
]

setup(
    name="addnotespace",
    version=version,
    description="Add whitespace to the sides of your notes.",
    options={"build_exe": build_options},
    executables=executables,
)
