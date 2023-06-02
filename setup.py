import sys
from cx_Freeze import setup, Executable
from src.__about__ import __version__

version = __version__
build_name = f"addnotespace_v{version}_x86"

build_options = {
    "packages": [],
    "excludes": ["GitPython"],
    "build_exe": f"build/{build_name}",
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable("src/main.py", base=base),
    Executable("src/bulk_run.py", base=base),
]

setup(
    name="addnotespace",
    version=version,
    description="Add whitespace to the sides of your notes.",
    options={"build_exe": build_options},
    executables=executables,
)
