from __future__ import annotations

import shutil
from typing import Any
from pathlib import Path

import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

# make sure that the header files are copied to pybind's include folder before compilation
INCLUDE = Path(pybind11.__file__).parent / "include"
GOOGLE = Path().joinpath("protobuf", "src", "google").resolve()
try:
    shutil.move(GOOGLE, INCLUDE, copy_function=shutil.copytree)
except FileNotFoundError:  # shouldn't happen in normal code however may happen during development
    pass


def build(setup_kwargs: dict[str, Any]) -> None:
    ext_modules = [
        Pybind11Extension("_protobuf_parser", ["protobuf_parser/protoc.cpp"]),
    ]
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": {"build_ext": build_ext},
            "zip_safe": False,
        }
    )
