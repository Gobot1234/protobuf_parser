from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from ._parser import Error as _Error
from ._parser import parse as _parse
# from ._parser import run as _run
from ._types import *
from ._version import __version__


__all__ = (
    "Error",
    "SyntaxError",
    "Warning",
    "parse",
    "run",
)


class Error(Exception):
    # @overload
    # def __new__(cls, c_error: _Error) -> Error:
    #     ...
    #
    # @overload
    # def __new__(cls, c_error: _SyntaxError) -> SyntaxError:
    #     ...
    #
    # @overload
    # def __new__(cls, c_error: _Warning) -> Warning:
    #     ...
    #
    # def __new__(cls, c_error: _Error) -> Error:
    #     print(c_error.message)
    #     return super().__new__(
    #         {
    #             _Error: Error,
    #             _SyntaxError: SyntaxError,
    #             _Warning: Warning,
    #         }[c_error]
    #     )

    def __init__(self, c_error: _Error) -> None:
        self.file = Path(c_error.filename)
        self.line = c_error.line
        self.column = c_error.column
        self.message = c_error.message
        super().__init__(c_error.message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.file}:{self.line}:{self.column}: {self.message!r}>"


class SyntaxError(Error):
    ...


class Warning(Error, Warning):
    ...


def parse(*files: AnyPath | SupportsParse | FileDescriptorLike) -> tuple[list[bytes], Sequence[Error]]:
    """Parse files using protoc.

    Parameters
    ----------
    files
        Something that can be `open`ed or has a name attribute and read method.

    Returns
    -------
    tuple[`bytes`, list[`Error`]]
        A tuple of the FileDescriptor's bytes and any errors that were encountered when parsing.
    """
    files = list(files)
    for idx, file in enumerate(files):
        if not isinstance(file, SupportsParse):
            if isinstance(file, (os.PathLike, str, bytes)):
                files[idx] = open(file, "r", encoding="utf-8")
            elif isinstance(file, FileDescriptorLike):
                files[idx] = open_fileno(file)
            else:
                raise TypeError(f"parse doesn't support passing {file.__class__} as a file argument")

    output, errors = _parse(files)
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
    ```py
    run("this", "that", I="hello")
    # would be equivalent to
    # protoc -I=hello this that
    ```

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
