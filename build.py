from typing import Any
from pathlib import Path

import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

import subprocess

INCLUDE = Path(pybind11.__file__).parent / "include"


def build(setup_kwargs: dict[str, Any]) -> None:
    ext_modules = [
        Pybind11Extension("_protobuf_parser", ["protobuf_parser/protoc.cpp"]),
    ]
    setup_kwargs.update({
        'ext_modules': ext_modules,
        'cmdclass': {'build_ext': build_ext},
        "zip_safe": False,
    })
