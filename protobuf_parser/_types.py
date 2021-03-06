# Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

from __future__ import annotations

import sys
from io import TextIOWrapper
from os import PathLike
from typing import Protocol, Union, runtime_checkable


@runtime_checkable
class SupportsParse(Protocol):
    name: str | bytes

    def read(self) -> str | bytes:
        ...


FileDescriptor = int


@runtime_checkable
class HasFileno(Protocol):
    def fileno(self) -> FileDescriptor:
        ...


if sys.version_info >= (3, 10):
    FileDescriptorLike = FileDescriptor | HasFileno
    StrPath = str | PathLike[str]
    AnyPath = StrPath | bytes | PathLike[bytes]
else:
    FileDescriptorLike = Union[FileDescriptor, HasFileno]
    StrPath = Union[str, PathLike[str]]
    AnyPath = Union[StrPath, bytes, PathLike[bytes]]


def open_fileno(x: FileDescriptorLike) -> TextIOWrapper:
    if isinstance(x, FileDescriptor):
        return open(x, "r", encoding="UTF-8")
    elif isinstance(x, HasFileno):
        x = x.fileno()
        if not isinstance(x, FileDescriptor):
            raise TypeError("object.fileno(): returned a non-integer")
        return open(x, "r", encoding="UTF-8")

    raise TypeError("object passed is not a file descriptor")
