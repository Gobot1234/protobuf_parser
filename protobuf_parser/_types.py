from io import TextIOWrapper
from typing import AnyStr, Protocol, TYPE_CHECKING, runtime_checkable
from typing_extensions import TypeAlias
from os import PathLike


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...

@runtime_checkable
class SupportsRead(Protocol[AnyStr]):
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
    else:
        raise TypeError("object passed is not a file descriptor")