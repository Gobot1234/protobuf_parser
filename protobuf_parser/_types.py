from io import TextIOWrapper
from typing import AnyStr, Protocol, TYPE_CHECKING, runtime_checkable
from typing_extensions import TypeAlias
from os import PathLike
from enum import IntEnum


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...

@runtime_checkable
class SupportsRead(Protocol[AnyStr]):
    name: AnyStr
    def read(self) -> AnyStr: ...

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
        return open(x)
    elif isinstance(x, HasFileno):
        x = x.fileno()
        if not isinstance(x, FileDescriptor):
            raise TypeError("object.fileno(): returned a non-integer")
        return open(x)
    
    raise TypeError("object passed is not a file descriptor")


class ErrorLocation(enum.IntEnum):
    NAME          = 0   # the symbol name, or the package name for files
    NUMBER        = 1   # field or extension range number
    TYPE          = 2   # field type
    EXTENDEE      = 3   # field extendee
    DEFAULT_VALUE = 4   # field default value
    INPUT_TYPE    = 6   # method input type
    OUTPUT_TYPE   = 7   # method output type
    OPTION_NAME   = 8   # name in assignment
    OPTION_VALUE  = 9   # value in option assignment
    IMPORT        = 10  # import error
    OTHER         = 11  # some other problem
