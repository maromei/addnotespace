import sys
from cx_Freeze import setup, Executable

build_options = {"packages": [], "exludes": ["GitPython"]}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable("src/main.py", base=base),
    Executable("src/run_bulk.py", base=base),
]

setup(
    name="addnotespace",
    version="1",
    description="Add whitespace to the sides of your notes.",
    options={"build_exe": build_options},
    executables=executables,
)
