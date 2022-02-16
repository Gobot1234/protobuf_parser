# Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

from __future__ import annotations

from io import TextIOWrapper
from os import PathLike
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from typing_extensions import TypeAlias


class SupportsStr(Protocol):  # technically just be Any, but it looks much nicer in signatures
    def __str__(self) -> str:
        ...


@runtime_checkable
class SupportsParse(Protocol):
    name: str | bytes

    def read(self) -> str | bytes:
        ...


@runtime_checkable
class HasFileno(Protocol):
    def fileno(self) -> int:
        ...


FileDescriptor = int

if TYPE_CHECKING:
    FileDescriptorLike: TypeAlias = "FileDescriptor | HasFileno"
else:
    FileDescriptorLike = (FileDescriptor, HasFileno)

AnyPath: TypeAlias = "str | bytes | PathLike[str] | PathLike[bytes]"


def open_fileno(x: FileDescriptorLike) -> TextIOWrapper:
    if isinstance(x, FileDescriptor):
        return open(x, "r", encoding="UTF-8")
    elif isinstance(x, HasFileno):
        x = x.fileno()
        if not isinstance(x, FileDescriptor):
            raise TypeError("object.fileno(): returned a non-integer")
        return open(x, "r", encoding="UTF-8")

    raise TypeError("object passed is not a file descriptor")
