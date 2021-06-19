from __future__ import annotations

import shutil
from pathlib import Path

from setuptools.monkey import patch_all
patch_all()
from setuptools.dist import Distribution
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
import tomli

PROTOBUF_PARSER = Path("protobuf_parser").resolve()

PYPROJECT = tomli.load(open(Path("pyproject.toml")))
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
parser = Pybind11Extension(
    "protobuf_parser._parser",
    ["protobuf_parser/_parser.cpp"],
    libraries=["protobuf"],
    #library_dirs=["/Users/James/PycharmProjects/protobuf_parser/protobuf/src/.libs"]
)
parser._needs_stub = False
command.extensions = [parser]
command.run()
# shutil.rmtree("build", ignore_errors=True)
