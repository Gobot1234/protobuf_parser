from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import pybind11
import tomli
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import Distribution

ROOT = Path(__file__).parent
PROTOBUF_PARSER = ROOT / "protobuf_parser"

PYPROJECT = tomli.loads((ROOT / "pyproject.toml").read_text("UTF-8"))
VERSION: str = PYPROJECT["tool"]["poetry"]["version"]

PROTOBUF_PARSER.joinpath("_version.py").write_text(f'__version__ = "{VERSION}"\n')

# make sure that the header files are copied to pybind's include folder before compilation
INCLUDE = Path(pybind11.__file__).parent / "include"
GOOGLE = ROOT / "protobuf" / "src" / "google"
try:
    shutil.move(GOOGLE, INCLUDE, copy_function=shutil.copytree)
except (FileNotFoundError, shutil.Error):  # shouldn't happen in normal code however may happen during development
    pass


with TemporaryDirectory() as temp_dir:
    command = build_ext(Distribution())
    command.finalize_options()
    command.build_lib = str(ROOT)
    parser = Pybind11Extension(
        "protobuf_parser._parser",
        ["protobuf_parser/_parser/lib.cpp"],
        libraries=["protobuf"],
        library_dirs=["protobuf/src/.libs"],
        extra_objects=["protobuf/src/.libs/libprotobuf.a", "protobuf/src/.libs/libprotoc.a"],
        extra_compile_args=["-std=c++14"],
    )
    parser._needs_stub = False  # type: ignore
    command.extensions = [parser]
    command.run()
