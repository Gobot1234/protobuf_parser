from __future__ import annotations

import shutil
from pathlib import Path
from distutils.dist import Distribution
from typing import Any, Dict, cast

import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from tomlkit import parse


PROTOBUF_PARSER = Path("protobuf_parser").resolve()

PYPROJECT = cast(Dict[str, Any], parse(Path("pyproject.toml").read_text()))
VERSION: str = PYPROJECT["tool"]["poetry"]["version"]

PROTOBUF_PARSER.joinpath("_version.py").write_text(f'__version__ = "{VERSION}"\n')

# make sure that the header files are copied to pybind's include folder before compilation
INCLUDE = Path(pybind11.__file__).parent / "include"
GOOGLE = Path("protobuf", "src", "google").resolve()
try:
    shutil.move(GOOGLE, INCLUDE, copy_function=shutil.copytree)
except (FileNotFoundError, shutil.Error):  # shouldn't happen in normal code however may happen during development
    pass


command = build_ext(Distribution())
command.finalize_options()
command.build_lib = str(PROTOBUF_PARSER.parent)
command.extensions = [
    Pybind11Extension("protobuf_parser._parser", ["protobuf_parser/_parser.cpp"]),
]
command.run()
shutil.rmtree("build", ignore_errors=True)
