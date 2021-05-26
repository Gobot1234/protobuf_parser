from __future__ import annotations

import os
from pathlib import Path
from io import BytesIO, StringIO
from typing import Sequence, TYPE_CHECKING, AnyStr, Protocol, overload, runtime_checkable

# from ._parser import run as _run, parse as _parse
from ._parser import parse as _parse, Error as _Error
from ._types import *


__all__ = (
    "Error",
    "SyntaxError",
    "Warning",
    "parse",
    "run",
)


class Error(Exception):
    file: Path
    line: int
    column: int
    message: str

    @overload
    def __new__(cls, c_error: _Error) -> Error:
        ...

    @overload
    def __new__(cls, c_error: _SyntaxError) -> SyntaxError:
        ...

    @overload
    def __new__(cls, c_error: _Warning) -> Warning:
        ...

    def __new__(cls, c_error: _Error) -> Error:
        return super().__new__(
            {
                _Error: Error,
                _SyntaxError: SyntaxError,
                _Warning: Warning,
            }[c_error]
        )

    def __init__(self, c_error) -> None:
        self.file = Path(c_error.file)
        self.line = c_error.line
        self.column = c_error.column
        self.args = c_error.column


class SyntaxError(Error):
    ...


class Warning(Error, Warning):
    ...


def parse(*files: AnyPath | SupportsRead[AnyStr] | FileDescriptorLike) -> tuple[bytes, Sequence[Error]]:
    """Parse files using protoc.

    Parameters
    ----------
    files: `str | bytes | os.Pathlike | SupportsRead | FileDescriptorLike`
        A `str`, `bytes` pathlike or an object that has a read method.

    Returns
    -------
    tuple[`bytes`, list[`Error`]]
        A tuple of the FileDescriptor's bytes and any errors that were encountered when parsing.
    """
    files = list(files)
    for idx, file in enumerate(files):
        if not isinstance(file, SupportsRead):
            if isinstance(file, os.PathLike):
                files[idx] = open(file)
            elif isinstance(file, (str, bytes)):
                files[idx] = open(file)
            elif isinstance(file, FileDescriptorLike):
                files[idx] = open_fileno(file)
            else:
                raise TypeError(f"parse doesn't support passing {file.__class__} as a file argument")
    
    output, errors = _parse(*files)
    return output, [Error(error) for error in errors]


def run(*args: SupportsStr, **kwargs: SupportsStr) -> list[Error]:
    """Manually invoke protoc.

    Parameters
    ----------
    *args: `str`
        Any arguments to pass to protoc.
    **kwargs: `str`
        Any keyword arguments to pass to protoc.

    Example
    -------
    .. code-block:: python

        invoke_protoc("this", "that", I="hello")
        # would be equivalent to
        # protoc -I=hello this that

    Returns
    -------
    list[`Error`]
        The errors that were encountered when invoking protoc.
    """

    return [
        Error(error)
        for error in _run(
            *[str(arg) for arg in args],
            **{str(k): str(v) for k, v in kwargs}
        )
    ]
