import os
import sys
import shutil
from pathlib import Path

from cx_Freeze import setup, Executable
from src.__about__ import __version__

version = __version__

build_name = f"addnotespace_v{version}_x86_{sys.platform}"
build_path = f"build/{build_name}"
build_zip = f"{build_path}.zip"

icon_path = "ui_files/addnotespace.ico"

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
    Executable("src/main.py", base=base, icon=icon_path, target_name="addnotespace"),
    Executable("src/bulk_run.py", base=base, icon=icon_path),
]

# Standalone cli exe for windows without the GUI base. This means console opens
# if not called from console. With the WIN32GUI base, console output would
# crash the program.
if sys.platform == "win32":
    executables.append(
        Executable("src/cli_exe.py", base=None, icon=icon_path, target_name="cli")
    )

setup(
    name="addnotespace",
    version=version,
    description="Add whitespace to the sides of your notes.",
    options={"build_exe": build_options},
    executables=executables,
)
