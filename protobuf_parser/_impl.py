from __future__ import annotations
from dataclasses import dataclass

import os
from pathlib import Path
from typing import Sequence

from ._parser import Error as _Error, parse as _parse, run as _run
from ._types import *
from ._version import __version__

__all__ = (
    "Error",
    "Warning",
    "parse",
    "run",
)


class Error(Exception):
    def __new__(cls, c_error: _Error) -> Error | Warning:
        return super().__new__(Warning if c_error.warning else Error)

    def __init__(self, c_error: _Error) -> None:
        self.file = Path(c_error.filename)
        self.line = c_error.line
        self.column = c_error.column
        self.message = c_error.message
        super().__init__(c_error.message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.file}:{self.line}:{self.column}: {self.message!r}>"


class Warning(Error, Warning):
    ...


@dataclass
class FPWithName:
    fp: TextIOWrapper
    name: str | bytes

    def read(self) -> str:
        return self.fp.read()


def parse(*files_: AnyPath | SupportsParse | FileDescriptorLike) -> tuple[list[bytes], Sequence[Error]]:
    """Parse files using protoc.

    Parameters
    ----------
    files
        Something that can be `open`ed or has a name attribute and read method.

    Returns
    -------
    tuple[list[bytes], list[Error]]
        A tuple of the FileDescriptor's bytes and any errors that were encountered when parsing.
    """
    files: list[SupportsParse] = []
    for idx, file in enumerate(files_):
        if not isinstance(file, SupportsParse):
            if isinstance(file, (os.PathLike, str, bytes)):
                files[idx] = FPWithName(open(file, "r", encoding="UTF-8"), os.fspath(file))
            elif isinstance(file, FileDescriptorLike):
                files[idx] = FPWithName(open_fileno(file), f"fd-{file}.proto")
            else:
                raise TypeError(f"parse doesn't support passing {file.__class__} as a file argument")

    output, errors = _parse(*files)
    return output, [Error(error) for error in errors]


# TODO
def run(*args: SupportsStr, **kwargs: SupportsStr) -> Sequence[Error]:
    """Manually invoke protoc.

    Parameters
    ----------
    *args: `str`
        Any arguments to pass to protoc.
    **kwargs: `str`
        Any keyword arguments to pass to protoc.

    Example
    -------
    ```py
    >>> run("this", "that", I="hello")
    # would be equivalent to
    # protoc -I=hello this that
    ```

    Returns
    -------
    list[`Error`]
        The errors that were encountered when invoking protoc.
    """

    return [Error(error) for error in _run(*[str(arg) for arg in args], **{k: str(v) for k, v in kwargs.items()})]
