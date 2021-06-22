from __future__ import annotations

from io import TextIOWrapper
from os import PathLike
from typing import Any, Protocol, TYPE_CHECKING, runtime_checkable

from typing_extensions import TypeAlias


class SupportsStr(Protocol):  # technically every this could just be Any, but it looks much nicer in signatures
    def __str__(self) -> str:
        ...


@runtime_checkable
class SupportsParse(Protocol):
    name: str | bytes
    def read(self) -> str | bytes: ...


@runtime_checkable
class HasFileno(Protocol):
    def fileno(self) -> int: ...


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


# class ErrorLocation(IntEnum):
#     NAME          = 0   # the symbol name, or the package name for files
#     NUMBER        = 1   # field or extension range number
#     TYPE          = 2   # field type
#     EXTENDEE      = 3   # field extendee
#     DEFAULT_VALUE = 4   # field default value
#     INPUT_TYPE    = 6   # method input type
#     OUTPUT_TYPE   = 7   # method output type
#     OPTION_NAME   = 8   # name in assignment
#     OPTION_VALUE  = 9   # value in option assignment
#     IMPORT        = 10  # import error
#     OTHER         = 11  # some other problem
